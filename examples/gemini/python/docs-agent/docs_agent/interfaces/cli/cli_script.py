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
from pathlib import Path
import os
import subprocess
import time

from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_common import show_config
from docs_agent.utilities import helpers  # Import the helpers module


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_script(ctx, config_file, product):
    """With Docs Agent, you can interact with Google's Gemini
    models and manage online corpora on Google Cloud."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


@cli_script.command(name="script")
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
def script(
    words,
    config_file: typing.Optional[str] = None,
    new: bool = False,
    cont: bool = False,
    sleep: int = 0,
    product: list[str] = [""],
):
    """Run a script from the project root and add its output into context."""
    # Set the filename for recording exchanges with the Gemini models.
    history_file = "/tmp/docs_agent_responses"

    # Get the project root path using the helper function
    try:
        project_path = helpers.get_project_path()
    except FileNotFoundError as e:
         click.echo(f"Error: Could not find project root. {e}", err=True)
         return

    # Extract the script name and its arguments
    if not words:
        click.echo("Error: No script name provided.", err=True)
        return

    script_name = words[0]

    # Get the Current Working Directory where the command was invoked
    # This is used especially for things like custom_input
    original_cwd = Path.cwd()

    script_arguments_for_subprocess = []
    for arg in words[1:]:
        # Expand ~ if present
        if arg.startswith("~/"):
            expanded_arg = os.path.expanduser(arg)
            script_arguments_for_subprocess.append(expanded_arg)
        else:
            # Resolve the argument path relative to the original working directory
            absolute_arg_path = original_cwd.resolve() / arg
            # Passes absolute path to the subprocess
            script_arguments_for_subprocess.append(str(absolute_arg_path.resolve()))

    # The script path itself should be relative to the project root
    # This defines scripts/
    script_path_relative_to_project = Path("scripts") / script_name

    command = ["python3", str(script_path_relative_to_project)] + script_arguments_for_subprocess

    print("Running script from project root:")
    print(f"  Command: {' '.join(command)}\n")

    try:
        # Execute the script with current working directory set to the project root
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=project_path
        )
        this_output = process.stdout
        if process.stderr:
            click.echo("Script produced warnings/errors on stderr:\n", err=True)
            click.echo(process.stderr, err=True)

    # Catch all errors and print them to the click console
    except FileNotFoundError:
        click.echo(
            f"Error: 'python3' command not found or script '{script_path_relative_to_project}' not found within '{project_path}'.",
            err=True,
        )
        return
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: Script execution failed with exit code {e.returncode}", err=True)
        click.echo(f"Stderr:\n{e.stderr}", err=True)
        click.echo(f"Stdout:\n{e.stdout}", err=True)
        return
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
        return

    write_mode = "None"
    if new:
        write_mode = "w"
    elif cont:
        write_mode = "a"
    if write_mode != "None":
        try:
            with open(history_file, write_mode, encoding="utf-8") as out_file:
                # Enhanced the logging by adding the script name and arguments
                out_file.write(f"SCRIPT (run in {project_path}): {' '.join(command)}\n\n")
                out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
        except IOError as e:
            click.echo(f"Error writing to history file '{history_file}': {e}", err=True)

    if sleep > 0:
        time.sleep(int(sleep))


cli = click.CommandCollection(
    sources=[cli_script],
    help="With Docs Agent, you can interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()