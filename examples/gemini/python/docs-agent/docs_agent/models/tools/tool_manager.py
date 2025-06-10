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
from typing import List, Dict, Any, Optional
import json
import contextlib
from absl import logging

from docs_agent.utilities.config import ProductConfig
from docs_agent.models.tools.base import Tools
from docs_agent.models.tools.tools import ToolsFactory
from docs_agent.models.base import GenerativeLanguageModel


class ToolManager:
    """
    Manages and orchestrates interactions with various tool services.

    This class handles the initialization, connection, and execution of tools
    from different tool services (e.g., MCP). It formats tool information for
    use with GenerativeLanguageModels and manages the multi-turn interaction
    loop, including tool execution and response processing.
    """
    def __init__(self, config: ProductConfig):
        self.config = config
        self.tool_services: List[Tools] = []
        if self.config.mcp_servers:
            try:
                self.tool_services = ToolsFactory.create_tool_service(
                    mcp_servers=self.config.mcp_servers,
                    tool_service_type="mcp",
                )
                logging.info(
                    f"ToolManager initialized with {len(self.tool_services)} tool service instance(s)."
                )
            except Exception as e:
                logging.error(f"ToolManager failed to initialize tool services: {e}")
                self.tool_services = []
        else:
            logging.info(
                "ToolManager initialized without any tool services configured."
            )

    def clean_openapi_schema(
        self, schema_data, keys_to_remove={"title", "default", "additionalProperties", "$schema"}
    ):
        """
        Recursively cleans an OpenAPI schema by removing specified keys and
        handling `anyOf` compositions. This is necessary because MCP returns
        schemas that are not always valid with Gemini models.

        Args:
            schema_data (dict or list): The OpenAPI schema data to clean.
            keys_to_remove (set): A set of keys to remove from the schema.

        Returns:
            dict or list: The cleaned schema data.
        """
        if isinstance(schema_data, dict):
            if "anyOf" in schema_data:
                any_of_list = schema_data.get("anyOf", [])
                chosen_schema = None
                for sub_schema in any_of_list:
                    if (
                        isinstance(sub_schema, dict)
                        and sub_schema.get("type") != "null"
                    ):
                        chosen_schema = sub_schema
                        break
                if chosen_schema is None and any_of_list:
                    chosen_schema = any_of_list[0]
                    if not isinstance(chosen_schema, dict):
                        logging.warning(
                            f"anyOf contained non-dict element, cannot determine type for: {schema_data}"
                        )
                        chosen_schema = None
                if chosen_schema:
                    new_schema = chosen_schema.copy()
                    for k, v in schema_data.items():
                        if k not in ["anyOf", *keys_to_remove]:
                            new_schema[k] = v
                    return self.clean_openapi_schema(new_schema, keys_to_remove)
                else:
                    logging.warning(
                        f'Could not extract valid type from "anyOf", creating minimal schema for: {schema_data}'
                    )
                    minimal_schema = {
                        k: v
                        for k, v in schema_data.items()
                        if k not in ["anyOf", *keys_to_remove]
                    }
                    if "type" not in minimal_schema:
                        minimal_schema["type"] = "string"
                        logging.warning(
                            f'--> Defaulting to type: "string" for problematic anyOf schema.'
                        )
                    return self.clean_openapi_schema(minimal_schema, keys_to_remove)

            cleaned_dict = {}
            for k, v in schema_data.items():
                if k not in keys_to_remove:
                    cleaned_dict[k] = self.clean_openapi_schema(v, keys_to_remove)

            if "properties" in cleaned_dict and "type" not in cleaned_dict:
                cleaned_dict["type"] = "object"
            if (
                cleaned_dict
                and "type" not in cleaned_dict
                and "properties" not in cleaned_dict
                and "items" not in cleaned_dict
            ):
                potential_type_indicators = {"format", "enum"}
                if any(key in cleaned_dict for key in potential_type_indicators):
                    logging.warning(
                        f'Cleaned schema seems to be missing "type", defaulting to "string": {cleaned_dict}'
                    )
                    cleaned_dict["type"] = "string"
            return cleaned_dict
        elif isinstance(schema_data, list):
            return [
                self.clean_openapi_schema(item, keys_to_remove) for item in schema_data
            ]
        else:
            return schema_data

    def format_tools_for_model(
        self, raw_tools: List[Any], verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Formats a list of raw tool objects (e.g., from MCP) into a generic list
        of dictionaries suitable for the GenerativeLanguageModel interface.

        Args:
            raw_tools (List[Any]): A list of raw tool objects from a tool service.
            verbose (bool): Enable verbose logging during formatting.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a
                                  tool's function declaration.
        """
        generic_tools: List[Dict[str, Any]] = []
        if not raw_tools:
            logging.info("No raw tools provided for formatting.")
            return generic_tools

        logging.info("Attempting to format raw tools into generic model format...")
        skipped_count = 0
        for tool in raw_tools:
            tool_name = getattr(tool, "name", None)
            tool_desc = getattr(tool, "description", None)
            # Check for essential attributes before proceeding
            if not (tool_name and tool_desc and hasattr(tool, "inputSchema")):
                logging.warning(
                    f"Skipping tool \"{tool_name or 'Unnamed'}\" due to missing required attributes (name, description, or inputSchema)."
                )
                skipped_count += 1
                continue

            original_schema = getattr(tool, "inputSchema", {})
            cleaned_schema = {}
            try:
                # Ensure we have a dict to clean
                schema_dict_to_clean = (
                    dict(original_schema)
                    if not isinstance(original_schema, dict)
                    else original_schema
                )
                cleaned_schema = self.clean_openapi_schema(schema_dict_to_clean)
                if not isinstance(cleaned_schema, dict):
                    logging.warning(
                        f'Schema cleaning for tool "{tool_name}" did not result in a dictionary. Attempting to use original schema as dict.'
                    )
                    # Fallback attempt
                    cleaned_schema = (
                        dict(original_schema)
                        if not isinstance(original_schema, dict)
                        else original_schema
                    )
                    if not isinstance(cleaned_schema, dict):
                        raise TypeError(
                            "Cleaned schema and original schema could not be represented as a dictionary."
                        )

            except Exception as clean_e:
                logging.warning(
                    f'Could not clean schema for tool "{tool_name}": {clean_e}. Trying original schema as dict.'
                )
                try:
                    # Ensure the fallback is also a dict
                    cleaned_schema = (
                        dict(original_schema)
                        if not isinstance(original_schema, dict)
                        else original_schema
                    )
                    if not isinstance(cleaned_schema, dict):
                        raise TypeError(
                            "Original schema could not be represented as a dictionary."
                        )
                except Exception as fallback_e:
                    logging.error(
                        f'Could not use original or cleaned schema for "{tool_name}": {fallback_e}. Skipping tool.'
                    )
                    skipped_count += 1
                    continue
            generic_tool_dict = {
                "name": tool_name,
                "description": tool_desc,
                "parameters": cleaned_schema,
            }
            generic_tools.append(generic_tool_dict)

            if verbose:
                try:
                    logging.info(
                        f"  Formatted tool '{tool_name}': description='{tool_desc[:50]}...', schema={json.dumps(cleaned_schema, indent=2)}"
                    )
                except Exception as log_e:
                    logging.info(
                        f"  Formatted tool '{tool_name}' (logging schema failed: {log_e})"
                    )

        valid_tool_count = len(generic_tools)
        logging.info(
            f"Formatted {valid_tool_count} tools into generic structure (skipped {skipped_count})."
        )

        return generic_tools

    async def _execute_tool_calls(
        self, function_calls: List[Any], tool_to_service_map: typing.Dict[str, Tools]
    ) -> List[Dict[str, Any]]:
        """
        Executes a list of function calls (tool calls) using the appropriate tool services.

        Args:
            function_calls (List[Any]): A list of function call objects.
            tool_to_service_map (typing.Dict[str, Tools]): A dictionary mapping tool names to their
                corresponding service instances.

        Returns:
            List[Dict[str, Any]]: A list of function response parts (as dicts).
        """
        function_response_parts_list: List[Dict[str, Any]] = []
        logging.info(f"Executing {len(function_calls)} tool call(s).")

        for func_call in function_calls:
            tool_name = func_call.get("name", "unknown_tool")
            # Find the correct service instance from the map
            target_service = tool_to_service_map.get(tool_name)

            if not target_service:
                logging.error(
                    f"Could not find active tool service for tool '{tool_name}'. Skipping call."
                )
                # Optionally return an error part for the model
                error_response = {
                    "error": f"Tool '{tool_name}' not found in active sessions."
                }
                function_response_parts_list.append(
                     {
                        "function_response": {
                            "name": tool_name,
                            "response": error_response,
                        }
                    }
                )
                continue

            # Call execute_tool on the found Tools instance
            tool_response_content = await target_service.execute_tool(func_call)
            function_response_parts_list.append(
                {
                    "function_response": {
                        "name": tool_name,
                        "response": tool_response_content,
                    }
                }
            )
        return function_response_parts_list

    def _extract_final_text_from_history(self, contents: List[Dict[str, Any]]) -> str:
        """
        Extracts the final text response from the conversation history (list of dicts).

        Args:
            contents (List[Dict[str, Any]]): A list of conversation content dictionaries.

        Returns:
            str: The final text response, or an error message if not found.
        """
        final_text = ""
        try:
            last_model_response_content = None
            # Find the last "model" content object in the history
            for item in reversed(contents):
                if isinstance(item, dict) and item.get("role") == "model":
                    last_model_response_content = item
                    break

            if last_model_response_content is not None:
                parts = last_model_response_content.get("parts", [])
                if parts:
                    for part in parts:
                        # Check if part is a dict and has text, but not function_call
                        if isinstance(part, dict):
                           text = part.get("text")
                           is_function_call = "function_call" in part
                           if text and not is_function_call:
                               final_text += text
                    if not final_text:
                        logging.info(
                            "Last model response found but contained no text parts."
                        )
                else:
                    logging.info("Last model response found in history had no parts.")
            else:
                logging.info('No "model" role content found in the final history.')

        except Exception as e:
            logging.error(
                f"Error extracting final text from history: {type(e).__name__}: {e}"
            )
            return "[ERR Extracting text from history]"
        return final_text

    def _extract_final_response_text(
        self, contents: List[Dict[str, Any]], last_response: Optional[Dict[str, Any]]
    ) -> str:
        """
        Extracts the final text response from the conversation history or the last API response.

        Args:
            contents (List[Dict[str, Any]]): A list of conversation content dictionaries.
            last_response (Optional[Dict[str, Any]]): The last API response object (as dict)

        Returns:
            str: The final text response, or an error message if not found.
        """
        # 1. Try extracting from history first
        final_text = self._extract_final_text_from_history(contents)

        # 2. Fallback using the very last API response if history extraction failed/empty
        if not final_text or final_text.startswith("[ERR"):
            logging.info(
                "No text found in last model history item, trying last API response."
            )
            fallback_text = ""
            try:
                # Check the dictionary structure of last_response
                if last_response and isinstance(last_response, dict):
                    # Attempt to find text parts in the last response dict
                    response_parts = last_response.get("parts", [])
                    if isinstance(response_parts, list):
                        for part in response_parts:
                            if isinstance(part, dict):
                                text = part.get("text")
                                is_function_call = "function_call" in part
                                if text and not is_function_call:
                                    fallback_text += text
                                    logging.info(
                                        "(Fallback text extracted from last API response parts)"
                                    )
                                    break
            except Exception as e:
                logging.error(f"Error during fallback text extraction: {e}")

            if fallback_text:
                final_text = fallback_text
            elif not final_text or final_text.startswith("[ERR"):
                 final_text = "[Agent loop finished. No final text content found.]"
                 logging.warning("No final text found in history or last response.")

        return final_text

    async def _setup_tool_services(
        self, stack: contextlib.AsyncExitStack
    ) -> tuple[List[Tools], Dict[str, Tools], List[Any]]:
        """
        Sets up connections to all configured tool services, retrieves their tools,
        and creates a mapping for tool name to service instance.

        Args:
            stack (contextlib.AsyncExitStack): An async exit stack for managing
                the tool service connections.

        Returns:
            tuple[List[Tools], Dict[str, Tools], List[Any]]: A tuple containing:
                - A list of active tool service instances.
                - A dictionary mapping tool names to their corresponding service instances.
                - A list of all raw tools retrieved from all services.
        """
        active_services: List[Tools] = []
        tool_to_service_map: Dict[str, Tools] = {}
        all_raw_tools: List[Any] = []

        logging.info(
            f"Attempting to connect to {len(self.tool_services)} tool service(s)..."
        )
        # Enter context for each service
        for service in self.tool_services:
            try:
                active_service_context = await stack.enter_async_context(service)
                active_services.append(active_service_context)
                service_config_repr = getattr(
                    service, "config", f"Instance of {type(service).__name__}"
                )
                logging.info(
                    f"Successfully connected to tool service: {service_config_repr}"
                )

                mcp_tools = await active_service_context.list_tools()
                all_raw_tools.extend(mcp_tools)

                for tool in mcp_tools:
                    tool_name = getattr(tool, "name", None)
                    if tool_name:
                        if tool_name in tool_to_service_map:
                            logging.warning(
                                f"Duplicate tool name '{tool_name}' found across services. Using the one from {service_config_repr}."
                            )
                        tool_to_service_map[tool_name] = active_service_context
                    else:
                        logging.warning(
                            f"Found a tool without a name from service {service_config_repr}. Skipping."
                        )

            except Exception as e:
                service_config_repr = getattr(
                    service, "config", f"Instance of {type(service).__name__}"
                )
                logging.error(
                    f"Failed to connect or list tools for service {service_config_repr}: {e}"
                )

        return active_services, tool_to_service_map, all_raw_tools

    async def _run_tool_interaction_loop(
        self,
        language_model: GenerativeLanguageModel,
        initial_contents: List[Dict[str, Any]],
        formatted_tools: List[Dict[str, Any]],
        tool_to_service_map: Dict[str, Tools],
        verbose: bool = False,
        max_tool_turns: int = 5,
    ) -> tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        contents = list(initial_contents)
        last_response: Optional[Dict[str, Any]] = None

        logging.info("\n--- Turn 0: Initial Request ---")
        logging.info(
            f"Sending prompt {'with aggregated tools' if formatted_tools else '(no tools found/formatted)'} to model {language_model}..."
        )
        try:
            # Expecting generate_content_async to return a dictionary now
            response_dict = await language_model.generate_content_async(
                contents=contents[:1],
                tools=formatted_tools,
            )
            last_response = response_dict
        except Exception as e:
            logging.error(f"Initial LLM interaction failed: {type(e).__name__}: {e}")
            # Attempt to extract error from response if it's a dict
            if isinstance(last_response, dict) and last_response.get("error"):
                 raise RuntimeError(f"ERR: {last_response.get('error')}") from e
            raise

        # --- Process Initial Response ---
        if not isinstance(last_response, dict):
             logging.error(f"Invalid model response type received: {type(last_response)}. Expected dict.")
             raise RuntimeError("ERR: Invalid response format from model.")
        logging.info(f"Received initial response dict: {json.dumps(last_response, indent=2)}")
        # Check for errors or blocking indicated in the response dict (implementation specific)
        if last_response.get("error"):
             logging.error(f"Model response indicates error: {last_response['error']}")
             raise RuntimeError(f"ERR: {last_response['error']}")
        if last_response.get("blocked"):
             reason = last_response.get("block_reason", "Unknown")
             logging.error(f"Model response blocked. Reason: {reason}")
             raise RuntimeError(f"ERR: Response blocked ({reason})")

        initial_model_content_dict = last_response
        current_function_calls = []
        try:
            # Add the model's response dictionary to the history
            contents.append(initial_model_content_dict)

            response_parts = initial_model_content_dict.get("parts", [])
            if isinstance(response_parts, list):
                 current_function_calls = [
                     part["function_call"]
                     for part in response_parts
                     if isinstance(part, dict) and "function_call" in part
                 ]
                 logging.info(f"Extracted initial function calls: {current_function_calls}")
                 has_text = any(
                     isinstance(part, dict) and "text" in part and part["text"]
                     for part in response_parts
                 )
                 response_summary = (
                     "[Function Call]"
                     if current_function_calls
                     else "[Text]"
                     if has_text
                     else "[Empty Parts]"
                 )
                 logging.info(f"Model initial response: {response_summary}")
                 if verbose:
                     logging.info(
                         f"Model initial response (dict): {json.dumps(initial_model_content_dict, indent=2)}"
                     )
            else:
                 logging.warning("Initial model response content dict has no 'parts' list.")
                 # Ensure history has a model entry even if parts are missing/invalid
                 if contents[-1] != initial_model_content_dict:
                     contents.append({"role": "model", "parts": []})

        except (KeyError, TypeError) as e:
            logging.error(f"Error parsing initial response dictionary: {e}")
            if verbose and last_response:
                 try:
                     logging.info(f"Response structure issue. Raw response dict: {json.dumps(last_response, indent=2)}")
                 except Exception: pass
            raise RuntimeError("ERR: Parse initial response dict.") from e

        # --- Tool Calling Loop ---
        turn_count = 0
        while current_function_calls and turn_count < max_tool_turns:
            turn_count += 1
            logging.info(f"\n--- Turn {turn_count}: Tool Execution ---")

            function_response_parts_list = await self._execute_tool_calls(
                current_function_calls, tool_to_service_map
            )

            if function_response_parts_list:
                contents.append(
                    {"role": "function", "parts": function_response_parts_list}
                )
                logging.info(
                    f"Added {len(function_response_parts_list)} tool response(s) to history."
                )
            else:
                logging.warning("No tool calls successfully processed in this turn.")
                break

            logging.info("Requesting next step from Model...")
            try:
                # Expecting a dictionary response again
                response_dict = await language_model.generate_content_async(
                    contents=contents, # Send full history (list of dicts)
                    tools=formatted_tools,
                )
                last_response = response_dict
                logging.info(f"Received subsequent response dict: {json.dumps(last_response, indent=2)}")
            except Exception as e:
                logging.error(
                    f"Subsequent model API call failed: {type(e).__name__}: {e}"
                )
                # Attempt to extract error from response if it's a dict
                if isinstance(last_response, dict) and last_response.get("error"):
                     raise RuntimeError(f"ERR: {last_response.get('error')}") from e
                raise RuntimeError(f"ERR: Subsequent API call: {e}") from e

            # --- Process Subsequent Response (as dict) ---
            if not isinstance(last_response, dict):
                 logging.error(f"Invalid model response type after tool use: {type(last_response)}. Expected dict.")
                 raise RuntimeError("ERR: Invalid response format from model after tool use.")

            # Check for errors or blocking
            if last_response.get("error"):
                 logging.error(f"Model response indicates error: {last_response['error']}")
                 raise RuntimeError(f"ERR: {last_response['error']}")
            if last_response.get("blocked"):
                 reason = last_response.get("block_reason", "Unknown")
                 logging.error(f"Model response blocked after tool use. Reason: {reason}")
                 break

            model_content_dict = last_response
            current_function_calls = []

            try:
                # Add the model's response dictionary to the history
                contents.append(model_content_dict)

                response_parts = model_content_dict.get("parts", [])
                if isinstance(response_parts, list):
                    current_function_calls = [
                        part["function_call"]
                        for part in response_parts
                        if isinstance(part, dict) and "function_call" in part
                    ]
                    logging.info(f"Extracted subsequent function calls: {current_function_calls}")
                    has_text = any(
                        isinstance(part, dict) and "text" in part and part["text"]
                        for part in response_parts
                    )
                    response_summary = (
                        "[Function Call]"
                        if current_function_calls
                        else "[Text]"
                        if has_text
                        else "[Empty Parts]"
                    )
                    logging.info(f"Model response: {response_summary}")
                    if verbose:
                        logging.info(f"Model response (dict): {json.dumps(model_content_dict, indent=2)}")

                    # If the response is just text or empty, the loop will naturally end
                    if not current_function_calls:
                        logging.info("Model response contains text or is empty, ending tool loop.")
                        break

                else:
                    logging.warning("Model response dict has no 'parts' list after tool use.")
                    # Ensure history has a model entry
                    if contents[-1] != model_content_dict:
                        contents.append({"role": "model", "parts": []})
                    break

            except (KeyError, TypeError) as e:
                logging.error(f"Error parsing subsequent response dictionary: {e}")
                if verbose and last_response:
                    try:
                        logging.info(f"Response structure issue. Raw response dict: {json.dumps(last_response, indent=2)}")
                    except Exception: pass
                break

        # --- End Loop ---
        if turn_count >= max_tool_turns and current_function_calls:
            logging.warning(f"Max tool turns ({max_tool_turns}) reached.")
        elif not current_function_calls:
            logging.info("Model finished generating or no further tool calls needed.")

        return contents, last_response

    async def process_prompt_with_tools(
        self,
        prompt: str,
        language_model: GenerativeLanguageModel,
        verbose: bool = False,
    ):
        """
        Processes a user prompt using available tools and a language model.

        This method orchestrates the interaction between the language model and
        tool services, managing the multi-turn conversation loop and tool
        execution.

        Args:
            prompt (str): The user's input prompt.
            language_model (GenerativeLanguageModel): The language model instance
                to use.
            verbose (bool): Enable verbose logging.

        Returns:
            str: The final text response from the model, or an error message.
        """
        if not self.tool_services:
            logging.warning(
                "ToolManager.process_prompt_with_tools called, but no tool services are initialized."
            )
            # Fallback to simple generation if desired, or raise error
            try:
                 response = await language_model.generate_content_async(
                     contents=[{"role": "user", "parts": [{"text": prompt}]}],
                     tools=None,
                 )
                 # Extract text from the expected dictionary response
                 final_text = "[ERR: Failed to get text from fallback]"
                 if isinstance(response, dict):
                     parts = response.get("parts", [])
                     if isinstance(parts, list):
                         for part in parts:
                             if isinstance(part, dict) and "text" in part:
                                 final_text = part["text"]
                                 break
                 return final_text
            except Exception as e:
                 logging.error(f"LLM interaction failed (no tools): {type(e).__name__}: {e}")
                 return f"Error: Failed to generate content: {e}"

        final_text: Optional[str] = None
        contents: List[Dict[str, Any]] = [{"role": "user", "parts": [{"text": prompt}]}]
        last_response: Optional[Dict[str, Any]] = None

        async with contextlib.AsyncExitStack() as stack:
            try:
                (
                    active_services,
                    tool_to_service_map,
                    all_raw_tools,
                ) = await self._setup_tool_services(stack)

                if not active_services:
                    logging.error("Failed to establish connection with any tool service.")
                    # Set error text directly if connection fails
                    final_text = "[ERR: Failed to connect to any tool service]"
                else:
                    # Proceed only if services are active
                    formatted_tools = self.format_tools_for_model(all_raw_tools, verbose)

                    logging.info("--- Starting Loop (within ToolManager) ---")
                    # Run the loop
                    contents, last_response = await self._run_tool_interaction_loop(
                        language_model=language_model,
                        initial_contents=contents,
                        formatted_tools=formatted_tools,
                        tool_to_service_map=tool_to_service_map,
                        verbose=verbose,
                    )
                    logging.info("\n--- Finished loop (within ToolManager) ---")

            except Exception as e:
                logging.error(
                    f"Error during tool processing in ToolManager: {type(e).__name__}: {e}"
                )
                # Set final_text only if an exception occurs
                final_text = f"[ERR: {type(e).__name__} - {e}]"
                if isinstance(last_response, dict) and last_response.get("error"):
                    final_text = f"[ERR: {last_response.get('error')}]"

            # Extract final text only if no error was explicitly set during try/except
            if final_text is None:
                 if last_response is not None or contents:
                     # Call extraction method if loop completed successfully
                     final_text = self._extract_final_response_text(contents, last_response)
                 else:
                     final_text = "[ERR: No response or history available after loop]"

        # Ensure we always return a string
        return final_text if final_text is not None else "[ERR: Unknown processing state]"
