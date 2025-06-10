#
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Chroma wrapper"""

from enum import auto, Enum
import string
import shutil
import typing

from absl import logging
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.api.types import Images
from chromadb.api.types import QueryResult
from docs_agent.storage.base import RAG
from docs_agent.models.llm import GenerativeLanguageModelFactory
from docs_agent.utilities.config import Models, ProductConfig, DbConfig
from docs_agent.utilities.helpers import resolve_path

from docs_agent.preprocess.splitters.markdown_splitter import Section as Section
from docs_agent.postprocess.docs_retriever import FullPage as FullPage
from docs_agent.postprocess.docs_retriever import (
    query_vector_store_to_build as retriever_query_vector_store_to_build,
    SectionDistance,
)
from docs_agent.utilities import helpers


# Embeddable types for Chroma - from chroma docs
Embeddable = typing.Union[Documents, Images]


class Error(Exception):
    """Base error class for chroma"""


class ChromaEmbeddingModelNotSupportedError(Error, RuntimeError):
    """Raised if the embedding model specified by a collection is not supported."""


class Format(Enum):
    CONTEXT = auto()
    URL = auto()
    CLICKABLE_URL = auto()


class ChromaQueryResultItem:
    """Chroma query result item wrapper

    Chroma query result has the following type:
    ```
    class QueryResult(TypedDict):
        ids: List[IDs]
        embeddings: Optional[List[List[Embedding]]]
        documents: Optional[List[List[Document]]]
        metadatas: Optional[List[List[Metadata]]]
        distances: Optional[List[List[float]]]
    ```
    Since the Chroma's query support multiple texts as input, the outer list
    corresponds to each of the input text. The inner list corresponds to
    the nearest k documents for a specific input text. Since we always only
    provide one input text to the query call, our access pattern to the
    query result will look like `query_result["documents"][0][i]`, where index
    0 stands for the result for the first (and the only) input text, and index
    i stands for the i-th nearest document.
    """

    templates_with_ref_index = {
        Format.CONTEXT: "$document **[${ref_index}]**",
        Format.URL: "**[${ref_index}]** $url ($distance)",
        Format.CLICKABLE_URL: '**[${ref_index}]** <a href="$url">$url</a> ($distance)',
    }

    templates_without_ref_index = {
        Format.CONTEXT: "$document",
        Format.URL: "$url",
        Format.CLICKABLE_URL: '<a href="$url">$url</a>',
    }

    def __init__(self, result: QueryResult, index: int) -> None:
        self.document = result["documents"][0][index]
        self.metadata = result["metadatas"][0][index]
        self.distance = result["distances"][0][index]

    def format(self, format_type: Format, ref_index: typing.Optional[int] = None):
        d = {
            "document": self.document.strip(),
            "ref_index": ref_index,
            "url": self.metadata.get("url", None),
            "distance": self.distance,
        }
        if ref_index is None:
            template = self.templates_without_ref_index[format_type]
        else:
            template = self.templates_with_ref_index[format_type]

        return string.Template(template).substitute(d)


class ChromaQueryResult:
    """Chroma query result wrapper"""

    def __init__(self, result: QueryResult) -> None:
        self.result = result

    def __len__(self):
        return len(self.result["documents"][0])

    def fetch(self, distance_threshold=float("inf")):
        for i in range(len(self)):
            item = ChromaQueryResultItem(self.result, i)
            if item.distance < distance_threshold:
                yield item

    def fetch_formatted(self, format_type: Format, distance_threshold=float("inf")):
        return "\n\n".join(
            item.format(format_type, i + 1)
            for i, item in enumerate(self.fetch(distance_threshold=distance_threshold))
        )

    def fetch_nearest(self):
        return ChromaQueryResultItem(self.result, 0)

    def fetch_nearest_formatted(self, format_type: Format):
        return self.fetch_nearest().format(format_type)

    def fetch_at(self, index):
        return ChromaQueryResultItem(self.result, index)

    def fetch_at_formatted(self, index, format_type: Format):
        return self.fetch_at(index).format(format_type)


class ChromaCollection:
    """Chroma collection wrapper"""

    def __init__(self, collection, embedding_function) -> None:
        self.collection = collection
        self.embedding_function = embedding_function

    def query(self, text: str, top_k: int = 1):
        return ChromaQueryResult(
            self.collection.query(query_texts=[text], n_results=top_k)
        )

    def embed(self, text: str):
        return self.embedding_function(text)


# New classes to work with Chromadb
class SectionDB(Enum):
    SECTION_ID = auto()
    SECTION_NAME_ID = auto()
    SECTION_LEVEL = auto()
    SECTION_TITLE = auto()
    PREVIOUS_ID = auto()
    CONTENT = auto()
    DISTANCE = auto()
    REF_INDEX = auto()
    URL = auto()
    TOKEN_ESTIMATE = auto()
    PARENT_TREE = auto()

    def decodeSection(self):
        if self.SECTION_ID:
            section_id = self.SECTION_ID.value
        else:
            section_id = ""
        if self.SECTION_NAME_ID:
            section_name_id = self.SECTION_NAME_ID.value
        else:
            section_name_id = ""
        if self.SECTION_TITLE:
            section_title = self.SECTION_TITLE.value
        else:
            section_title = ""
        if self.SECTION_LEVEL:
            section_level = self.SECTION_LEVEL.value
        else:
            section_level = ""
        if self.PREVIOUS_ID:
            previous_id = self.PREVIOUS_ID.value
        else:
            previous_id = ""
        if self.PARENT_TREE:
            parent_tree = self.PARENT_TREE.value
            parent_tree_str = str(parent_tree).strip("[]").split(",")
            parent_tree = []
            for num in parent_tree_str:
                parent_tree.append(int(num))
        else:
            parent_tree = ""
        if self.TOKEN_ESTIMATE:
            token_estimate = self.TOKEN_ESTIMATE.value
        else:
            token_estimate = ""
        if self.CONTENT:
            content = self.CONTENT
        else:
            content = ""
        section = Section(
            id=int(section_id),
            name_id=str(section_name_id),
            section_title=str(section_title),
            page_title="",
            level=int(section_level),
            previous_id=int(previous_id),
            parent_tree=parent_tree,
            token_count=float(token_estimate),
            content=str(content),
        )
        return section


class ChromaDBGet:
    """Chroma query result item wrapper

    Chroma query result has the following type:
    ```
    """

    def __init__(self, result) -> None:
        self.document = result["documents"]
        self.metadata = result["metadatas"]
        self.id = result["ids"]

    # Measure how many responses were returned
    def __len__(self):
        return len(self.id)

    # def get_section_id(self, index: int = 0):
    #     return self.id[index]


class ChromaSectionDBItem:
    """Chroma query result item wrapper for SectionDB objects

    Chroma query result has the following type:
    ```
    """

    templates_base = {
        SectionDB.SECTION_ID: "$section_id",
        SectionDB.SECTION_NAME_ID: "$name_id",
        SectionDB.SECTION_LEVEL: "$section_level",
        SectionDB.SECTION_TITLE: "$section_title",
        SectionDB.PREVIOUS_ID: "$previous_id",
        SectionDB.TOKEN_ESTIMATE: "$token_estimate",
        SectionDB.CONTENT: "$content",
        SectionDB.DISTANCE: "$distance",
        SectionDB.URL: "$url",
        SectionDB.PARENT_TREE: "$parent_tree",
        SectionDB.REF_INDEX: "${ref_index}",
    }

    def __init__(self, result: QueryResult, index: int) -> None:
        self.document = result["documents"][0][index]
        self.metadata = result["metadatas"][0][index]
        self.distance = result["distances"][0][index]
        self.id = result["ids"][0][index]

    def __str__(self):
        return f"This is a section with the following properties:\n\
Section ID: {SectionDB.SECTION_ID}\n\
Section Title: {SectionDB.SECTION_TITLE}\n\
Section URL: {SectionDB.URL}\n"

    def format(self, format_type: SectionDB, ref_index: typing.Optional[int] = None):
        d = {
            "content": self.document.strip(),
            "ref_index": ref_index,
            "section_id": self.metadata.get("section_id", None),
            "section_title": self.metadata.get("section_title", None),
            "section_level": self.metadata.get("section_level", None),
            "section_name_id": self.metadata.get("section_name_id", None),
            "tree": self.metadata.get("tree", None),
            "previous_id": self.metadata.get("previous_id", None),
            "token_estimate": self.metadata.get("token_estimate", None),
            "parent_tree": self.metadata.get("tree", None),
            "url": self.metadata.get("url", None),
            "distance": self.distance,
        }

        template = self.templates_base[format_type]
        result = string.Template(template).substitute(d)
        return result


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Embedding function wrapper for Gemini models"""

    def __init__(self, models_config: Models, task_type: str = "RETRIEVAL_DOCUMENT"):
        self.models_config = models_config
        self.task_type = task_type
        # Create the embedding model instance
        self.model = GenerativeLanguageModelFactory.create_model(
            model_type=self.models_config.embedding_model,
            models_config=self.models_config,
        )

    def __call__(self, input: Embeddable) -> Embeddings:
        # Handles list of strings
        if isinstance(input, list) and all(isinstance(i, str) for i in input):
            embeddings_list = self.model.embed(content=input, task_type=self.task_type)
        # Commented out for now. Can use images here.
        # elif isinstance(input, list) and all(isinstance(i, np.ndarray) for i in input):
        #    embeddings_list = model.embed_images(images=input, task_type=self.task_type) # Example
        else:
            logging.error(
                f"Unsupported input type for embedding function: {type(input)}"
            )
            # In case there is a single string, which is the most common case
            if isinstance(input, str):
                embeddings_list = self.model.embed(
                    content=[input], task_type=self.task_type
                )
            else:
                # Update this if images get enabled
                raise TypeError("Input must be Documents (List[str])")

        return typing.cast(Embeddings, embeddings_list)


