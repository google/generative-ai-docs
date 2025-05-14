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

import typing
from absl import logging
from docs_agent.models.base import AQAModel
import google.ai.generativelanguage as glm


class AQA(AQAModel):
    """
    An implementation of AQAModel using Google's Generative AI API.
    """

    def __init__(self):
        self.generative_service_client = glm.GenerativeServiceClient()
        self.retriever_service_client = glm.RetrieverServiceClient()
        self.permission_service_client = glm.PermissionServiceClient()
        self.aqa_response_buffer: typing.Any = None

    def generate_answer(
        self,
        question: str,
        grounding_passages_texts: typing.List[str],
        answer_style: str,
    ) -> typing.Tuple[str, typing.List[typing.Dict[str, typing.Any]]]:
        """
        Generates an answer to a question using the provided grounding passages.

        Args:
            question (str): The question to answer.
            grounding_passages_texts (typing.List[str]): A list of texts to use as grounding passages.
            answer_style (str): The style of the answer (e.g., "ABSTRACTIVE", "EXTRACTIVE").

        Returns:
            typing.Tuple[str, typing.List[typing.Dict[str, typing.Any]]]: A tuple containing the answer and a list of citations.
        """
        user_query_content = glm.Content(parts=[glm.Part(text=question)])

        grounding_passages = glm.GroundingPassages()
        for i, passage_text in enumerate(grounding_passages_texts):
            new_passage = glm.Content(parts=[glm.Part(text=passage_text)])
            index_id = str("{:03d}".format(i + 1))
            grounding_passages.passages.append(
                glm.GroundingPassage(content=new_passage, id=index_id)
            )

        req = glm.GenerateAnswerRequest(
            model="models/aqa",
            contents=[user_query_content],
            inline_passages=grounding_passages,
            answer_style=answer_style,
        )

        try:
            aqa_response = self.generative_service_client.generate_answer(req)
            self.aqa_response_buffer = aqa_response

            # Create the structured result
            result_list: typing.List[typing.Dict[str, typing.Any]] = []
            try:
                answer_text = aqa_response.answer.content.parts[0].text
            except (AttributeError, IndexError):
                answer_text = ""

            if answer_text:
                for i in range(len(grounding_passages_texts)):
                    result_list.append(
                        {
                            "text": grounding_passages_texts[i],
                            "probability": aqa_response.answerable_probability,
                            "metadata": {},
                        }
                    )
            return answer_text, result_list

        except Exception as e:
            logging.error(f"Error generating answer: {e}")
            self.aqa_response_buffer = None
            return "", []

    def generate_answer_with_corpora(
        self, question: str, corpus_name: str, answer_style: str
    ) -> typing.Tuple[str, typing.List[typing.Dict[str, typing.Any]]]:
        """
        Generates an answer to a question using the provided corpus.

        Args:
            question (str): The question to answer.
            corpus_name (str): The name of the corpus to use.
            answer_style (str): The style of the answer (e.g., "ABSTRACTIVE", "EXTRACTIVE").

        Returns:
            typing.Tuple[str, typing.List[typing.Dict[str, typing.Any]]]: A tuple containing the answer and a list of citations.
        """

        user_question_content = glm.Content(
            parts=[glm.Part(text=question)], role="user"
        )
        retriever_config = glm.SemanticRetrieverConfig(
            source=corpus_name, query=user_question_content
        )
        req = glm.GenerateAnswerRequest(
            model="models/aqa",
            contents=[user_question_content],
            semantic_retriever=retriever_config,
            answer_style=answer_style,
        )

        try:
            aqa_response = self.generative_service_client.generate_answer(req)
            self.aqa_response_buffer = aqa_response

            result_list: typing.List[typing.Dict[str, typing.Any]] = []
            try:
                answer_text = aqa_response.answer.content.parts[0].text
            except (AttributeError, IndexError):
                answer_text = ""

            if answer_text:
                for item in aqa_response.answer.grounding_attributions:
                    metadata = self._get_aqa_response_metadata(item)
                    for part in item.content.parts:
                        metadata["content"] = part.text
                    result_list.append(
                        {
                            "metadata": metadata,
                            "probability": aqa_response.answerable_probability,
                        }
                    )

            return answer_text, result_list

        except Exception as e:
            logging.error(f"Error in generate_answer_with_corpora: {e}")
            self.aqa_response_buffer = None
            return "", []

    def get_saved_aqa_response_json(self) -> typing.Any:
        """
        Returns the raw AQA response from the last call to generate_answer or generate_answer_with_corpora.

        Returns:
            typing.Any: The raw AQA response, or None if no response has been saved.
        """
        return self.aqa_response_buffer

    def query_corpus(self, user_query: str, corpus_name: str, results_count: int) -> typing.Any:
        """
        Queries a corpus for relevant information.

        Args:
            user_query (str): The user's query.
            corpus_name (str): The name of the corpus to query.
            results_count (int): The number of results to return.

        Returns:
            typing.Any: The response from the query.
        """
        request = glm.QueryCorpusRequest(
            name=corpus_name, query=user_query, results_count=results_count
        )
        return self.retriever_service_client.query_corpus(request)

    def _get_aqa_response_metadata(
        self, aqa_response_item: typing.Any
    ) -> typing.Dict[str, typing.Any]:
        """
        Retrieves metadata from an AQA response item.

        Args:
            aqa_response_item (typing.Any): An item from the AQA response.

        Returns:
            typing.Dict[str, typing.Any]: A dictionary containing the metadata.
        """
        try:
            chunk_resource_name = (
                aqa_response_item.source_id.semantic_retriever_chunk.chunk
            )
            get_chunk_response = self.retriever_service_client.get_chunk(
                name=chunk_resource_name
            )
            metadata = get_chunk_response.custom_metadata
            final_metadata = {}
            for m in metadata:
                if m.string_value:
                    value = m.string_value
                elif m.numeric_value:
                    value = m.numeric_value
                else:
                    value = ""
                final_metadata[m.key] = value
            return final_metadata
        except Exception:
            return {}

    # Retrieve and return chunks that are most relevant to the input question
    def retrieve_chunks_from_corpus(self, question: str, corpus_name: str):
        results_count = 5
        return self.query_corpus(
            corpus_name=corpus_name,
            user_query=question,
            results_count=results_count
        )
