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

from docs_agent.models.base import GenerativeLanguageModel
from docs_agent.models.google_genai import Gemini
from docs_agent.utilities.config import Models


class GenerativeLanguageModelFactory:
    """Factory class for creating generative language models."""

    @staticmethod
    def create_model(
        model_type: str,
        models_config: Models,
        conditions: typing.Optional[typing.Any] = None,
    ) -> GenerativeLanguageModel:
        """Creates a generative language model."""
        # Remove the "models/" prefix if it exists. models/ prefix is legacy
        if model_type.startswith("models/"):
            model_type = model_type.removeprefix("models/")
        if model_type.startswith("gemini"):
            return Gemini(models_config=models_config, conditions=conditions)
        # This then needs to be moved for the embedding model
        if model_type.startswith(("text-embedding", "embedding", "gemini-embedding")):
            return Gemini(models_config=models_config, conditions=conditions)
        elif model_type == "aqa":
            gemini_config = Models(
                language_model="gemini-2.0-flash",
                embedding_model=models_config.embedding_model,
                api_endpoint=models_config.api_endpoint,
            )
            return Gemini(models_config=gemini_config, conditions=conditions)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
