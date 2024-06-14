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

from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_common import show_config

import subprocess
import os
import time


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_posix(ctx, config_file, product):
    """With Docs Agent, you can interact with Google's Gemini
    models and manage online corpora on Google Cloud."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


@cli_posix.command(name="posix")
@click.argument("words", nargs=-1)
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
def posix(
    words,
    config_file: typing.Optional[str] = None,
    new: bool = False,
    cont: bool = False,
    sleep: int = 0,
    product: list[str] = [""],
):
    """Run a POSIX command and add its output into context."""
    # Set the filename for recording exchanges with the Gemini models.
    history_file = "/tmp/docs_agent_responses"

    # Get the question string.
    command = ""
    for word in words:
        if word.startswith("~/"):
            word = os.path.expanduser(word)
        command += word + " "
    command = command.strip()

    print(f"Running a POSIX command: {command}")
    print()
    subprocess.run(command.split())
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    this_output = result.stdout.decode("utf-8")

    # If the `--new` flag is set, overwrite the history file.
    write_mode = "None"
    if new:
        write_mode = "w"
    elif cont:
        write_mode = "a"
    if write_mode != "None":
        # Record this exchange in the history file.
        with open(history_file, write_mode, encoding="utf-8") as out_file:
            out_file.write(f"POSIX COMMAND: {command}\n\n")
            out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
            out_file.close()

    # When the --sleep flag is provided, sleep for the specified duration.
    if sleep > 0:
        time.sleep(int(sleep))


cli = click.CommandCollection(
    sources=[cli_posix],
    help="With Docs Agent, you can interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()
