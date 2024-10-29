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
import os
import string
import shutil
import typing

from absl import logging
import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.models import Collection
from chromadb.api.types import QueryResult

from docs_agent.preprocess.splitters.markdown_splitter import Section as Section
from docs_agent.postprocess.docs_retriever import FullPage as FullPage
from docs_agent.utilities.helpers import resolve_path, parallel_backup_dir


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


class ChromaEnhanced:
    """Chroma wrapper"""

    def __init__(self, chroma_dir) -> None:
        self.client = chromadb.PersistentClient(path=chroma_dir)

    def list_collections(self):
        return self.client.list_collections()

    # Returns output_dir if backup was successful, None if it failed
    # Output dir can only be a child to chroma_dir
    def backup_chroma(self, chroma_dir: str, output_dir: typing.Optional[str] = None):
        try:
            chroma_dir = resolve_path(chroma_dir)
            if output_dir == None:
                output_dir = parallel_backup_dir(chroma_dir)
            shutil.copytree(chroma_dir, output_dir, dirs_exist_ok=True)
            logging.info(f"Backed up from: {chroma_dir} to {output_dir}")
            return output_dir
        except:
            return None

    # def getSameOriginUUID(self):
    #     return self.client.get()

    def get_collection(self, name, embedding_function=None, embedding_model=None):
        if embedding_function is not None:
            return ChromaCollectionEnhanced(
                self.client.get_collection(
                    name=name, embedding_function=embedding_function
                ),
                embedding_function,
            )
        # Read embedding meta information from the collection
        collection = self.client.get_collection(name=name)
        if embedding_model is None and collection.metadata:
            embedding_model = collection.metadata.get("embedding_model", None)
            if embedding_model is None:
                # If embedding_model is not found in the metadata,
                # use `models/embedding-001` by default.
                logging.info(
                    "Embedding model is not specified in the metadata of "
                    "the collection %s. Using the default embedding model: models/embedding-001",
                    name,
                )
                embedding_model = "models/embedding-001"
        if embedding_model == "local/all-mpnet-base-v2":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            local_model_dir = os.path.join(base_dir, "models/all-mpnet-base-v2")
            embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=local_model_dir
                )
            )
        else:
            raise ChromaEmbeddingModelNotSupportedError(
                f"Embedding model {embedding_model} specified by collection {name} "
                "is not supported."
            )

        return ChromaCollectionEnhanced(
            self.client.get_collection(
                name=name, embedding_function=embedding_function
            ),
            embedding_function,
        )


class ChromaCollectionEnhanced:
    """Chroma collection wrapper"""

    def __init__(self, collection, embedding_function) -> None:
        self.collection = collection
        self.embedding_function = embedding_function

    def query(self, text: str, top_k: int = 1):
        dict = {}
        # dict.update({"token_estimate": {"$gt": 100}})
        return ChromaQueryResultEnhanced(
            self.collection.query(query_texts=[text], n_results=top_k, where=dict)
        )

        # same_page = self.collection.get(include=["documents","metadatas"],
        #                             where={"origin_uuid": {"$eq": origin_uuid[i]}},)

    # # Return all entries that match an origin_uuid
    # def getPageOriginUUID(self, origin_uuid):
    #     return ChromaDBGet(
    #         self.collection.get(
    #             include=["metadatas", "documents"],
    #             where={"origin_uuid": {"$eq": origin_uuid}},
    #         )
    #     )

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
        return len(self.result["documents"][0])

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
        results = self.fetch(distance_threshold=distance_threshold)
        contents = []
        for item in results:
            contents.append(item)
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
        return ChromaSectionDBItem(self.result, 0)

    def fetch_nearest_formatted(self, format_type: SectionDB):
        return self.fetch_nearest().format(format_type)

    # def return_response(self):
    #     return ChromaSectionDBItem.returnSection(self)
