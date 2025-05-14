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
import abc
from typing import List, Dict, Any

class Tools(abc.ABC):
    """
    Abstract base class for tools.
    """

    @abc.abstractmethod
    async def list_tools(self) -> List[Any]:
        """
        Lists the tools available in the session.

        Returns:
            List[Any]: A list of tool objects, or an empty list if no tools
                       are found or an error occurs.
        """
        pass

    @abc.abstractmethod
    async def execute_tool(self, func_call: Any) -> Dict[str, Any]:
        """
        Executes a tool call.

        Args:
            func_call (Any): The function call object (e.g., from Gemini).

        Returns:
            Dict[str, Any]: A dictionary containing the tool's result or an error.
        """
        pass
