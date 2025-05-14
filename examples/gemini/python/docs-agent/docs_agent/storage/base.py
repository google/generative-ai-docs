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

import abc
import typing


class RAG(abc.ABC):
    """Abstract base class for Retrieval-Augmented Generation."""

    @abc.abstractmethod
    def query_vector_store_to_build(
        self,
        question: str,
        token_limit: float = 200000,
        results_num: int = 10,
        max_sources: int = 4,
        collection_name: typing.Optional[str] = None,
        docs_agent_config: typing.Optional[str] = "normal",
    ) -> tuple[list[typing.Any], str]:
        """
        Queries the vector store and builds context. Must be implemented
        by subclasses.

        Args:
            docs_agent_config: The configuration string ('experimental' or other).
            question (str): The user's question.
            token_limit (float, optional): The total token limit for the context.
            results_num (int, optional): The initial number of results to retrieve.
            max_sources (int, optional): The maximum number of sources to use.

        Returns:
            tuple: A tuple containing a list of SectionDistance-like objects
                   and the final context string.
        """
        pass

    @abc.abstractmethod
    def get_collection(self, name, embedding_function=None, embedding_model=None):
        """
        Gets the collection from the vector store.  Must be implemented
        by subclasses.
        """
        pass

    @abc.abstractmethod
    def backup(self):
        """
        Backs up the vector store.
        """
        pass

    @abc.abstractmethod
    def embedding_function(
            self,
            api_key,
            embedding_model,
            task_type: str = "RETRIEVAL_QUERY"):
        """
        Gets the embedding function.
        """
        pass