class ChromaEnhanced(RAG):
    """Chroma wrapper"""

    def __init__(self, chroma_dir: str, models_config: Models) -> None:
        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.models_config = models_config
        self.chroma_dir = chroma_dir
        self._collection_name: typing.Optional[str] = None
        # Start the embedding function
        self.embedding_function_instance = GeminiEmbeddingFunction(
            models_config=self.models_config, task_type="RETRIEVAL_DOCUMENT"
        )
        logging.info(f"ChromaEnhanced instance initialized for path: {chroma_dir}")

    @staticmethod
    def from_product_config(product_config: ProductConfig) -> "ChromaEnhanced":
        """Creates a ChromaEnhanced instance from a ProductConfig."""
        chroma_db_conf: DbConfig | None = None
        for db_conf in product_config.db_configs:
            if db_conf.db_type == "chroma":
                chroma_db_conf = db_conf
                break
        if not chroma_db_conf:
            logging.error("Chroma configuration not found in product config.")
            raise ValueError("Chroma configuration not found in product config.")

        if not chroma_db_conf.vector_db_dir:
            logging.error("Chroma vector_db_dir is missing in the configuration.")
            raise ValueError("Chroma vector_db_dir is missing in the configuration.")

        logging.info(
            f"[ChromaEnhanced] Relative chroma path from configuration: '{chroma_db_conf.vector_db_dir}'"
        )
        try:
            resolved_chroma_dir = resolve_path(chroma_db_conf.vector_db_dir)
            logging.info(
                f"[ChromaEnhanced] Resolved absolute chroma path: '{resolved_chroma_dir}'"
            )
        except Exception as e:
            logging.error(f"[ChromaEnhanced] Error resolving chroma path: {e}")
            raise

        # Create the ChromaEnhanced instance
        try:
            chroma_instance = ChromaEnhanced(
                chroma_dir=resolved_chroma_dir, models_config=product_config.models
            )
            logging.info(
                f"ChromaEnhanced successfully created for path: {resolved_chroma_dir}"
            )
            return chroma_instance
        except Exception as e:
            logging.error(f"Error creating ChromaEnhanced instance: {e}")
            raise

    # Returns the instance of the embedding function
    def embedding_function(self, *args, **kwargs) -> GeminiEmbeddingFunction:
        """Returns the embedding function instance configured for the Chroma wrapper."""
        return self.embedding_function_instance

    def list_collections(self):
        return self.client.list_collections()

    def backup(self, output_dir: typing.Optional[str] = None):
        """Backs up the chroma database to the specified output directory.

        Args:
            output_dir (str, optional): The directory to backup to. If None, a
                backup directory will be created that is parralel to the
                self.chroma_dir.

        Returns:
            str: The path to the backup directory, or None if the backup failed.
        """
        if output_dir == None:
            try:
                output_dir = helpers.parallel_backup_dir(self.chroma_dir)
            except:
                logging.exception(
                    "Failed to create backup directory for: %s", self.chroma_dir
                )
                return None
        else:
            try:
                pure_path = helpers.return_pure_dir(self.chroma_dir)
                output_dir = (
                    helpers.end_path_backslash(
                        helpers.start_path_no_backslash(output_dir)
                    )
                    + pure_path
                )
            except:
                logging.exception(
                    "Failed to resolve output directory for: %s", output_dir
                )
                return None
        try:
            if output_dir == None:
                output_dir = helpers.parallel_backup_dir(self.chroma_dir)
            shutil.copytree(self.chroma_dir, output_dir, dirs_exist_ok=True)
            logging.info("Backed up from: %s to %s", self.chroma_dir, output_dir)
            return output_dir
        except:
            logging.exception(
                "Failed to backup from: %s to %s", self.chroma_dir, output_dir
            )
            return None

    # def getSameOriginUUID(self):
    #     return self.client.get()

    def get_collection(self, name, embedding_function=None):
        # Can override the embedding function
        ef_to_use = (
            embedding_function
            if embedding_function
            else self.embedding_function_instance
        )
        try:
            collection = self.client.get_collection(name=name)
            if self._collection_name is None:
                self._collection_name = name
        except Exception as e:
            logging.error(f"Failed to get collection '{name}': {e}")
            raise
        return ChromaCollectionEnhanced(collection, ef_to_use)

    def query_vector_store_to_build(
        self,
        question: str,
        token_limit: float = 200000,
        results_num: int = 10,
        max_sources: int = 4,
        collection_name: typing.Optional[str] = None,
        docs_agent_config: typing.Optional[str] = "normal",
    ) -> tuple[list[SectionDistance], str]:
        """
        Queries the vector database collection and builds a context string.
        Calls the retriever function.

        Args:
            question (str): The user's question.
            token_limit (float, optional): The total token limit for the context. Defaults to 200000.
            results_num (int, optional): The initial number of results to retrieve. Defaults to 10.
            max_sources (int, optional): The maximum number of sources to use. Defaults to 4.
            collection_name (str, optional): The name of the collection to query.
                                            If None, uses the collection name stored
                                            during the first get_collection call.
            docs_agent_config (str, optional): The docs agent configuration string. "experimental" or "normal". Defaults to "normal".

        Returns:
            tuple: A tuple containing a list of SectionDistance objects and the final context string.
        """
        target_collection_name = collection_name or self._collection_name
        if not target_collection_name:
            logging.error("Collection name not provided and not previously set.")
            raise ValueError(
                "Must provide collection_name or call get_collection first."
            )

        target_docs_agent_config = docs_agent_config
        try:
            collection_obj = self.get_collection(name=target_collection_name)
        except Exception as e:
            logging.error(f"Failed to get collection '{target_collection_name}': {e}")
            raise

        # Call the function from docs_retriever
        return retriever_query_vector_store_to_build(
            collection=collection_obj,
            docs_agent_config=target_docs_agent_config,
            question=question,
            token_limit=token_limit,
            results_num=results_num,
            max_sources=max_sources,
        )


