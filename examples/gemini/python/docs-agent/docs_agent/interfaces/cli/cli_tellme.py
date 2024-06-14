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
from docs_agent.utilities.config import ConfigFile
from docs_agent.utilities.config import return_config_and_product

from docs_agent.interfaces import run_console as console
from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_common import show_config
import time


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_tellme(ctx, config_file, product):
    """With Docs Agent, you can interact with Google's Gemini
    models and manage online corpora on Google Cloud."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


@cli_tellme.command(name="tellme")
@click.argument("words", nargs=-1)
@click.option(
    "--model",
    help="Specify a language model.",
    default=None,
    multiple=False,
)
@click.option(
    "--new",
    is_flag=True,
    help="Start a new session.",
)
@click.option(
    "--cont",
    is_flag=True,
    help="Use the previous responses in the session as context.",
)
@click.option(
    "--sleep",
    type=int,
    default=0,
    help="Sleep for a specified duration (in seconds) after completing the command.",
    hidden=True,
)
@common_options
def tellme(
    words,
    config_file: typing.Optional[str] = None,
    new: bool = False,
    cont: bool = False,
    sleep: int = 0,
    product: list[str] = [""],
    model: typing.Optional[str] = None,
):
    """Answer a question related to the product."""
    # Loads configurations from common options
    loaded_config, product_configs = return_config_and_product(
        config_file=config_file, product=product, model=model
    )
    if product == ():
        # Extracts the first product by default
        product_config = ConfigFile(products=[product_configs.products[0]])
    else:
        product_config = product_configs

    # Set the filename for recording exchanges with the Gemini models.
    history_file = "/tmp/docs_agent_responses"

    # Get the question string.
    question = ""
    for word in words:
        question += word + " "
    question = question.strip()

    # Ask the model and retrieve the response.
    this_output = console.ask_model(question, product_config, return_output=True)

    # If the `--new` flag is set, overwrite the history file.
    write_mode = "None"
    if new:
        write_mode = "w"
    elif cont:
        write_mode = "a"
    if write_mode != "None":
        # Record this exchange in the history file.
        with open(history_file, write_mode, encoding="utf-8") as out_file:
            out_file.write(f"QUESTION: {question}\n\n")
            out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
            out_file.close()

    # When the --sleep flag is provided, sleep for the specified duration.
    if sleep > 0:
        time.sleep(int(sleep))


cli = click.CommandCollection(
    sources=[cli_tellme],
    help="With Docs Agent, you can interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()
