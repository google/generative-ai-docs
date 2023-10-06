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

palm = PaLM(api_key=API_KEY, api_endpoint=PALM_API_ENDPOINT)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set up the path to the chroma vector database.
LOCAL_VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_stores/chroma")
COLLECTION_NAME = "docs_collection"

IS_CONFIG_FILE = True
if IS_CONFIG_FILE:
    config_values = read_config.ReadConfig()
    LOCAL_VECTOR_DB_DIR = config_values.returnConfigValue("vector_db_dir")
    COLLECTION_NAME = config_values.returnConfigValue("collection_name")
    CONDITION_TEXT = config_values.returnConfigValue("condition_text")
    FACT_CHECK_QUESTION = config_values.returnConfigValue("fact_check_question")
    MODEL_ERROR_MESSAGE = config_values.returnConfigValue("model_error_message")

# Select the number of contents to be used for providing context.
NUM_RETURNS = 5


class DocsAgent:
    """DocsAgent class"""

    def __init__(self):
        # Initialize the Chroma vector database
        logging.info(
            "Using the local vector database created at %s", LOCAL_VECTOR_DB_DIR
        )
        self.chroma = Chroma(LOCAL_VECTOR_DB_DIR)
        self.collection = self.chroma.get_collection(COLLECTION_NAME)
        # Update PaLM's custom prompt strings
        self.prompt_condition = CONDITION_TEXT
        self.fact_check_question = FACT_CHECK_QUESTION
        self.model_error_message = MODEL_ERROR_MESSAGE

    # Use this method for talking to PaLM (Text)
    def ask_text_model_with_context(self, context, question):
        new_prompt = f"{context}\nQuestion: {question}"
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

    # Use this method for talking to PaLM (Chat)
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
            return self.palm_none_response
        return response.last

    # Use this method for asking PaLM (Text) for fact-checking
    def ask_text_model_to_fact_check(self, context, prev_response):
        question = self.fact_check_question + "\n\nText: "
        question += prev_response
        return self.ask_text_model_with_context(context, question)

    # Query the local Chroma vector database using the user question
    def query_vector_store(self, question):
        return self.collection.query(question, NUM_RETURNS)

    # Add specific instruction as a prefix to the context
    def add_instruction_to_context(self, context):
        new_context = ""
        new_context += self.prompt_condition + "\n" + context
        return new_context
