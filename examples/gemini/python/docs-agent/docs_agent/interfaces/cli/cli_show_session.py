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

"""Docs Agent CLI client"""

import click
import typing
from docs_agent.utilities import config

from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_common import show_config


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_show_session(ctx, config_file, product):
    """With Docs Agent, you can interact with Google's Gemini
    models and manage online corpora on Google Cloud."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


@cli_show_session.command(name="show-session")
@common_options
def show_session(config_file: typing.Optional[str] = None, product: list[str] = [""]):
    """Print the questions and responses being tracked in the current session."""
    # Set the filename for recording exchanges with the Gemini models.
    history_file = "/tmp/docs_agent_responses"
    with open(history_file, "r", encoding="utf-8") as target_file:
        context = target_file.read()
        target_file.close()
    print(context.strip() + "\n")


cli = click.CommandCollection(
    sources=[cli_show_session],
    help="With Docs Agent, you can interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()