class ChromaCollectionEnhanced:
    """Chroma collection wrapper"""

    def __init__(self, collection, embedding_function_instance) -> None:
        self.collection = collection
        # Store the embedding function instance
        self.embedding_function = embedding_function_instance
        # Retrieve the models config from the embedding function instance
        if hasattr(embedding_function_instance, "models_config"):
            self._models_config = embedding_function_instance.models_config
        else:
            self._models_config = None
            logging.warning(
                "ChromaCollectionEnhanced could not access models_config from the embedding function."
            )

    def query(self, text: str, top_k: int = 1, where: dict = None):
        """Queries the ChromaDB collection using appropriate query embeddings."""
        if self._models_config:
            query_ef = GeminiEmbeddingFunction(
                models_config=self._models_config, task_type="RETRIEVAL_QUERY"
            )
            # Query the collection using the query embeddings
            query_embeddings = query_ef([text])
            query_args = {"query_embeddings": query_embeddings, "n_results": top_k}
            if where is not None:
                query_args["where"] = where
            result = self.collection.query(**query_args)
        else:
            logging.warning(
                "Cannot create query-specific embedding function. Falling back to using collection's default embedding function for query."
            )
            query_args = {"query_texts": [text], "n_results": top_k}
            if where is not None:
                query_args["where"] = where
            result = self.collection.query(**query_args)
        return ChromaQueryResultEnhanced(result)

    # Return a FullPage (list of Section) that match an origin_uuid
    def getPageOriginUUIDList(self, origin_uuid):
        get_obj = ChromaDBGet(
            self.collection.get(
                include=["metadatas", "documents"],
                where={"origin_uuid": {"$eq": origin_uuid}},
            )
        )
        page = []
        # added_id = []
        for i in range(len(get_obj.id)):
            # Makes sure that each ID is only added once
            # if get_obj.id not in added_id:
            section = Section(
                id=get_obj.metadata[i].get("section_id", None),
                name_id=get_obj.metadata[i].get("name_id", None),
                page_title=get_obj.metadata[i].get("page_title", None),
                section_title=get_obj.metadata[i].get("section_title", None),
                level=get_obj.metadata[i].get("level", None),
                previous_id=get_obj.metadata[i].get("previous_id", None),
                parent_tree=get_obj.metadata[i].get("parent_tree", None),
                token_count=get_obj.metadata[i].get("token_estimate", None),
                url=get_obj.metadata[i].get("url", None),
                uuid=get_obj.id[i],
                content=get_obj.document[i],
            )
            page.append(section)
        full_page = FullPage(page)
        return full_page

    def getPageSection(self, section_title):
        return self.collection.get(
            include=["metadatas"], where={"section_title": {"$eq": section_title}}
        )

    def embed(self, text: str):
        return self.embedding_function(text)


