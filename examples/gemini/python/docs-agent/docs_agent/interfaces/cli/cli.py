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

"""Docs Agent CLI wrapper"""

import click

from docs_agent.interfaces.cli.cli_admin import cli_admin
from docs_agent.interfaces.cli.cli_common import cli_common
from docs_agent.interfaces.cli.cli_runtask import cli_runtask
from docs_agent.interfaces.cli.cli_helpme import cli_helpme
from docs_agent.interfaces.cli.cli_tellme import cli_tellme
from docs_agent.interfaces.cli.cli_posix import cli_posix
from docs_agent.interfaces.cli.cli_show_session import cli_show_session


cli = click.CommandCollection(
    sources=[cli_common, cli_admin, cli_runtask, cli_helpme, cli_tellme, cli_posix, cli_show_session],
    help="With Docs Agent, you can populate vector databases, manage online corpora, and interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()
