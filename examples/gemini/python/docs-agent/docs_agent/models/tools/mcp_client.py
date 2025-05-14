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
import json
import logging
from typing import Any, Dict, List, Optional

import mcp
from docs_agent.utilities.config import MCPServerConfig
from mcp.client import stdio
from mcp.client import sse

from docs_agent.models.tools.base import Tools

class MCPService(Tools):
    """
    A service class that interacts with the MCP (Model Context Protocol) client.

    This class provides methods to list available tools and execute tool calls
    within an active MCP session.
    """

    def __init__(self, config: MCPServerConfig, verbose: bool = False):
        self.config = config
        self.name = config.name
        self.verbose = verbose
        self._client_context = None
        self.session: Optional[mcp.ClientSession] = None
        self._read = None
        self._write = None
        self._stdio_params: Optional[mcp.StdioServerParameters] = None

        # Prepare StdioServerParameters
        if self.config.server_type == "stdio":
            self._stdio_params = mcp.StdioServerParameters(
                command=self.config.command,
                args=self.config.args,
                env= self.config.env
            )
            logging.info(
                f"MCPService configured for STDIO connection: {self._stdio_params.command} {' '.join(self._stdio_params.args)}"
                f"{f' with env {self.config.env}' if self.config.env else ''}"
            )
        elif self.config.server_type == "sse":
            logging.info(f"MCPService configured for SSE connection: {self.config.url}")
        else:
            raise ValueError(
                f"Unsupported MCP server_type: {self.config.server_type}. Must be 'stdio' or 'sse'."
            )

    async def __aenter__(self):
        """
        Connects to the MCP server and initializes the client session.

        Returns:
            MCPService: The initialized MCPService instance.

        Raises:
            ValueError: If stdio_params are missing for stdio server type.
            ImportError: If required libraries for SSE client are missing.
        """
        server_type_upper = self.config.server_type.upper()
        logging.info(f"Attempting to connect through {server_type_upper}...")
        if self.config.server_type == "stdio":
            if not self._stdio_params:
                raise RuntimeError(
                    "Internal Error: Stdio parameters not initialized for stdio connection."
                )
            self._client_context = stdio.stdio_client(self._stdio_params)
        elif self.config.server_type == "sse":
            self._client_context = sse.sse_client(self.config.url)
        else:
            raise RuntimeError(
                f"Internal Error: Unexpected server type {self.config.server_type}"
            )

        try:
            # Enter the client context (stdio.stdio_client or sse.sse_client)
            self._read, self._write = await self._client_context.__aenter__()
            logging.info(f"MCP {server_type_upper} client connected successfully.")

            # Create and initialize the mcp.ClientSession
            self.session = mcp.ClientSession(self._read, self._write)
            await self.session.__aenter__()
            await self.session.initialize()
            logging.info("MCP Session initialized.")
        except Exception as e:
            logging.error(f"Failed to establish MCP connection or session: {e}")
            # Clean up context if connection failed partially
            if (
                self._client_context and self.session is None
            ):  # Connection started but session failed
                try:
                    await self._client_context.__aexit__(type(e), e, e.__traceback__)
                except Exception as cleanup_e:
                    logging.error(
                        f"Error during cleanup after connection failure: {cleanup_e}"
                    )
            self.session = None
            self._client_context = None
            self._read = None
            self._write = None
            raise  # Re-raise the original exception

        # Return the MCPService instance
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the MCP session and the client connection.

        Args:
            exc_type: The type of the exception that occurred, or None.
            exc_val: The value of the exception that occurred, or None.
            exc_tb: The traceback of the exception that occurred, or None.
        """
        logging.info("Closing MCP Session and Connection...")
        session_closed = False
        if self.session:
            try:
                await self.session.__aexit__(exc_type, exc_val, exc_tb)
                session_closed = True
                logging.info("MCP Session closed.")
            except Exception as e:
                logging.error(f"Error closing MCP session: {e}")
        else:
            logging.warning("No active MCP session to close.")

        if self._client_context:
            try:
                server_type_upper = self.config.server_type.upper()
                await self._client_context.__aexit__(exc_type, exc_val, exc_tb)
                logging.info(f"MCP {server_type_upper} client connection closed.")
            except Exception as e:
                logging.error(f"Error closing MCP client context: {e}")
        else:
            logging.warning("No active MCP client context to close.")

        # Reset state
        self.session = None
        self._client_context = None
        self._read = None
        self._write = None

    async def list_tools(self) -> List[Any]:
        """
        Lists the available tools in the MCP session.

        Returns:
            List[Any]: A list of tool objects from the MCP session.

        Raises:
            RuntimeError: If the MCP session is not active.
        """
        if not self.session:
            raise RuntimeError(
                "MCP session not active. Use 'async with MCPService(...):'"
            )
        logging.info("Listing tools from MCP session via MCPService...")
        mcp_tools = []
        try:
            mcp_tools_response = await self.session.list_tools()
            mcp_tools = mcp_tools_response.tools
            tool_count = len(mcp_tools) if hasattr(mcp_tools, "__len__") else "unknown"
            logging.info(f"Found {tool_count} tools.")
            if self.verbose and mcp_tools:
                print("\n--- MCP Tool Details ---")
                i = 0
                for tool in mcp_tools:
                    i += 1
                    print(f"Tool {i}/{tool_count}:")
                    tool_name = getattr(tool, "name", "N/A")
                    tool_desc = getattr(tool, "description", "N/A")
                    tool_schema = getattr(tool, "inputSchema", {})
                    print(f"  Name: {tool_name}")
                    print(f"  Description: {tool_desc}")
                    if tool_schema:
                        try:
                            print(
                                f"  Input Schema (Original):\n{json.dumps(dict(tool_schema), indent=4)}"
                            )
                        except Exception as schema_e:
                            print(
                                f"  Input Schema: (Error print: {schema_e}) Raw: {tool_schema}"
                            )
                    else:
                        print("  Input Schema: {}")
                    print("-" * 20)
                print("--- End MCP Tool Details ---\n")

        except Exception as e:
            logging.error(f"Error listing tools via MCPService: {e}")
            mcp_tools = []

        return mcp_tools

    async def execute_tool(self, func_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a tool call in the MCP session.

        Args:
            func_call (Dict[str, Any]): The function call dictionary from the model.

        Returns:
            Dict[str, Any]: A dictionary containing the tool's result or an error.
        """
        if not self.session:
            raise RuntimeError("MCP session not active.'")
        if not isinstance(func_call, dict) or not func_call.get("name"):
            logging.warning(f"Skipping invalid/empty function call dictionary: {func_call}")
            return {"error": "Invalid function call dictionary received."}

        tool_name = func_call["name"]
        args = func_call.get("args", {})

        logging.info(
            f'Calling MCP tool via MCPService: "{tool_name}" with args: {args}'
        )
        tool_response_content: Dict[str, Any]

        try:
            tool_result = await self.session.call_tool(tool_name, args)
            logging.info(f'MCP tool "{tool_name}" executed via MCPService.')
            is_error = getattr(tool_result, "isError", False)
            content_parts = getattr(tool_result, "content", [])
            result_text = None
            if content_parts and hasattr(content_parts[0], "text"):
                result_text = content_parts[0].text

            if is_error:
                error_msg = result_text if result_text else "Unknown tool error"
                logging.error(f'Tool "{tool_name}" returned an error: {error_msg}')
                tool_response_content = {"error": error_msg}
            elif result_text is not None:
                log_msg = (
                    f'Tool "{tool_name}" result: {result_text[:100]}'
                    f"{'...' if len(result_text) > 100 else ''}"
                )
                if self.verbose and len(result_text) > 100:
                    log_msg += f"\nFull result:\n{result_text}"
                logging.info(log_msg)
                tool_response_content = {"result": result_text}
            else:
                logging.warning(
                    f'Tool "{tool_name}" succeeded but returned no standard text content. Raw result: {tool_result}'
                )
                tool_response_content = {"result": ""}

        except Exception as e:
            logging.critical(
                f'!! Exception during MCP tool execution "{tool_name}" via MCPService: {type(e).__name__}: {e}'
            )
            if self.verbose:
                import traceback
                traceback.print_exc()
            tool_response_content = {
                "error": f"MCP Execution Failed: {type(e).__name__}: {e}"
            }

        return tool_response_content
