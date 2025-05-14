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

"""Docs Agent"""

import typing
from typing import List, Optional
from absl import logging
import google.api_core

from docs_agent.utilities.config import ProductConfig, Models
from docs_agent.preprocess.splitters import markdown_splitter

from docs_agent.postprocess.docs_retriever import (
    SectionProbability as SectionProbability,
    query_vector_store_to_build,
)
from docs_agent.models.base import GenerativeLanguageModel
from docs_agent.models.llm import GenerativeLanguageModelFactory
from docs_agent.storage.rag import RAGFactory, return_collection_name
from docs_agent.storage.base import RAG

from docs_agent.models.base import AQAModel
from docs_agent.models.aqa import AQAModelFactory

from docs_agent.models.tools.tool_manager import ToolManager


class DocsAgent:
    """DocsAgent class"""

    # Temporary parameter of init_chroma
    def __init__(
        self,
        config: ProductConfig,
        init_chroma: bool = True,
        init_semantic: bool = True,
    ):
        # Models settings
        self.config = config
        self.language_model_name = str(self.config.models.language_model)
        self.embedding_model_name = str(self.config.models.embedding_model)
        self.api_endpoint = str(self.config.models.api_endpoint)
        self.tool_manager: Optional[ToolManager] = None
        if self.config.mcp_servers:
            try:
                self.tool_manager = ToolManager(config=self.config)
                if self.tool_manager.tool_services:
                    logging.info(
                        f"ToolManager initialized successfully with {len(self.tool_manager.tool_services)} tool service instance(s)."
                    )
                else:
                    logging.warning(
                        "ToolManager initialized, but failed to set up any tool services."
                    )
            except Exception as e:
                logging.error(f"Failed to instantiate ToolManager: {e}")
                self.tool_manager = None
        else:
            logging.info("ToolManager not initialized: No MCP servers configured.")
        self.language_model: GenerativeLanguageModel = (
            GenerativeLanguageModelFactory.create_model(
                self.language_model_name,
                models_config=config.models,
                conditions=config.conditions,
            )
        )
        self.context_model = self.language_model_name
        if self.tool_manager and not hasattr(
            self.language_model, "generate_content_async"
        ):
            logging.error(
                f"Configured language model {self.language_model_name} does not support async generation required for tools. Disabling ToolManager."
            )
            self.tool_manager = None
        # Use the new chroma db for all queries
        # Should make a function for this or clean this behavior
        if init_chroma:
            self.rag: RAG = RAGFactory.create_rag(product_config=self.config)
            collection_name = return_collection_name(product_config=self.config)
            logging.info(f"Getting Chroma collection: {collection_name}")
            try:
                # Store the collection object directly on the instance
                self.collection = self.rag.get_collection(collection_name)
                logging.info(f"Successfully retrieved collection '{collection_name}'.")
            except Exception as e:
                logging.error(
                    f"Failed to get Chroma collection '{collection_name}': {e}"
                )
                raise
        else:
            self.rag = None
            self.collection = None

        # AQA model settings
        self.aqa_model = None
        if init_semantic:
            # Except in "full" and "pro" modes, the semantic retriever option
            # requires the AQA model. If not, exit the program.
            if (
                self.config.app_mode not in ("full", "widget-pro")
                and self.config.db_type == "google_semantic_retriever"
                and self.language_model_name != "aqa"
            ):
                logging.error(
                    "The db_type `google_semantic_retriever` option"
                    " requires the AQA model (`aqa`)."
                )
                exit(1)
            # If the AQA model is selected or the web app is on "full" and "pro" modes.
            if self.language_model_name == "aqa" or self.config.app_mode in (
                "full",
                "widget-pro",
            ):
                self.aqa_model: AQAModel = AQAModelFactory.create_model()
                self.context_model = "gemini-pro"
                gemini_model_config = Models(
                    language_model=self.context_model,
                    embedding_model=self.embedding_model_name,
                    api_endpoint=self.api_endpoint,
                )
                self.language_model = GenerativeLanguageModelFactory.create_model(
                    self.context_model,
                    models_config=gemini_model_config,
                    conditions=config.conditions,
                )
            # If semantic retriever is selected as the main database.
            if self.config.db_type == "google_semantic_retriever":
                for item in self.config.db_configs:
                    if "google_semantic_retriever" in item.db_type:
                        self.corpus_name = item.corpus_name
                        self.corpus_display = item.corpus_display or (
                            self.config.product_name + " documentation"
                        )
                self.aqa_response_buffer = ""
        else:
            self.aqa_model = None
        # Always initialize the Gemini 1.5 pro model for other tasks.
        gemini_pro_model_config = Models(
            language_model="gemini-1.5-pro",
            embedding_model=self.embedding_model_name,
            api_endpoint=self.api_endpoint,
        )
        self.gemini_pro = GenerativeLanguageModelFactory.create_model(
            "gemini-1.5-pro",
            models_config=gemini_pro_model_config,
            conditions=config.conditions,
        )

        if self.config.app_mode in ("full", "widget-pro"):
            # Initialize the Gemini 1.5 model for generating main responses.
            gemini_15_model_config = Models(
                language_model=self.language_model_name,
                embedding_model=self.embedding_model_name,
                api_endpoint=self.api_endpoint,
            )
            self.gemini_15 = GenerativeLanguageModelFactory.create_model(
                self.language_model_name,
                models_config=gemini_15_model_config,
                conditions=config.conditions,
            )
        else:
            self.gemini_15 = self.gemini_pro

    # Use this method for talking to a Gemini content model
    def ask_content_model_with_context(self, context, question):
        new_prompt = context + "\n\nQuestion: " + question
        # Print the prompt for debugging if the log level is VERBOSE.
        if self.config.log_level == "VERBOSE":
            self.print_the_prompt(new_prompt)
        try:
            response = self.language_model.generate_content(new_prompt)
        except google.api_core.exceptions.InvalidArgument:
            return self.config.conditions.model_error_message
        # for chunk in response:
        #     if str(chunk.candidates[0].content) == "":
        #         return self.config.conditions.model_error_message
        return response

    # Use this method for talking to Gemini's AQA model using inline passages
    # answer_style can be VERBOSE, ABSTRACTIVE, or EXTRACTIVE
    def ask_aqa_model_using_local_vector_store(
        self,
        question,
        results_num: int = 5,
        answer_style: str = "VERBOSE",
    ):
        """
        Use this method for talking to Gemini's AQA model using inline passages.

        Args:
            question (str): The user's question.
            results_num (int, optional): The number of results to retrieve from the vector store. Defaults to 5.
            answer_style (str, optional): The style of the answer. Can be "VERBOSE", "ABSTRACTIVE", or "EXTRACTIVE". Defaults to "VERBOSE".

        Returns:
            tuple: A tuple containing the answer text and a list of SectionProbability objects.
                   Returns a model error message and an empty list if the model fails.
        """
        verbose_prompt = "Question: " + question + "\n"
        # Retrieves from chroma, using up to 30k tokens
        if not self.rag:
            logging.error("Chroma collection not initialized.")
            return "Chroma collection not initialized.", []
        if not self.aqa_model:
            logging.error(
                "AQA model is not initialized. Cannot generate answer using local vector store."
            )
            return (
                "AQA model is not initialized. Cannot generate answer using local vector store.",
                [],
            )
        chroma_search_result, final_context = self.rag.query_vector_store_to_build(
            question=question,
            token_limit=30000,
            results_num=results_num,
            max_sources=results_num,
        )

        # Create list of grounding passages texts
        grounding_passages_texts = []
        for item in chroma_search_result:
            returned_context = item.section.content
            grounding_passages_texts.append(returned_context)
            verbose_prompt += "\nID: \n" + returned_context + "\n"

        answer_text, aqa_search_result_initial = self.aqa_model.generate_answer(
            question, grounding_passages_texts, answer_style
        )

        # Map the AQA results back to SectionProbability objects.
        aqa_search_result = []
        if answer_text:
            for raw_result in aqa_search_result_initial:
                for item in chroma_search_result:
                    if raw_result["text"] == item.section.content:
                        aqa_search_result.append(
                            SectionProbability(
                                section=item.section,
                                probability=raw_result["probability"],
                            )
                        )

        if self.config.log_level in ("VERBOSE", "DEBUG"):
            self.print_the_prompt(verbose_prompt)
            if self.config.log_level == "DEBUG":
                print(self.aqa_model.get_saved_aqa_response_json())

        if not answer_text:
            return self.config.conditions.model_error_message, []
        return answer_text, aqa_search_result

    # Use this method for talking to Gemini's AQA model using a corpus
    # Answer style can be "VERBOSE" or ABSTRACTIVE, EXTRACTIVE
    def ask_aqa_model_using_corpora(
        self, question, corpus_name: str = "None", answer_style: str = "VERBOSE"
    ):
        """
        Use this method for talking to Gemini's AQA model using a corpus.

        Args:
            question (str): The user's question.
            corpus_name (str, optional): The name of the corpus to use. Defaults to "None".
            answer_style (str, optional): The style of the answer. Can be "VERBOSE", "ABSTRACTIVE", or "EXTRACTIVE". Defaults to "VERBOSE".

        Returns:
            tuple: A tuple containing the answer text and a list of SectionProbability objects.
                   Returns a model error message and an empty list if the model fails.
        """
        if not self.aqa_model:
            logging.error(
                "AQA model is not initialized. Cannot generate answer using corpora."
            )
            return (
                "AQA model is not initialized. Cannot generate answer using corpora.",
                [],
            )
        if corpus_name == "None":
            corpus_name = self.corpus_name
        (
            answer_text,
            aqa_search_result_raw,
        ) = self.aqa_model.generate_answer_with_corpora(
            question, corpus_name, answer_style
        )

        search_result = []
        if self.config.log_level == "VERBOSE":
            verbose_prompt = "[question]\n" + question + "\n"
            verbose_prompt += (
                "\n[answerable_probability]\n"
                + str(
                    self.aqa_model.get_saved_aqa_response_json().answerable_probability
                )
                + "\n"
            )
            for (
                attribution
            ) in (
                self.aqa_model.get_saved_aqa_response_json().answer.grounding_attributions
            ):
                verbose_prompt += "\n[grounding_attributions]\n" + str(
                    attribution.content.parts[0].text
                )
            self.print_the_prompt(verbose_prompt)
        elif self.config.log_level == "DEBUG":
            print(self.aqa_model.get_saved_aqa_response_json())

        if not answer_text:
            return self.config.conditions.model_error_message, []

        # Convert raw results to SectionProbability objects
        for raw_result in aqa_search_result_raw:
            section = markdown_splitter.DictionarytoSection(raw_result["metadata"])
            search_result.append(
                SectionProbability(
                    section=section, probability=raw_result["probability"]
                )
            )
        return answer_text, search_result

    def ask_aqa_model(self, question):
        response = ""
        if self.config.db_type == "google_semantic_retriever":
            response = self.ask_aqa_model_using_corpora(question)
        else:
            response = self.ask_aqa_model_using_local_vector_store(question)
        return response

    # Query the local Chroma vector database using the user question
    def query_vector_store(self, question, num_returns: int = 5):
        if not self.rag and not self.collection:
            logging.error("Chroma collection not initialized.")
            return None
        if not hasattr(self.collection, "query"):
            raise AttributeError(
                "Passed collection object does not have a 'query' method."
            )
        else:
            return self.collection.query(question, num_returns)

    # Add specific instruction as a prefix to the context
    def add_instruction_to_context(self, context):
        new_context = ""
        new_context += self.config.conditions.condition_text + "\n\n" + context
        return new_context

    # Print the prompt on the terminal for debugging
    def print_the_prompt(self, prompt):
        print("#########################################")
        print("#              PROMPT                   #")
        print("#########################################")
        print(prompt)
        print("#########################################")
        print("#           END OF PROMPT               #")
        print("#########################################")
        print("\n")

    # Use this method for talking to a Gemini content model
    # Optionally provide a prompt, if not use the one from config.yaml
    # config.yaml for the prompt
    def ask_content_model_with_context_prompt(
        self,
        context: str,
        question: str,
        prompt: typing.Optional[str] = None,
        model: typing.Optional[str] = None,
    ):
        if prompt == None:
            prompt = self.config.conditions.condition_text
        new_prompt = f"{prompt}\n\nContext:\n{context}\nQuestion:\n{question}"
        # Print the prompt for debugging if the log level is VERBOSE.
        if self.config.log_level == "VERBOSE":
            self.print_the_prompt(new_prompt)
        try:
            response = ""
            if model == "gemini-pro":
                response = self.gemini_pro.generate_content(
                    contents=new_prompt, log_level=self.config.log_level
                )
            elif model == "gemini-1.5":
                response = self.gemini_15.generate_content(
                    contents=new_prompt, log_level=self.config.log_level
                )
            else:
                response = self.language_model.generate_content(
                    contents=new_prompt, log_level=self.config.log_level
                )
        except Exception as e:
            print("Error in generate_content()")
            print(e)
            return self.config.conditions.model_error_message, new_prompt
        return response, new_prompt

    async def process_prompt_with_tools(
        self,
        prompt: str,
        verbose: bool = False,
    ):
        """
        Processes a prompt using tools. Returns an error if tools aren't
        configured.

        Args:
            prompt (str): The user's prompt.
            verbose (bool): Whether to enable verbose logging.

        Returns:
            str: The generated response or an error message.
        """
        if self.tool_manager:
            if hasattr(self.language_model, "generate_content_async"):
                logging.info("Processing prompt with tools using ToolManager...")
                return await self.tool_manager.process_prompt_with_tools(
                    prompt=prompt,
                    language_model=self.language_model,
                    verbose=verbose,
                )
            else:
                error_msg = f"Error: ToolManager is configured, but the language model '{self.language_model_name}' does not asynchronously generate content."
                logging.error(error_msg)
                return error_msg
        else:
            error_msg = "Error: Tool processing was requested, but no 'mcp_servers' are configured in the config.yaml. Cannot use tools."
            logging.error(error_msg)
            return error_msg
