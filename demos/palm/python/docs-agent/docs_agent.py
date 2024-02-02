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

import os
import sys

from absl import logging
import google.api_core
import google.ai.generativelanguage as glm
from chromadb.utils import embedding_functions

from modules.chroma import Chroma, Format
from modules.palm import PaLM

from scripts import read_config, markdown_splitter, tokenCount

# Set up the PaLM API key from the environment.
API_KEY = os.getenv("PALM_API_KEY")
if API_KEY is None:
    sys.exit("Please set the environment variable PALM_API_KEY to be your API key.")

# Select your PaLM API endpoint.
PALM_API_ENDPOINT = "generativelanguage.googleapis.com"
LANGUAGE_MODEL = None
EMBEDDING_MODEL = None
AQA_MODEL = "models/aqa"

# Set up the path to the chroma vector database.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_stores/chroma")
COLLECTION_NAME = "docs_collection"
PRODUCT_NAME = ""
DB_TYPE = "LOCAL_DB"
IS_AQA_USED = "NO"

# Set the log level for the DocsAgent class: NORMAL or VERBOSE
LOG_LEVEL = "NORMAL"

IS_CONFIG_FILE = True
if IS_CONFIG_FILE:
    config_values = read_config.ReadConfig()
    LOCAL_VECTOR_DB_DIR = config_values.returnConfigValue("vector_db_dir")
    COLLECTION_NAME = config_values.returnConfigValue("collection_name")
    PRODUCT_NAME = config_values.returnConfigValue("product_name")
    CONDITION_TEXT = config_values.returnConfigValue("condition_text")
    FACT_CHECK_QUESTION = config_values.returnConfigValue("fact_check_question")
    MODEL_ERROR_MESSAGE = config_values.returnConfigValue("model_error_message")
    LOG_LEVEL = config_values.returnConfigValue("log_level")
    PALM_API_ENDPOINT = config_values.returnConfigValue("api_endpoint")
    LANGUAGE_MODEL = config_values.returnConfigValue("language_model")
    EMBEDDING_MODEL = config_values.returnConfigValue("embedding_model")
    DB_TYPE = config_values.returnConfigValue("db_type")
    IS_AQA_USED = config_values.returnConfigValue("is_aqa_used")

# Select the number of contents to be used for providing context.
NUM_RETURNS = 5

# Initialize the PaLM instance.
if LANGUAGE_MODEL != None and EMBEDDING_MODEL != None:
    if "gemini" in LANGUAGE_MODEL:
        palm = PaLM(
            api_key=API_KEY,
            api_endpoint=PALM_API_ENDPOINT,
            content_model=LANGUAGE_MODEL,
            embed_model=EMBEDDING_MODEL,
        )
    else:
        palm = PaLM(
            api_key=API_KEY,
            api_endpoint=PALM_API_ENDPOINT,
            text_model=LANGUAGE_MODEL,
            embed_model=EMBEDDING_MODEL,
        )
elif EMBEDDING_MODEL != None:
    palm = PaLM(
        api_key=API_KEY, api_endpoint=PALM_API_ENDPOINT, embed_model=EMBEDDING_MODEL
    )
else:
    palm = PaLM(api_key=API_KEY, api_endpoint=PALM_API_ENDPOINT)

embedding_function_gemini_retrieval = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=API_KEY, model_name="models/embedding-001",
    task_type="RETRIEVAL_QUERY")

