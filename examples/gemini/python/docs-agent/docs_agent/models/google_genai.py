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

"""Rate limited Gemini wrapper"""

import typing
from typing import List
import time

import google.generativeai
from google.generativeai.types import GenerationConfig
from ratelimit import limits
from ratelimit import sleep_and_retry

from docs_agent.utilities.config import Models
from docs_agent.utilities.config import Conditions


class Error(Exception):
    """Base error class for Gemini."""


class GoogleNoAPIKeyError(Error, RuntimeError):
    """Raised if no API key is provided nor found in environment variable."""

    def __init__(self) -> None:
        super().__init__(
            "Google API key is not provided "
            "or set in the environment variable GOOGLE_API_KEY"
        )


class GoogleUnsupportedModelError(Error, RuntimeError):
    """Raised if a specified model is not supported by the endpoint."""

    def __init__(self, model, api_endpoint) -> None:
        super().__init__(
            f"The specified model {model} is not supported "
            f"on the API endpoint {api_endpoint}"
        )


# Create a class for the response schema
# class DocType(enum.Enum):
#     CONCEPT = "concept"
#     CODELAB = "codelab"
#     REFERENCE = "reference"
#     OTHER = "other"
#     GUIDE = "guide"


class Gemini:
    """Rate limited Gemini wrapper.

    This class exposes Gemini's chat, text, and embedding API, but with a rate
    limit. Besides the rate limit, the `chat` and `generate_text` method has the
    same name and behavior as `google.generativeai.chat` and
    `google.generativeai.generate_text`, respectively. The `embed` method is
    different from `google.generativeai.generate_embeddings` since `embed`
    returns List[float] while `google.generativeai.generate_embeddings` returns a
    dict. And that's why it has a different name.
    """

    minute = 60  # seconds in a minute
    max_embed_per_minute = 1400
    max_text_per_minute = 30

    # MAX_MESSAGE_PER_MINUTE = 30
    def __init__(
        self,
        models_config: Models,
        conditions: typing.Optional[Conditions] = None,
    ) -> None:
        if conditions is None:
            self.model_error_message = "Gemini model failed to generate"
            self.prompt_condition = ""
        else:
            self.model_error_message = conditions.model_error_message
            self.prompt_condition = conditions.condition_text
        self.api_endpoint = models_config.api_endpoint
        self.api_key = models_config.api_key
        self.embed_model = models_config.embedding_model
        self.language_model = models_config.language_model
        self.embedding_api_call_limit = models_config.embedding_api_call_limit
        self.embedding_api_call_period = models_config.embedding_api_call_period
        self.response_type = models_config.response_type
        self.response_schema = models_config.response_schema
        # Sets the response type to full mime type
        if self.response_type:
            match self.response_type:
                case "x.enum":
                    self.response_type = "text/x.enum"
                case "json":
                    self.response_type = "application/json"
                case _:
                    self.response_type = "text/plain"
            self.generation_config = GenerationConfig(
                response_mime_type=self.response_type,
            )
        # Configure the model
        google.generativeai.configure(
            api_key=self.api_key, client_options={"api_endpoint": self.api_endpoint}
        )
        # Check whether the specified models are supported
        # supported_models = set(
        #    model.name for model in google.generativeai.list_models()
        # )
        # for model in (models_config.language_model, models_config.embedding_model):
        #  if model not in supported_models:
        #    raise GoogleUnsupportedModelError(model, self.api_endpoint)

    # TODO: bring in limit values from config files
    @sleep_and_retry
    @limits(calls=max_embed_per_minute, period=minute)
    def embed(
        self,
        content,
        task_type: str = "RETRIEVAL_QUERY",
        title: typing.Optional[str] = None,
    ) -> List[float]:
        if (
            self.embed_model == "models/embedding-001"
            or self.embed_model == "models/text-embedding-004"
        ):
            return [
                google.generativeai.embed_content(
                    model=self.embed_model,
                    content=content,
                    task_type=task_type,
                    title=title,
                )["embedding"]
            ]
        else:
            raise GoogleUnsupportedModelError(self.embed_model, self.api_endpoint)

    # TODO: bring in limit values from config files
    @sleep_and_retry
    @limits(calls=max_text_per_minute, period=minute)
    def generate_content(
        self, contents, request_options=None, log_level: typing.Optional[str] = "NORMAL"
    ):
        if self.language_model is None:
            raise GoogleUnsupportedModelError(self.language_model, self.api_endpoint)
        model = google.generativeai.GenerativeModel(model_name=self.language_model)
        try:
            if request_options is None:
                response = model.generate_content(
                    contents, generation_config=self.generation_config
                )
            else:
                response = model.generate_content(
                    contents,
                    request_options=request_options,
                    generation_config=self.generation_config,
                )
        except google.api_core.exceptions.InvalidArgument:
            return self.model_error_message
        if log_level == "VERBOSE" or log_level == "DEBUG":
            print("[Response JSON]")
            print(response)
            print()
        for chunk in response:
            if not hasattr(chunk, "candidates"):
                return self.model_error_message
            if len(chunk.candidates) == 0:
                return self.model_error_message
            if not hasattr(chunk.candidates[0], "content"):
                return self.model_error_message
            if str(chunk.candidates[0].content) == "":
                return self.model_error_message
        return response.text

    # Use this method for talking to a Gemini content model
    # Optionally provide a prompt, if not use the one from config.yaml
    def ask_content_model_with_context_prompt(
        self,
        context: str,
        question: str,
        prompt: typing.Optional[str] = None,
        log_level: typing.Optional[str] = "NORMAL",
    ):
        if prompt == None:
            prompt = self.prompt_condition
        # elif prompt == "fact_checker":
        #   prompt = self.fact_check_question
        new_prompt = f"{prompt}\n\nQuestion: {question}\n\nContext:\n{context}"
        # Print the prompt for debugging if the log level is VERBOSE.
        # if LOG_LEVEL == "VERBOSE":
        #   self.print_the_prompt(new_prompt)
        try:
            response = self.generate_content(new_prompt)
        except google.api_core.exceptions.InvalidArgument:
            return self.model_error_message
        if log_level == "VERBOSE" or log_level == "DEBUG":
            print("[Response JSON]")
            print(response)
            print()
        for chunk in response:
            if not hasattr(chunk, "candidates"):
                return self.model_error_message
            if len(chunk.candidates) == 0:
                return self.model_error_message
            if not hasattr(chunk.candidates[0], "content"):
                return self.model_error_message
            if str(chunk.candidates[0].content) == "":
                return self.model_error_message
        return response.text, new_prompt

    # Use this method for uploading a file to File API such as Video
    # Returns the name of the uploaded file
    def upload_file(self, file):
        print(f"Uploading file...")
        uploaded_file = google.generativeai.upload_file(path=file)
        print(f"Completed upload: {uploaded_file.uri}")
        return uploaded_file

    # Use this method for retrieving a file from the File API such as Video
    # Returns the file object
    def get_file(self, file):
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = google.generativeai.get_file(file.name)

        if file.state.name == "FAILED":
            print(f"Failed to get file: {file.name}")
            raise ValueError(file.state.name)
        return file
