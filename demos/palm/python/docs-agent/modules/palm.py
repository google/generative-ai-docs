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

"""Rate limited PaLM wrapper"""

import os

import google.generativeai
from ratelimit import limits, sleep_and_retry
from typing import List


class Error(Exception):
    """Base error class for palm"""


class PaLMNoAPIKeyError(Error, RuntimeError):
    """Raised if no API key is provided nor found in environment variable."""

    def __init__(self) -> None:
        super().__init__(
            "PaLM API key is not provided "
            "or set in the environment variable PALM_API_KEY"
        )


class PaLMUnsupportedModelError(Error, RuntimeError):
    """Raised if a specified model is not supported by the endpoint."""

    def __init__(self, model, api_endpoint) -> None:
        super().__init__(
            f"The specified model {model} is not supported "
            f"on the API endpoint {api_endpoint}"
        )


class PaLMNoModelError(Error, RuntimeError):
    """Raised if calling an API but the corresponding model is not specified."""

    def __init__(self, func_name, attr) -> None:
        super().__init__(
            f"Cannot call PaLM.{func_name}() since PaLM.{attr} is not set "
            "during class initialization."
        )


class PaLM:
    """Rate limited PaLM wrapper

    This class exposes PaLM's chat, text, and embedding API, but with a rate limit.
    Besides the rate limit, the `chat` and `generate_text` method has the same name and
    behavior as `google.generativeai.chat` and `google.generativeai.generate_text`,
    respectively. The `embed` method is different from
    `google.generativeai.generate_embeddings` since `embed` returns List[float]
    while `google.generativeai.generate_embeddings` returns a dict. And that's why it
    has a different name.
    """

    DEFAULT_ENDPOINT = "generativelanguage.googleapis.com"  # Prod endpoint
    MINUTE = 60  # seconds in a minute
    MAX_EMBED_PER_MINUTE = 1500
    MAX_MESSAGE_PER_MINUTE = 30
    MAX_TEXT_PER_MINUTE = 30

    def __init__(
        self,
        api_key=None,
        api_endpoint=DEFAULT_ENDPOINT,
        chat_model=None,
        text_model=None,
        content_model=None,
        embed_model=None,
        find_models=True,
    ) -> None:
        if api_key is None:
            api_key = os.getenv("PALM_API_KEY")
        if api_key is None:
            raise PaLMNoAPIKeyError()
        google.generativeai.configure(
            api_key=api_key, client_options={"api_endpoint": api_endpoint}
        )
        self.api_endpoint = api_endpoint
        self.chat_model = chat_model
        self.text_model = text_model
        self.content_model = content_model
        self.embed_model = embed_model

        # Check whether the specified models are supported
        supported_models = set(
            model.name for model in google.generativeai.list_models()
        )
        for model in (chat_model, text_model, content_model, embed_model):
            if model and model not in supported_models:
                raise PaLMUnsupportedModelError(model, api_endpoint)

        # Check whether we need to find available models
        if (not find_models) or (
            chat_model is not None
            and text_model is not None
            and content_model is not None
            and embed_model is not None
        ):
            return
        # Find available models
        for model in google.generativeai.list_models():
            if (
                self.chat_model is None
                and "generateMessage" in model.supported_generation_methods
                and "chat" in model.name
            ):
                self.chat_model = model.name
            if (
                self.text_model is None
                and "generateText" in model.supported_generation_methods
            ):
                self.text_model = model.name
            if (
                self.content_model is None
                and "generateContent" in model.supported_generation_methods
            ):
                self.content_model = model.name
            if self.embed_model is None and (
                "embedText" in model.supported_generation_methods
                or "embedContent" in model.supported_generation_methods
            ):
                self.embed_model = model.name

    @sleep_and_retry
    @limits(calls=MAX_MESSAGE_PER_MINUTE, period=MINUTE)
    def chat(self, *args, **kwargs):
        if self.chat_model is None:
            raise PaLMNoModelError(func_name="chat", attr="chat_model")
        return google.generativeai.chat(*args, model=self.chat_model, **kwargs)

    @sleep_and_retry
    @limits(calls=MAX_TEXT_PER_MINUTE, period=MINUTE)
    def generate_text(self, *args, **kwargs):
        if self.text_model is None:
            raise PaLMNoModelError(func_name="generate_text", attr="text_model")
        return google.generativeai.generate_text(*args, model=self.text_model, **kwargs)

    @sleep_and_retry
    @limits(calls=MAX_TEXT_PER_MINUTE, period=MINUTE)
    def generate_content(self, text):
        if self.content_model is None:
            raise PaLMNoModelError(func_name="generate_content", attr="content_model")
        model = google.generativeai.GenerativeModel(model_name=self.content_model)
        return model.generate_content(text)

    @sleep_and_retry
    @limits(calls=MAX_EMBED_PER_MINUTE, period=MINUTE)
    def embed(self, text: str) -> List[float]:
        if self.embed_model is None:
            raise PaLMNoModelError(func_name="embed", attr="embed_model")
        if self.embed_model == "models/embedding-001":
            # Use the `embed_content()` method if it's the new Gemini embedding model.
            return google.generativeai.embed_content(
                model=self.embed_model, content=text
            )["embedding"]
        else:
            return google.generativeai.generate_embeddings(
                model=self.embed_model, text=text
            )["embedding"]
