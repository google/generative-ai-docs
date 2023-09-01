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

from absl import logging
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.api.models import Collection
from chromadb.api.types import QueryResult

from palm import PaLM


class Error(Exception):
    """Base error class for chroma"""


class ChromaEmbeddingModelNotSupportedError(Error, RuntimeError):
    """Raised if the embedding model specified by a collection is not supported."""


class Chroma:
    """Chroma wrapper"""

    def __init__(self, chroma_dir) -> None:
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=chroma_dir,
            )
        )

    def list_collections(self):
        return self.client.list_collections()

    def get_collection(self, name, embedding_function=None):
        if embedding_function is not None:
            return ChromaCollection(
                self.client.get_collection(name, embedding_function=embedding_function),
                embedding_function,
            )
        # Read embedding meta information from the collection
        collection = self.client.get_collection(name, lambda x: None)
        embedding_model = None
        if collection.metadata:
            embedding_model = collection.metadata.get("embedding_model", None)

        if embedding_model == "local/all-mpnet-base-v2":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            local_model_dir = os.path.join(base_dir, "models/all-mpnet-base-v2")
            embedding_function = (
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=local_model_dir
                )
            )
        elif embedding_model is None or embedding_model == "palm/embedding-gecko-001":
            if embedding_model is None:
                logging.warning(
                    "Embedding model is not stored in the metadata of "
                    "the collection %s. Using PaLM as default.",
                    name,
                )
            palm = PaLM(embed_model="models/embedding-gecko-001", find_models=False)
            # We can not redefine embedding_function with def and
            # have to assign a lambda to it
            # pylint: disable-next=unnecessary-lambda-assignment
            embedding_function = lambda texts: [palm.embed(text) for text in texts]

        else:
            raise ChromaEmbeddingModelNotSupportedError(
                f"Embedding model {embedding_model} specified by collection {name} "
                "is not supported."
            )

        return ChromaCollection(
            self.client.get_collection(name, embedding_function=embedding_function),
            embedding_function,
        )


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

    def format(self, format_type: Format, ref_index: int = None):
        d = {
            "document": self.document,
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


class ChromaCollection:
    """Chroma collection wrapper"""

    def __init__(self, collection: Collection, embedding_function) -> None:
        self.collection = collection
        self.embedding_function = embedding_function

    def query(self, text: str, top_k: int = 1):
        return ChromaQueryResult(
            self.collection.query(query_texts=[text], n_results=top_k)
        )

    def embed(self, text: str):
        return self.embedding_function(text)
