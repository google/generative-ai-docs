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

from chroma import Chroma
from palm import PaLM

from scripts import read_config

# Set up the PaLM API key from the environment.
API_KEY = os.getenv("PALM_API_KEY")
if API_KEY is None:
    sys.exit("Please set the environment variable PALM_API_KEY to be your API key.")

# Select your PaLM API endpoint.
PALM_API_ENDPOINT = "generativelanguage.googleapis.com"
LANGUAGE_MODEL = None
EMBEDDING_MODEL = None

# Set up the path to the chroma vector database.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_stores/chroma")
COLLECTION_NAME = "docs_collection"

# Set the log level for the DocsAgent class: NORMAL or VERBOSE
LOG_LEVEL = "NORMAL"

IS_CONFIG_FILE = True
if IS_CONFIG_FILE:
    config_values = read_config.ReadConfig()
    LOCAL_VECTOR_DB_DIR = config_values.returnConfigValue("vector_db_dir")
    COLLECTION_NAME = config_values.returnConfigValue("collection_name")
    CONDITION_TEXT = config_values.returnConfigValue("condition_text")
    FACT_CHECK_QUESTION = config_values.returnConfigValue("fact_check_question")
    MODEL_ERROR_MESSAGE = config_values.returnConfigValue("model_error_message")
    LOG_LEVEL = config_values.returnConfigValue("log_level")
    PALM_API_ENDPOINT = config_values.returnConfigValue("api_endpoint")
    LANGUAGE_MODEL = config_values.returnConfigValue("language_model")
    EMBEDDING_MODEL = config_values.returnConfigValue("embedding_model")

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


class DocsAgent:
    """DocsAgent class"""

    def __init__(self):
        # Initialize the Chroma vector database
        logging.info(
            "Using the local vector database created at %s", LOCAL_VECTOR_DB_DIR
        )
        self.chroma = Chroma(LOCAL_VECTOR_DB_DIR)
        self.collection = self.chroma.get_collection(
            COLLECTION_NAME, embedding_model=EMBEDDING_MODEL
        )
        # Update PaLM's custom prompt strings
        self.prompt_condition = CONDITION_TEXT
        self.fact_check_question = FACT_CHECK_QUESTION
        self.model_error_message = MODEL_ERROR_MESSAGE
        # Models settings
        self.language_model = LANGUAGE_MODEL
        self.embedding_model = EMBEDDING_MODEL

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
