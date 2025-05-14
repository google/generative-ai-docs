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
from typing import List
from absl import logging
from docs_agent.models.tools.base import Tools
from docs_agent.models.tools.mcp_client import MCPService
from docs_agent.utilities.config import MCPServerConfig


class ToolsFactory:
    """
    A factory class for creating tool service instances based on the specified type.
    """

    @staticmethod
    def create_tool_service(
        mcp_servers: list[MCPServerConfig],
        tool_service_type: str,
    ) -> List[Tools]:
        """
        Creates tool service instances based on the specified type and configurations.

        Args:
            mcp_servers: A list of MCPServerConfig objects.
            tool_service_type: The type of tool service to create ('mcp' is the only supported type).

        Returns:
            A list of Tools instances.

        Raises:
            ValueError: If an unsupported tool_service_type is provided.
        """
        tool_services: List[Tools] = []

        if not mcp_servers:
            logging.info(
                "No MCP servers defined in the configuration. No tool services created."
            )
            return tool_services

        if tool_service_type.lower() != "mcp":
            raise ValueError(
                f"Unsupported tool_service_type: '{tool_service_type}'. Only 'mcp' is currently supported."
            )

        logging.info(
            f"Creating MCPService instances for {len(mcp_servers)} configured server(s)..."
        )
        for mcp_server_config in mcp_servers:
            try:
                # Create an instance for each server config
                service_instance = MCPService(config=mcp_server_config)
                tool_services.append(service_instance)
                logging.info(
                    f"  Successfully created MCPService instance for server: {mcp_server_config}"
                )
            except Exception as e:
                logging.error(
                    f"Failed to instantiate MCPService for config {mcp_server_config}: {e}"
                )

        logging.info(f"Created {len(tool_services)} MCPService instance(s).")
        return tool_services