class ChromaQueryResultEnhanced:
    """Chroma query result wrapper"""

    def __init__(self, result: QueryResult) -> None:
        self.result = result

    def __len__(self):
        if self.result["documents"] and self.result["documents"][0]:
            return len(self.result["documents"][0])
        return 0

    # Get without considering distance
    def clean_get(self):
        for i in range(len(self)):
            item = ChromaSectionDBItem(self.result, i)
            yield item

    def fetch(self, distance_threshold=float("inf")):
        for i in range(len(self)):
            item = ChromaSectionDBItem(self.result, i)
            if item.distance < distance_threshold:
                yield item

    def fetch_formatted(self, format_type: SectionDB, distance_threshold=float("inf")):
        return "\n\n".join(
            item.format(format_type, i + 1)
            for i, item in enumerate(self.fetch(distance_threshold=distance_threshold))
        )

    def fetch_section_list_format(
        self, format_type: SectionDB, distance_threshold=float("inf")
    ):
        results = enumerate(self.fetch(distance_threshold=distance_threshold))
        contents = []
        for i, item in results:
            content_item = item.format(format_type, i + 1)
            contents.append(content_item)
        return contents

    def returnSectionObj(self, format_type: SectionDB, distance_threshold=float("inf")):
        results = self.fetch(distance_threshold=distance_threshold)
        contents = []
        # Don't need ids here as we will retrieve those with a get
        i = 0
        for item in results:
            # id = item.id
            content_item = item.format(format_type, i)
            # section = item.decodeSection()
            contents.append(content_item)
            # ids.append(id)
            i += 1
        return contents

    # This function returns a list of ChromaSectionDBItem that match results up to
    # limit specific in query. You can then access from each list item with
    # .document, .id, etc...
    def returnDBObjList(self, distance_threshold=float("inf")):
        contents = []
        # Check if results exist before iterating
        if self.result and self.result.get("documents") and self.result["documents"][0]:
            results = self.fetch(distance_threshold=distance_threshold)
            for item in results:
                contents.append(item)
        else:
            logging.warning(
                "No documents found in Chroma query result for returnDBObjList."
            )
        return contents

    # This function returns a list of ChromaSectionDBItem that match results up to
    # limit specific in query. You can then access from each list item with
    # .document, .id, etc...
    def returnDBObjListGet(self):
        results = self.clean_get()
        contents = []
        # for item in results:
        #     content_item = item
        #     contents.append(content_item)
        return results

    def fetch_nearest(self):
        # Add check for empty results
        if len(self) > 0:
            return ChromaSectionDBItem(self.result, 0)
        else:
            logging.warning(
                "Attempted to fetch nearest from empty Chroma query result."
            )
            return None  # Or raise an error

    def fetch_nearest_formatted(self, format_type: SectionDB):
        nearest = self.fetch_nearest()
        if nearest:
            return nearest.format(format_type)
        return ""  # Return empty string if no nearest item

    # def return_response(self):
    #     return ChromaSectionDBItem.returnSection(self)
