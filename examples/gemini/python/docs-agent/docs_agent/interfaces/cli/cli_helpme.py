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
from docs_agent.utilities.config import return_config_and_product, get_project_path
from docs_agent.utilities.helpers import resolve_path

from docs_agent.interfaces import run_console as console
from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_common import show_config
import os
import string
import re
import time
import subprocess
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.style import Style


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_helpme(ctx, config_file, product):
    """With Docs Agent, you can interact with Google's Gemini
    models and manage online corpora on Google Cloud."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


@cli_helpme.command()
@click.argument("words", nargs=-1)
@click.option(
    "--model",
    help="Specify a language model.",
    default=None,
    multiple=False,
)
@click.option(
    "--file",
    type=click.Path(),
    help="Specify a file to be included as context.",
)
@click.option(
    "--perfile",
    type=click.Path(),
    help="Specify a path where the request will be applied to each file in the directory.",
)
@click.option(
    "--allfiles",
    type=click.Path(),
    help="Specify a path where all files in the directory are used as context.",
)
@click.option(
    "--file_ext",
    help="Works with --perfile and --dir. Specify the file type to be selected. The default is set to use all files.",
)
@click.option(
    "--yaml",
    is_flag=True,
    help="Store the output to responses.yaml.",
)
@click.option(
    "--rag",
    is_flag=True,
    help="Add entries retrieved from the knowledge database as context.",
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
    "--terminal",
    is_flag=True,
    help="Use the terminal output as context. (This option requires a special setup in the terminal.)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Do not ask the user to confirm interactively.",
)
@click.option(
    "--check",
    is_flag=True,
    help="Print the current prompt for testing.",
    hidden=True,
)
@click.option(
    "--sleep",
    type=int,
    default=0,
    help="Sleep for a specified duration (in seconds) after completing the command.",
    hidden=True,
)
@click.option(
    "--out",
    type=click.Path(),
    help="Specify an output file for saving the response. By default, the file is saved in the project's `agent_out/` directory. Use an absolute path if you want to save the file in a directory outside your current project.",
)
@click.option(
    "--panel",
    is_flag=True,
    help="Use a panel for rendering the response.",
)
@click.option(
    "--response_type",
    type=click.Choice(["text", "json", "x.enum"]),
    default="text",
    help="Specify the response type of the response from the model. When using json, you can specify the JSON schema at the end of your question.",
)
@click.option(
    "--response_schema",
    help="Specify a response schema for the response type.",
    hidden=True,
)
@common_options
def helpme(
    words,
    config_file: typing.Optional[str] = None,
    file: typing.Optional[str] = None,
    perfile: typing.Optional[str] = None,
    allfiles: typing.Optional[str] = None,
    file_ext: typing.Optional[str] = None,
    yaml: bool = False,
    out: typing.Optional[str] = None,
    rag: bool = False,
    new: bool = False,
    cont: bool = False,
    terminal: bool = False,
    force: bool = False,
    check: bool = False,
    sleep: int = 0,
    panel: bool = False,
    product: list[str] = [""],
    response_type: typing.Optional[str] = "text",
    response_schema: typing.Optional[str] = None,
    model: typing.Optional[str] = None,
):
    """Ask an AI language model to perform a task from the terminal."""
    # Initialize Rich console
    ai_console = Console(width=120)
    console_style = Style(color="cyan", bold=False)
    use_panel = False
    if panel:
        use_panel = True
    # Loads configurations from common options
    loaded_config, product_configs = return_config_and_product(
        config_file=config_file, product=product, model=model
    )
    if product == ():
        # Extracts the first product by default
        product_config = ConfigFile(products=[product_configs.products[0]])
    else:
        product_config = product_configs

    # Get the language model.
    this_model = product_config.products[0].models.language_model
    # This feature is only available to the Gemini Pro models (not AQA).
    if not this_model.startswith("models/gemini"):
        click.echo(f"File mode is not supported with this model: {this_model}")
        exit(1)
    # This feature is only available to the Gemini 1.5 models.
    if not this_model.startswith("models/gemini-1.5") and response_type != "text":
        click.echo(f"x.enum and json only work on gemini-1.5 models. You are using: {this_model}")
        exit(1)
    if response_type == "x.enum" and response_schema is None:
         click.echo(f"You must specify a response_schema when using text/x.enum. Optional for json.")
         exit(1)
    if response_type:
        product_config.products[0].models.response_type = response_type
    # Get the question string.
    question = ""
    for word in words:
        question += word + " "
    question = question.strip()
    if response_schema:
        product_config.products[0].models.response_schema = response_schema
    # This is wrapped around the question when --out flag is set, this will
    # help format the output of the final file.
    question_out_wrapper = (
        f"The answer that you provide to the question below will be saved to a file "
        + f"named {out}. Your response must only include what will go in this file. "
        + f"Do your best to ensure that you provide a response that matches the format "
        + f"of this file extension. For example .md indicates a Markdown file, .py "
        + f"a Python file, and so on. Markdown files must always be in valid Markdown "
        + f"format and begin with the # header (for instance, # <PAGE TITLE>).\n\n"
    )
    # Set output path to the agent_out directory.
    if out is not None and out != "" and out != "None":
        if out.startswith("~/"):
            out = os.path.expanduser(out)
        if out.startswith("/"):
            base_out = os.path.dirname(out)
            out = Path(out).name
        # This includes paths like out.startswith("~")
        else:
            base_out = os.path.join(get_project_path(), "agent_out")
        # Creates the output directory if it can't write, it will try home directory.
        try:
            os.makedirs(base_out, exist_ok=True)
        except:
            base_out = os.path.expanduser("~/docs_agent")
            base_out = os.path.join(base_out, "agent_out")
            try:
                os.makedirs(base_out, exist_ok=True)
            except:
                base_out = os.path.join("/tmp/docs_agent", "agent_out")
                try:
                    os.makedirs(base_out, exist_ok=True)
                except:
                    print(f"Failed to create the output directory: {base_out}")
                    exit(1)
        if base_out.endswith("/"):
            base_out = base_out[:-1]
        out = base_out + "/" + out

    # Print the prompt for testing.
    if check:
        print(f"Prompt: {question}")
        exit(0)

    # Set the filename for recording exchanges with the Gemini models.
    history_file = "/tmp/docs_agent_responses"

    # Different modes: Terminal output, Single file, Per file, All files,
    # Previous exchanges, and No flags.
    helpme_mode = ""
    if perfile and perfile != "None":
        helpme_mode = "PER_FILE"
    elif allfiles and allfiles != "None":
        helpme_mode = "ALL_FILES"
    elif file and file != "None":
        helpme_mode = "SINGLE_FILE"
    elif cont:
        helpme_mode = "PREVIOUS_EXCHANGES"
    elif terminal:
        helpme_mode = "TERMINAL_OUTPUT"
    else:
        helpme_mode = "NO_FLAGS"

    # Select the mode.
    if helpme_mode == "PREVIOUS_EXCHANGES":
        if out is not None and out != "" and out != "None":
            question = question_out_wrapper + question
        # Continue mode, which uses the previous exchangs as the main context.
        this_output = console.ask_model_with_file(
            question.strip(),
            product_config,
            context_file=history_file,
            rag=rag,
            return_output=True,
        )

        # Render the response.
        if use_panel:
            ai_console.print("[Response]", style=console_style)
            ai_console.print(Panel(Markdown(this_output, code_theme="manni")))
        else:
            print()
            print(f"{this_output}")
            print()

        # Save the response as context.
        with open(history_file, "a", encoding="utf-8") as out_file:
            out_file.write(f"QUESTION: {question}\n\n")
            out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
            out_file.close()

        # Save this exchange in a YAML file.
        if yaml is True:
            output_filename = "./responses.yaml"
            # Prepare output to be saved in the YAML file.
            yaml_buffer = (
                f"  - question: {question}\n" + f"    response: {this_output}\n"
            )
            with open(output_filename, "w", encoding="utf-8") as yaml_file:
                yaml_file.write("logs:\n")
                yaml_file.write(yaml_buffer)
                yaml_file.close()

        # Save the response to the `out` file.
        if out is not None and out != "" and out != "None":
            try:
                with open(out, "w", encoding="utf-8") as out_file:
                    out_file.write(f"{this_output}\n")
                    out_file.close()
            except:
                print(f"Failed to write the output to file: {out}")

    elif helpme_mode == "SINGLE_FILE":
        if out is not None and out != "" and out != "None":
            question = question_out_wrapper + question
        # Single file mode.
        if file.startswith("~/"):
            file = os.path.expanduser(file)
        this_file = os.path.realpath(os.path.join(os.getcwd(), file))
        this_output = ""

        # if the `--cont` flag is set, inlcude the previous exchanges as additional context.
        context_file = None
        if cont:
            context_file = history_file

        this_output = console.ask_model_with_file(
            question.strip(),
            product_config,
            file=this_file,
            context_file=context_file,
            rag=rag,
            return_output=True,
        )

        # Render the response.
        if use_panel:
            ai_console.print("[Response]", style=console_style)
            ai_console.print(Panel(Markdown(this_output, code_theme="manni")))
        else:
            print()
            print(f"{this_output}")
            print()

        # Read the file content to be included in the history file.
        file_content = ""
        if (
            this_file.endswith(".png")
            or this_file.endswith(".jpg")
            or this_file.endswith(".gif")
        ):
            file_content = "This is an image file.\n"
        elif (
            this_file.endswith(".mp3")
            or this_file.endswith(".wav")
            or this_file.endswith(".ogg")
            or this_file.endswith(".flac")
            or this_file.endswith(".aac")
            or this_file.endswith(".aiff")
            or this_file.endswith(".mp4")
            or this_file.endswith(".mov")
            or this_file.endswith(".avi")
            or this_file.endswith(".x-flv")
            or this_file.endswith(".mpg")
            or this_file.endswith(".webm")
            or this_file.endswith(".wmv")
            or this_file.endswith(".3gpp")
        ):
            file_content = "This is an audio file.\n"
        else:
            try:
                with open(this_file, "r", encoding="utf-8") as target_file:
                    file_content = target_file.read()
                    target_file.close()
            except:
                print(f"[Error] This file cannot be opened: {this_file}\n")
                exit(1)

        # If the `--new` flag is set, overwrite the history file.
        write_mode = "a"
        if new:
            write_mode = "w"
        # Record this exchange in the history file.
        with open(history_file, write_mode, encoding="utf-8") as out_file:
            out_file.write(f"QUESTION: {question}\n\n")
            out_file.write(f"FILE NAME: {file}\n")
            out_file.write(f"FILE CONTENT:\n\n{file_content}\n")
            out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
            out_file.close()

        # Save this exchange in a YAML file.
        if yaml is True:
            output_filename = "./responses.yaml"
            # Prepare output to be saved in the YAML file.
            yaml_buffer = (
                f"  - question: {question}\n"
                + f"    response: {this_output}\n"
                + f"    file: {this_file}\n"
            )
            with open(output_filename, "w", encoding="utf-8") as yaml_file:
                yaml_file.write("logs:\n")
                yaml_file.write(yaml_buffer)
                yaml_file.close()

        # Save the response to the `out` file.
        if out is not None and out != "" and out != "None":
            try:
                with open(out, "w", encoding="utf-8") as out_file:
                    out_file.write(f"{this_output}\n")
                    out_file.close()
            except:
                print(f"Failed to write the output to file: {out}")

    elif helpme_mode == "PER_FILE":
        # Per file mode, which makes the request to each file in the path.
        if perfile.startswith("~/"):
            perfile = os.path.expanduser(perfile)
        this_path = os.path.realpath(resolve_path(perfile))
        if not os.path.exists(this_path):
            print(f"[Error] Cannot access the input path: {this_path}")
            exit(1)
        # Set the `file_type` variable for display only.
        file_type = "." + str(file_ext)
        if file_ext is None or file_ext == "":
            file_type = "All types"

        # if the `--cont` flag is set, inlcude the previous exchanges as additional context.
        context_file = None
        if cont:
            context_file = history_file

        # Ask the user to confirm.
        confirm_string = (
            f"Making a request to each file found in the path below:\n"
            + f"Question: {question}\nPath: {this_path}\nFile type: {file_type}\n"
        )
        if force or click.confirm(
            f"{confirm_string}" + f"Do you want to continue?",
            abort=True,
        ):
            if force:
                print(confirm_string)
            else:
                print()
            out_buffer = ""
            out_buffer_2 = ""
            yaml_buffer = ""
            for root, dirs, files in os.walk(resolve_path(perfile)):
                for file in files:
                    file_path = os.path.realpath(os.path.join(root, file))
                    if file_ext == None:
                        # Apply to all files.
                        print(f"# File: {file_path}")
                        file_content = ""
                        if (
                            file.endswith(".png")
                            or file.endswith(".jpg")
                            or file.endswith(".gif")
                        ):
                            file_content = "This is an image file.\n"
                        else:
                            try:
                                with open(file_path, "r", encoding="utf-8") as auto:
                                    file_content = auto.read()
                                    auto.close()
                            except:
                                print(
                                    f"[Warning] Skipping this file because it cannot be opened: {file}\n"
                                )
                                continue
                        this_output = console.ask_model_with_file(
                            question,
                            product_config,
                            file=file_path,
                            context_file=context_file,
                            rag=rag,
                            return_output=True,
                        )
                        this_output = this_output.strip()
                        # Render the response.
                        if use_panel:
                            print()
                            ai_console.print("[Response]", style=console_style)
                            ai_console.print(
                                Panel(Markdown(this_output, code_theme="manni"))
                            )
                            print()
                        else:
                            print()
                            print(f"{this_output}")
                            print()
                        # Prepare output to be saved in the history file.
                        out_buffer += (
                            f"QUESTION: {question}\n\n"
                            + f"FILE NAME: {file_path}\n"
                            + f"FILE CONTENT:\n\n{file_content}\n"
                            + f"RESPONSE:\n\n{this_output}\n\n"
                        )
                        # Prepare output to be saved in the `out` file.
                        out_buffer_2 += (
                            f"FILE NAME: {file_path}\n\n" + f"{this_output}\n\n"
                        )
                        # Prepare output to be saved in the YAML file.
                        if yaml is True:
                            yaml_buffer += (
                                f"  - question: {question}\n"
                                + f"    response: {this_output}\n"
                                + f"    file: {file_path}\n"
                            )
                        time.sleep(3)
                    elif file.endswith(file_ext):
                        print(f"# File: {file_path}")
                        file_content = ""
                        if (
                            file.endswith(".png")
                            or file.endswith(".jpg")
                            or file.endswith(".gif")
                        ):
                            file_content = "This is an image file.\n"
                        else:
                            try:
                                with open(file_path, "r", encoding="utf-8") as auto:
                                    file_content = auto.read()
                                    auto.close()
                            except:
                                print(
                                    f"[Warning] Skipping this file because it cannot be opened: {file}\n"
                                )
                                continue
                        this_output = console.ask_model_with_file(
                            question,
                            product_config,
                            file=file_path,
                            context_file=context_file,
                            rag=rag,
                            return_output=True,
                        )
                        this_output = this_output.strip()
                        # Render the response.
                        if use_panel:
                            print()
                            ai_console.print("[Response]", style=console_style)
                            ai_console.print(
                                Panel(Markdown(this_output, code_theme="manni"))
                            )
                            print()
                        else:
                            print()
                            print(f"{this_output}")
                            print()

                        # Prepare output to be saved in the history file.
                        out_buffer += (
                            f"QUESTION: {question}\n\n"
                            + f"FILE NAME: {file_path}\n"
                            + f"FILE CONTENT:\n\n{file_content}\n"
                            + f"RESPONSE:\n\n{this_output}\n\n"
                        )
                        # Prepare output to be saved in the `out` file.
                        out_buffer_2 += (
                            f"FILE NAME: {file_path}\n\n" + f"{this_output}\n\n"
                        )
                        # Prepare output to be saved in the YAML file.
                        if yaml is True:
                            yaml_buffer += (
                                f"  - question: {question}\n"
                                + f"    response: {this_output}\n"
                                + f"    file: {file_path}\n"
                            )
                        time.sleep(3)

            # If the `--new` flag is set, overwrite the history file.
            write_mode = "a"
            if new:
                write_mode = "w"
            # Record this exchange in the history file.
            with open(history_file, write_mode, encoding="utf-8") as out_file:
                out_file.write(out_buffer)
                out_file.close()

            if yaml is True:
                output_filename = "./responses.yaml"
                with open(output_filename, "w", encoding="utf-8") as yaml_file:
                    yaml_file.write("logs:\n")
                    yaml_file.write(yaml_buffer)
                    yaml_file.close()

            # Save the responses to the `out` file.
            if out is not None and out != "" and out != "None":
                try:
                    with open(out, "w", encoding="utf-8") as out_file:
                        out_file.write(f"{out_buffer_2}")
                        out_file.close()
                except:
                    print(f"Failed to write the output to file: {out}")

    elif helpme_mode == "ALL_FILES":
        if allfiles.startswith("~/"):
            allfiles = os.path.expanduser(allfiles)
        # All files mode, which makes all files in the path to be included as context.
        this_path = os.path.realpath(resolve_path(allfiles))
        if not os.path.exists(this_path):
            print(f"[Error] Cannot access the input path: {this_path}")
            exit(1)
        # Set the `file_type` variable for display only.
        file_type = "." + str(file_ext)
        if file_ext is None or file_ext == "":
            file_type = "All types"

        # Ask the user to confirm.
        confirm_string = (
            f"Adding all files found in the path below to context:\n"
            + f"Question: {question}\nPath: {this_path}\nFile type: {file_type}\n"
        )
        if force or click.confirm(
            f"{confirm_string}" + f"Do you want to continue?",
            abort=True,
        ):
            if force:
                print(confirm_string)
            else:
                print()
            context_buffer = ""
            for root, dirs, files in os.walk(resolve_path(allfiles)):
                for file in files:
                    file_path = os.path.realpath(os.path.join(root, file))
                    file_content = ""
                    if file_ext == None:
                        # Apply to all files.
                        print(f"# File: {file_path}")
                        try:
                            with open(file_path, "r", encoding="utf-8") as auto:
                                file_content = auto.read()
                                auto.close()
                            context_buffer += (
                                f"FILE NAME: {file_path}\n"
                                + f"FILE CONTENT:\n\n{file_content}\n\n"
                            )
                            print(f"Adding this file to context: {file}\n")
                        except:
                            print(
                                f"[Warning] Skipping this file because it cannot be opened: {file}\n"
                            )
                            continue
                    elif file.endswith(file_ext):
                        print(f"# File: {file_path}")
                        try:
                            with open(file_path, "r", encoding="utf-8") as auto:
                                file_content = auto.read()
                                auto.close()
                            context_buffer += (
                                f"FILE NAME: {file_path}\n"
                                + f"FILE CONTENT:\n\n{file_content}\n\n"
                            )
                            print(f"Adding this file to context: {file}\n")
                        except:
                            print(
                                f"[Warning] Skipping this file because it cannot be opened: {file}\n"
                            )
                            continue

            context = (
                "THE FOLLOWING ARE THE CONTENTS OF ALL THE FILES FOUND IN THE TARGET DIRECTORY:\n\n"
                + context_buffer
            )

            # If the `--new` flag is set, overwrite the history file.
            write_mode = "a"
            if new:
                write_mode = "w"
            elif cont:
                write_mode = "a"
            # Record this context in the history file.
            with open(history_file, write_mode, encoding="utf-8") as out_file:
                out_file.write(context)
                out_file.close()

            this_output = console.ask_model_with_file(
                question.strip(),
                product_config,
                file=None,
                context_file=history_file,
                rag=rag,
                return_output=True,
            )
            this_output = this_output.strip()
            # Render the response.
            if use_panel:
                ai_console.print("[Response]", style=console_style)
                ai_console.print(Panel(Markdown(this_output, code_theme="manni")))
            else:
                print()
                print(f"{this_output}")
                print()

            # Record this output in the history file.
            write_mode = "a"
            with open(history_file, write_mode, encoding="utf-8") as out_file:
                out_file.write(f"QUESTION: {question}\n\n")
                out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
                out_file.close()

            # Save this exchange in a YAML file.
            if yaml is True:
                output_filename = "./responses.yaml"
                # Prepare output to be saved in the YAML file.
                yaml_buffer = (
                    f"  - question: {question}\n"
                    + f"    response: {this_output}\n"
                    + f"    path: {this_path}\n"
                )
                with open(output_filename, "w", encoding="utf-8") as yaml_file:
                    yaml_file.write("logs:\n")
                    yaml_file.write(yaml_buffer)
                    yaml_file.close()

            # Save the response to the `out` file.
            if out is not None and out != "" and out != "None":
                try:
                    with open(out, "w", encoding="utf-8") as out_file:
                        out_file.write(f"{this_output}\n")
                        out_file.close()
                except:
                    print(f"Failed to write the output to file: {out}")

    elif helpme_mode == "TERMINAL_OUTPUT":
        # Terminal output mode, which reads the terminal ouput as context.
        terminal_output = ""
        # Set the default filename created from the `script` command.
        file_path = "/tmp/docs_agent_console_input"
        # Set the maximum number of lines to read from the terminal.
        lines_limit = -150
        # For the new 1.5 pro model, increase the limit to 5000 lines.
        if this_model.startswith("models/gemini-1.5"):
            lines_limit = -5000
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file.readlines()[int(lines_limit) : -2]:
                    # Filter non-ascii and control characters.
                    printable = set(string.printable)
                    line = "".join(filter(lambda x: x in printable, line))
                    terminal_output += line
                    # if an Enter key is detected, remove all saved lines.
                    # This allows to read the output of the last commandline only.
                    if re.search("^\[\?2004", line):
                        terminal_output = ""
        except:
            terminal_output = "No console output is provided."
        context = "THE FOLLOWING IS MY CONSOLE OUTPUT:\n\n" + terminal_output
        console.ask_model_for_help(question, context, product_config)
    else:
        # Default mode. No additional context is provided.
        this_output = console.ask_model_without_context(
            question.strip(),
            product_config,
            return_output=True,
        )

        # Render the response.
        if use_panel:
            ai_console.print("[Response]", style=console_style)
            ai_console.print(Panel(Markdown(this_output, code_theme="manni")))
        else:
            print()
            print(f"{this_output}")
            print()

        # If the `--new` flag is set, overwrite the history file.
        if new:
            write_mode = "w"
            # Record this exchange in the history file.
            with open(history_file, write_mode, encoding="utf-8") as out_file:
                out_file.write(f"QUESTION: {question}\n\n")
                out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
                out_file.close()

        # Save this exchange in a YAML file.
        if yaml is True:
            output_filename = "./responses.yaml"
            # Prepare output to be saved in the YAML file.
            yaml_buffer = (
                f"  - question: {question}\n" + f"    response: {this_output}\n"
            )
            with open(output_filename, "w", encoding="utf-8") as yaml_file:
                yaml_file.write("logs:\n")
                yaml_file.write(yaml_buffer)
                yaml_file.close()

        # Save the response to the `out` file.
        if out is not None and out != "" and out != "None":
            try:
                with open(out, "w", encoding="utf-8") as out_file:
                    out_file.write(f"{this_output}\n")
                    out_file.close()
            except:
                print(f"Failed to write the output to file: {out}")

    # When the --sleep flag is provided, sleep for the specified duration.
    if sleep > 0:
        time.sleep(int(sleep))


cli = click.CommandCollection(
    sources=[cli_helpme],
    help="With Docs Agent, you can interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()
