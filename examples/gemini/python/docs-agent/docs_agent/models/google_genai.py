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
from typing import Any, Dict, List, cast
import time
import os
import mimetypes
from PIL import Image
from io import BytesIO

from absl import logging

from google import genai
from google.genai import types

from ratelimit import limits
from ratelimit import sleep_and_retry

from docs_agent.utilities.config import Models
from docs_agent.utilities.config import Conditions
from docs_agent.utilities.helpers import open_image

from docs_agent.models.base import GenerativeLanguageModel


class Error(Exception):
    """Base error class for Gemini."""

    pass  # Add pass here to avoid indentation errors


class GoogleNoAPIKeyError(Error, RuntimeError):
    """Raised if no API key is provided."""

    def __init__(self) -> None:
        super().__init__(
            "Google API key is not provided "
            "or set in the environment variable GOOGLE_API_KEY"
        )


class GoogleUnsupportedModelError(Error, RuntimeError):
    """Raised if a specified model is not supported."""

    def __init__(self, model, api_endpoint) -> None:
        super().__init__(
            f"The specified model {model} is not supported "
            f"on the API endpoint {api_endpoint}"
        )


class Gemini(GenerativeLanguageModel):
    """
    A wrapper for the Google Gemini model.
    """

    minute = 60
    # 1400 calls per minute for embedding text-embedding-004 and embedding-001
    # Use half to avoid hitting the limit
    max_embed_per_minute = 130
    max_text_per_minute = 30

    def __init__(
        self,
        models_config: Models,
        conditions: typing.Optional[Conditions] = None,
    ) -> None:
        """Initializes the Gemini model.

        Args:
            models_config: The configuration for the models.
            conditions: The conditions for the model.
        """
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
        self.safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            )
        ]
        self.config = types.GenerateContentConfig(safety_settings=self.safety_settings)
        # Configure the model for image generation
        if self.language_model.startswith("gemini-2.0-flash-exp-image-generation"):
            self.config = types.GenerateContentConfig(
                response_modalities=["Text", "Image"],
                safety_settings=self.safety_settings,
            )
        # Configure the model
        self.client = genai.Client(api_key=self.api_key)
        logging.info(f"Created Gemini client for model: {self.language_model}")

    @sleep_and_retry
    @limits(calls=max_embed_per_minute, period=minute)
    def embed(
        self,
        content,
        task_type: str = "RETRIEVAL_QUERY",
        title: typing.Optional[str] = None,
    ) -> List[float]:
        if (
            self.embed_model == "embedding-001"
            or self.embed_model == "text-embedding-004"
            or self.embed_model == "gemini-embedding-exp-03-07"
        ):
            return [
                self.client.models.embed_content(
                    model=self.embed_model,
                    contents=content,
                    config=types.EmbedContentConfig(task_type=task_type, title=title),
                )
                .embeddings[0]
                .values
            ]
        else:
            raise GoogleUnsupportedModelError(self.embed_model, self.api_endpoint)

    @sleep_and_retry
    @limits(calls=max_text_per_minute, period=minute)
    def generate_content(
        self,
        contents,
        log_level: typing.Optional[str] = "NORMAL",
        image_output_path: typing.Optional[str] = "image.png",
    ):
        """
        Generates content using the Gemini model.

        Args:
            contents: The content to generate from.
            log_level: The level of logging.
            image_output_path: The path to save the generated image.

        Returns:
            The generated content or an error message.
        """
        if self.language_model is None:
            raise GoogleUnsupportedModelError(self.language_model, self.api_endpoint)
        try:
            response = self.client.models.generate_content(
                model=self.language_model,
                contents=contents,
                config=self.config,
            )
        except:
            return self.model_error_message
        if log_level == "VERBOSE" or log_level == "DEBUG":
            print("[Response JSON]")
            print(response)
            print()
        try:
            for part in response.candidates[0].content.parts:
                # If the response contains an image, save it to the specified path.
                if part.inline_data is not None:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    image.save(image_output_path)
                    # Return a message indicating that the image was generated from
                    # the prompt.
                    return f"Image generated from your prompt."
                if part.text is not None:
                    return part.text
        except:
            return self.model_error_message

    async def generate_content_async(
        self,
        contents: typing.List[typing.Dict[str, typing.Any]],
        tools: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Generates content asynchronously using the Gemini model.

        Args:
            contents: The conversation history as a list of dictionaries.
                      Expected format: [{"role": str, "parts": [Dict]}]
            tools: The tools as a list of dictionaries (FunctionDeclaration format).

        Returns:
            A dictionary representing the model's response, including potential
            errors or blocking information.
            Format: {"role": "model", "parts": [...], "error": Optional[str], "blocked": Optional[bool], ...}
        """
        if self.language_model is None:
            return {"error": f"Unsupported model: {self.language_model}", "role": "model", "parts": []}
        logging.info(f"Gemini: Generating content asynchronously for model: {self.language_model}")
        gemini_contents = []
        try:
            for item in contents:
                if isinstance(item, dict) and "role" in item and "parts" in item:
                     # Convert parts based on role
                     converted_parts = []
                     for part_dict in item["parts"]:
                         if "text" in part_dict:
                             converted_parts.append(types.Part(text=part_dict["text"]))
                         elif "function_call" in part_dict:
                              fc_dict = part_dict["function_call"]
                              converted_parts.append(types.Part(function_call=types.FunctionCall(**fc_dict)))
                         elif "function_response" in part_dict:
                              fr_dict = part_dict["function_response"]
                              converted_parts.append(types.Part(function_response=types.FunctionResponse(**fr_dict)))
                     gemini_contents.append(types.Content(role=item["role"], parts=converted_parts))
                else:
                     logging.warning(f"Skipping invalid content item during conversion: {item}")
        except Exception as e:
            logging.error(f"Error converting generic contents to Gemini format: {e}")
            return {"error": f"Content conversion failed: {e}", "role": "model", "parts": []}

        gemini_tools = None
        if tools:
            try:
                declarations = []
                for tool_dict in tools:
                    if "name" in tool_dict and "description" in tool_dict and "parameters" in tool_dict:
                         params = tool_dict["parameters"]
                         if not isinstance(params, dict):
                              logging.warning(f"Tool '{tool_dict['name']}' has non-dict parameters: {type(params)}. Attempting to use anyway.")
                         declarations.append(types.FunctionDeclaration(**tool_dict))
                    else:
                         logging.warning(f"Skipping invalid tool dict during conversion: {tool_dict}")
                if declarations:
                    gemini_tools = [types.Tool(function_declarations=declarations)]
                    logging.info(f"Converted {len(declarations)} generic tools to Gemini format.")
                else:
                    logging.warning("No valid generic tools found to convert for Gemini.")
            except Exception as e:
                logging.error(f"Error converting generic tools to Gemini format: {e}")
                return {"error": f"Tool conversion failed: {e}", "role": "model", "parts": []}

        # --- Prepare API Call ---
        model_config = {}
        if self.safety_settings:
            model_config["safety_settings"] = self.safety_settings

        if gemini_tools:
            model_config["tools"] = gemini_tools
            logging.info("Added converted tools to Gemini API call config.")

        # --- Call API and Process Response ---
        try:
            response = await self.client.aio.models.generate_content(
                model=self.language_model,
                contents=gemini_contents,
                config=model_config,
            )

            # --- Convert google.genai response to generic dictionary ---
            response_dict = {"role": "model", "parts": []}
            finish_reason = None
            block_reason = None
            safety_ratings = []

            # Check for blocking via prompt_feedback first
            if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                 block_reason = getattr(response.prompt_feedback, "block_reason", None)
                 if block_reason:
                     response_dict["blocked"] = True
                     response_dict["block_reason"] = block_reason.name # Or str(block_reason)
                     response_dict["error"] = f"Prompt blocked due to {block_reason.name}"
                     logging.error(f"Prompt blocked by API. Reason: {block_reason.name}")
                     return response_dict

            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, "finish_reason", None)
                safety_ratings = getattr(candidate, "safety_ratings", [])

                # Check for blocking via finish_reason or safety_ratings
                if finish_reason == types.FinishReason.SAFETY:
                     response_dict["blocked"] = True
                     response_dict["block_reason"] = finish_reason.name
                     response_dict["error"] = f"Response blocked due to {finish_reason.name}"
                     logging.error(f"Response blocked by safety settings. Finish Reason: {finish_reason.name}, Ratings: {safety_ratings}")
                     return response_dict

                parts_list: List[Dict[str, Any]] = response_dict["parts"]
                if hasattr(candidate, "content") and candidate.content and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        part_dict = {}
                        if hasattr(part, "text") and part.text:
                            part_dict["text"] = part.text
                        if hasattr(part, "function_call") and part.function_call:
                            # Convert FunctionCall object to dict
                            fc = part.function_call
                            part_dict["function_call"] = {"name": fc.name, "args": dict(fc.args)}

                        if part_dict:
                             # Append to the extracted list variable
                             parts_list.append(part_dict)

            # Add finish reason if needed for downstream logic
            if finish_reason:
                 response_dict["finish_reason"] = finish_reason.name

            return response_dict

        except Exception as e:
            logging.error(f"Gemini: Async generate_content call failed: {type(e).__name__}: {e}")
            # Return error as dict
            return {"error": f"API call failed: {type(e).__name__}: {e}", "role": "model", "parts": []}

    def upload_file(self, file):
        print(f"Uploading file...")
        uploaded_file = self.client.files.upload(file=file)
        print(f"Completed upload: {uploaded_file.uri}")
        return uploaded_file

    def get_file(self, file):
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = self.client.files.get(name=file.name)

        if file.state.name == "FAILED":
            print(f"Failed to get file: {file.name}")
            raise ValueError(file.state.name)
        return file

    def ask_content_model_with_context_prompt(
        self,
        context: str,
        question: str,
        prompt: typing.Optional[str] = None,
        log_level: typing.Optional[str] = "NORMAL",
    ):
        if prompt == None:
            prompt = self.prompt_condition
        new_prompt = f"{prompt}\n\nQuestion: {question}\n\nContext:\n{context}"
        try:
            response = self.generate_content(new_prompt)
        except:
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

    def ask_about_file(self, prompt: str, file_path: str):
        """
        Use this method for asking Gemini model about a file.

        Args:
            prompt (str): The prompt to use for the model.
            file_path (str): The path to the file.

        Returns:
            str: The response from the model or raise an exception.
        """
        file_size = os.path.getsize(file_path)
        # Unused value is the encoding
        mime_type, _ = mimetypes.guess_type(file_path)

        if not mime_type:
            logging.exception(f"Could not determine MIME type for {file_path}")
            raise

        if mime_type.startswith("image/"):
            if not prompt:
                prompt = "Describe this image:"
            # 7MB limit
            max_size = 7 * 1024 * 1024
            if file_size > max_size:
                logging.error(
                    f"Image file {file_path} exceeds size limit ({file_size} > {max_size} bytes)."
                )
                raise
            try:
                file_content = open_image(file_path)

            except Exception as e:
                logging.exception(f"Error reading image file {file_path}: {e}")
                raise

        elif mime_type.startswith("audio/"):
            if not prompt:
                prompt = "Describe this audio clip:"
            # 20MB limit
            max_size = 20 * 1024 * 1024
            if file_size > max_size:
                logging.exception(
                    f"Audio file {file_path} exceeds size limit ({file_size} > {max_size} bytes)."
                )
                raise
            try:
                audio_clip_uploaded = self.upload_file(file_path)
                file_content = self.get_file(audio_clip_uploaded)
            except Exception as e:
                logging.exception(f"Error reading audio file {file_path}: {e}")
                raise

        elif mime_type.startswith("video/"):
            if not prompt:
                prompt = "Describe this video clip:"
            # 2GB limit
            max_size = 2 * 1024 * 1024 * 1024
            if file_size > max_size:
                logging.exception(
                    f"Video file {file_path} exceeds size limit ({file_size} > {max_size} bytes)."
                )
                raise
            # Upload video and get file object
            try:
                video_clip_uploaded = self.upload_file(file_path)
                file_content = self.get_file(video_clip_uploaded)

            except Exception as e:
                logging.exception(
                    f"Error uploading or processing video file {file_path}: {e}"
                )
                raise
        else:
            logging.exception(f"Unsupported file type: {mime_type}")
            raise

        # Gemini multimodal models
        # Need to fix it so models/ isn't required. Right now needed for scripts
        gemini_multimodal_models = [
            "models/gemini-1.5",
            "models/gemini-2.0",
            "models/gemini-2.5",
            "gemini-1.5",
            "gemini-2.0",
            "gemini-2.5",
        ]
        if any(
            self.language_model.startswith(model) for model in gemini_multimodal_models
        ):
            try:
                response = self.generate_content([prompt, file_content])
                return response
            except:
                logging.exception(f"Error generating content")
                raise
        else:
            logging.exception(
                f"The {self.language_model} doesn't support image, audio, or video processing."
            )
            raise