class DocsAgent:
    """DocsAgent class"""

    def __init__(self):
        # Initialize the Chroma vector database
        logging.info(
            "Using the local vector database created at %s", LOCAL_VECTOR_DB_DIR
        )
        self.chroma = Chroma(LOCAL_VECTOR_DB_DIR)
        self.collection = self.chroma.get_collection(
            COLLECTION_NAME, embedding_model=EMBEDDING_MODEL,
            embedding_function=embedding_function_gemini_retrieval
        )
        # Update PaLM's custom prompt strings
        self.prompt_condition = CONDITION_TEXT
        self.fact_check_question = FACT_CHECK_QUESTION
        self.model_error_message = MODEL_ERROR_MESSAGE
        # Models settings
        self.language_model = LANGUAGE_MODEL
        self.embedding_model = EMBEDDING_MODEL
        self.aqa_model = AQA_MODEL
        self.is_aqa_used = IS_AQA_USED
        self.db_type = DB_TYPE
        # AQA model setup
        self.generative_service_client = glm.GenerativeServiceClient()
        self.retriever_service_client = glm.RetrieverServiceClient()
        self.permission_service_client = glm.PermissionServiceClient()
        self.corpus_display = PRODUCT_NAME + " documentation"
        self.corpus_name = "corpora/" + PRODUCT_NAME.lower().replace(" ", "-")
        self.aqa_response_buffer = ""

    # Use this method for talking to a PaLM text model
    def ask_text_model_with_context(self, context, question):
        new_prompt = f"{context}\n\nQuestion: {question}"
        # Print the prompt for debugging if the log level is VERBOSE.
        if LOG_LEVEL == "VERBOSE":
            self.print_the_prompt(new_prompt)
        try:
            response = palm.generate_text(
                prompt=new_prompt,
                max_output_tokens=800,
                candidate_count=1,
                temperature=0.0,
            )
        except google.api_core.exceptions.InvalidArgument:
            return self.model_error_message
        if response.result is None:
            print("Block reason: " + str(response.filters))
            print("Safety feedback: " + str(response.safety_feedback))
            return self.model_error_message
        return response.result

    # Use this method for talking to a Gemini content model
    def ask_content_model_with_context(self, context, question):
        new_prompt = context + "\n\nQuestion: " + question
        # Print the prompt for debugging if the log level is VERBOSE.
        if LOG_LEVEL == "VERBOSE":
            self.print_the_prompt(new_prompt)
        try:
            response = palm.generate_content(new_prompt)
        except google.api_core.exceptions.InvalidArgument:
            return self.model_error_message
        for chunk in response:
            if str(chunk.candidates[0].content) == "":
                return self.model_error_message
        return response.text

    # Use this method for talking to Gemini's AQA model using inline passages
    def ask_aqa_model_using_local_vector_store(self, question):
        user_query_content = glm.Content(parts=[glm.Part(text=question)])
        answer_style = "VERBOSE"  # or ABSTRACTIVE, EXTRACTIVE

        # Retrieve a list of context from the local vector database
        result = self.query_vector_store(question)
        verbose_prompt = "Question: " + question + "\n"

        # Create the grounding inline passages
        grounding_passages = glm.GroundingPassages()
        for i in range(NUM_RETURNS):
            returned_context = result.fetch_at_formatted(i, Format.CONTEXT)
            new_passage = glm.Content(parts=[glm.Part(text=returned_context)])
            index_id = str("{:03d}".format(i + 1))
            grounding_passages.passages.append(
                glm.GroundingPassage(content=new_passage, id=index_id)
            )
            verbose_prompt += "\nID: " + index_id + "\n" + returned_context + "\n"

        # Create a request to the AQA model
        req = glm.GenerateAnswerRequest(
            model=AQA_MODEL,
            contents=[user_query_content],
            inline_passages=grounding_passages,
            answer_style=answer_style,
        )
        try:
            aqa_response = self.generative_service_client.generate_answer(req)
            self.aqa_response_buffer = aqa_response
        except:
            self.aqa_response_buffer = ""
            return self.model_error_message

        if LOG_LEVEL == "VERBOSE":
            self.print_the_prompt(verbose_prompt)
        elif LOG_LEVEL == "DEBUG":
            self.print_the_prompt(verbose_prompt)
            print(aqa_response)
        return aqa_response.answer.content.parts[0].text

    # Use this method for talking to Gemini's AQA model using a corpus
    def ask_aqa_model_using_corpora(self, question):
        answer_style = "VERBOSE"  # or ABSTRACTIVE, EXTRACTIVE

        # Prepare parameters for the AQA model
        content = glm.Content(parts=[glm.Part(text=question)])
        retriever_config = glm.SemanticRetrieverConfig(
            source=self.corpus_name, query=content
        )

        # Create a request to the AQA model
        req = glm.GenerateAnswerRequest(
            model=AQA_MODEL,
            contents=[content],
            semantic_retriever=retriever_config,
            answer_style=answer_style,
        )
        try:
            aqa_response = self.generative_service_client.generate_answer(req)
            self.aqa_response_buffer = aqa_response
        except:
            self.aqa_response_buffer = ""
            return self.model_error_message

        if LOG_LEVEL == "VERBOSE":
            verbose_prompt = "[question]\n" + question + "\n"
            verbose_prompt += (
                "\n[answerable_probability]\n"
                + str(aqa_response.answerable_probability)
                + "\n"
            )
            for attribution in aqa_response.answer.grounding_attributions:
                verbose_prompt += "\n[grounding_attributions]\n" + str(
                    aqa_response.answer.grounding_attributions[0].content.parts[0].text
                )
            self.print_the_prompt(verbose_prompt)
        elif LOG_LEVEL == "DEBUG":
            print(aqa_response)
        return aqa_response.answer.content.parts[0].text

    def ask_aqa_model(self, question):
        response = ""
        if self.db_type == "ONLINE_STORAGE":
            response = self.ask_aqa_model_using_corpora(question)
        else:
            response = self.ask_aqa_model_using_local_vector_store(question)
        return response

    # Use this method for talking to a PaLM chat model
    def ask_chat_model_with_context(self, context, question):
        try:
            response = palm.chat(
                context=context,
                messages=question,
                temperature=0.05,
            )
        except google.api_core.exceptions.InvalidArgument:
            return self.model_error_message

        if response.last is None:
            return self.model_error_message
        return response.last

    # Use this method for asking a PaLM text model for fact-checking
    def ask_text_model_to_fact_check(self, context, prev_response):
        question = self.fact_check_question + "\n\nText: "
        question += prev_response
        return self.ask_text_model_with_context(context, question)

    # Use this method for asking a Gemini content model for fact-checking
    def ask_content_model_to_fact_check(self, context, prev_response):
        question = self.fact_check_question + "\n\nText: "
        question += prev_response
        return self.ask_content_model_with_context(context, question)

    # Query the local Chroma vector database using the user question
    def query_vector_store(self, question):
        return self.collection.query(question, NUM_RETURNS)

    # Add specific instruction as a prefix to the context
    def add_instruction_to_context(self, context):
        new_context = ""
        new_context += self.prompt_condition + "\n\n" + context
        return new_context

    # Add custom instruction as a prefix to the context
    def add_custom_instruction_to_context(self, condition, context):
        new_context = ""
        new_context += condition + "\n\n" + context
        return new_context

    # Generate an embedding given text input
    def generate_embedding(self, text):
        return palm.embed(text)

    # Get the name of the language model used in this Docs Agent setup
    def get_language_model_name(self):
        return self.language_model

    # Get the name of the embedding model used in this Docs Agent setup
    def get_embedding_model_name(self):
        return self.embedding_model

    # Get the type of the database used in this Docs Agent setup
    def get_db_type(self):
        return self.db_type

    # Return true if the aqa model used in this Docs Agent setup
    def check_if_aqa_is_used(self):
        if self.is_aqa_used == "YES":
            return True
        else:
            return False

    # Get the save response of the aqa model
    def get_saved_aqa_response_json(self):
        return self.aqa_response_buffer

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
