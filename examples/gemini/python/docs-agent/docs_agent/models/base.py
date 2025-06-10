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


class GenerativeLanguageModel(abc.ABC):
    """Abstract base class for generative language models."""

    @abc.abstractmethod
    def generate_content(self, contents, request_options=None, log_level="NORMAL"):
        """Generates content."""
        pass

    @abc.abstractmethod
    async def generate_content_async(
        self,
        contents: typing.List[typing.Any],
        tools: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None,
    ) -> typing.Any:
        pass

    @abc.abstractmethod
    def ask_content_model_with_context_prompt(
        self,
        context: str,
        question: str,
        prompt: typing.Optional[str] = None,
        log_level: typing.Optional[str] = "NORMAL",
    ):
        pass

    @abc.abstractmethod
    def embed(self, content, task_type="RETRIEVAL_QUERY", title=None):
        """Embeds content."""
        pass

    @abc.abstractmethod
    def ask_about_file(self, prompt: str, file_path: str):
        """
        Use this method for asking a model about a file.

        Args:
            prompt (str): The prompt to use for the model.
            file_path (str): The path to the file.

        Returns:
            str: The response from the model, or raises an exception.
        """
        pass


class AQAModel(abc.ABC):
    """Abstract base class for AQA models."""

    @abc.abstractmethod
    def generate_answer(
        self, question: str, grounding_passages: typing.List[str], answer_style: str
    ) -> typing.Tuple[str, typing.List[typing.Dict[str, typing.Any]]]:
        """Generates an answer given a question and grounding passages.

        Args:
            question: The user's question.
            grounding_passages: A list of strings, each representing a passage.
            answer_style:  The desired answer style (e.g., "VERBOSE").

        Returns:
            A tuple containing:
            - The answer text (string).
            - A list of dictionaries, where each dictionary represents a relevant
              section and contains its metadata and a probability score.
        """
        pass

    @abc.abstractmethod
    def generate_answer_with_corpora(
        self, question: str, corpus_name: str, answer_style: str
    ) -> typing.Tuple[str, typing.List[typing.Dict[str, typing.Any]]]:
        """Generates an answer given a question using a specified corpus.

        Args:
            question: The user's question.
            corpus_name: The name of the corpus to use.
            answer_style: The desired answer style.

        Returns:
            A tuple containing:
            - The answer text (string)
            - A list of dictionaries, where each dictionary contains section data and probability.
        """

    @abc.abstractmethod
    def get_saved_aqa_response_json(self) -> typing.Any:
        """Retrieves and returns any buffered AQA response."""
        pass

    @abc.abstractmethod
    def query_corpus(
            self,
            user_query: str,
            corpus_name: str,
            results_count: int) -> typing.Any:
        """Queries a corpus and returns relevant results."""
        pass

    @abc.abstractmethod
    def retrieve_chunks_from_corpus(
        self, question: str, corpus_name: str
    ) -> typing.Any:
        """Retrieves chunks from a corpus."""
        pass
