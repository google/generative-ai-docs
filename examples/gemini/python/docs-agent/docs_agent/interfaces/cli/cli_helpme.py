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
from docs_agent.utilities.config import ConfigFile
from docs_agent.utilities.config import return_config_and_product
from docs_agent.utilities.helpers import create_output_directory
from docs_agent.utilities.helpers import identify_file_type
from docs_agent.utilities.helpers import open_file
from docs_agent.utilities.helpers import resolve_and_ensure_path

from docs_agent.interfaces import run_console as console
from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_common import show_config
import os
import string
import re
import time
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
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
    multiple=True,
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
    "--list_file",
    type=click.Path(),
    help="Specify a path to a file that contains a list of input files.",
)
@click.option(
    "--file_ext",
    help="Works with --perfile and --dir. Specify the file type to be selected. The default is set to use all files.",
)
@click.option(
    "--repeat_until",
    is_flag=True,
    help="Repeat this step until conditions are met",
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
    list_file: typing.Optional[str] = None,
    file_ext: typing.Optional[str] = None,
    repeat_until: bool = False,
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
    # Remove the "models/" prefix if it exists. models/ prefix is legacy
    if this_model.startswith("models/"):
        this_model = this_model.removeprefix("models/")
    # This feature is only available to the Gemini Pro models (not AQA).
    if not this_model.startswith("gemini"):
        click.echo(f"File mode is not supported with this model: {this_model}")
        exit(1)
    # This feature is only available to the Gemini 1.5 or 2.0 models.
    if (
        not (this_model.startswith("gemini-1.5") or this_model.startswith("gemini-2.0"))
        and response_type != "text"
    ):
        click.echo(
            f"x.enum and json only work on gemini-1.5 or gemini-2.0 models. "
            + f"You are using: {this_model}"
        )
        exit(1)
    if response_type == "x.enum" and response_schema is None:
        click.echo(
            f"You must specify a response_schema when using text/x.enum. Optional for json."
        )
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
        + f"named {out}. Ensure that your response matches the format of this file "
        + f"extension. For example, .md indicates a Markdown file, .py a Python file, "
        + f"and so on. Markdown files must always be in valid Markdown format "
        + f"and begin with the # header (for instance, # <PAGE TITLE>).\n\n"
    )
    output_file_path = None
    original_question = question
    if out:
        output_file_path = create_output_directory(out)
        if not output_file_path:
            click.echo("Error: Could not determine or create a valid output directory.")
            exit(1)
        out_filename_display = Path(output_file_path).name
        question_out_wrapper = (
            f"The answer that you provide to the question below will be saved to a file "
            + f"named {out_filename_display}. Ensure that your response matches the format of this file "
            + f"extension. For example, .md indicates a Markdown file, .py a Python file, "
            + f"and so on. Markdown files must always be in valid Markdown format "
            + f"and begin with the # header (for instance, # <PAGE TITLE>).\n\n"
        )
        question = question_out_wrapper + question

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
    elif list_file and list_file != "None":
        helpme_mode = "LIST_FILE"
    elif file and file != "None" and file != [None]:
        helpme_mode = "SINGLE_FILE"
    elif cont:
        helpme_mode = "PREVIOUS_EXCHANGES"
    elif terminal:
        helpme_mode = "TERMINAL_OUTPUT"
    else:
        helpme_mode = "NO_FLAGS"

    # Select the mode.
    if helpme_mode == "PREVIOUS_EXCHANGES":
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
            yaml_file_path = create_output_directory("responses.yaml")
            # Prepare output to be saved in the YAML file.
            yaml_buffer = (
                f"  - question: {question}\n" + f"    response: {this_output}\n"
            )
            with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
                yaml_file.write("logs:\n")
                yaml_file.write(yaml_buffer)
                yaml_file.close()

        # Save the response to the `out` file.
        if out is not None and out != "" and out != "None":
            try:
                output_file_path = create_output_directory(out)
                with open(output_file_path, "w", encoding="utf-8") as out_file:
                    out_file.write(f"{this_output}\n")
                    out_file.close()
            except:
                print(f"Failed to write the output to file: {out}")

        # Check for conditions if repeat_until is True.
        if repeat_until:
            print()
            print("The repeat_until flag is set.")
            print()
            # print(f"{this_output}")
            # print()
            lines = this_output.splitlines()
            # print(lines)
            is_acceptable = False
            is_path_found = False
            yaml_lines = ""
            for this_line in lines:
                if this_line.startswith("- path:"):
                    print(this_line)
                    yaml_lines += this_line + "\n"
                    is_path_found = True
                elif is_path_found and this_line.startswith("  response:"):
                    print(this_line)
                    yaml_lines += this_line + "\n"
                    is_acceptable = True
            print()
            if is_acceptable is True:
                print("This yaml format is acceptable.")
                try:
                    yaml_out_filename = "./agent_out/task_output.yaml"
                    with open(yaml_out_filename, "w", encoding="utf-8") as yaml_file:
                        yaml_file.write(f"{yaml_lines}")
                        yaml_file.close()
                except:
                    print(f"Failed to write the output to file: {yaml_out_filename}")
            else:
                print("This yaml format is not acceptable!")
            print()
            return is_acceptable

    elif helpme_mode == "SINGLE_FILE":
        # Files mode, which makes the request to each file in the array.
        list_of_files = file
        input_file_count = 0
        is_multi = False
        for this_file in list_of_files:
            if len(list_of_files) > 1:
                if use_panel is True and input_file_count > 0:
                    print()
                print(f"Input file: {this_file}")
                if use_panel is True:
                    print()
            if input_file_count > 0:
                is_multi = True
            helpme_single_file_mode(
                console,
                question,
                product_config,
                history_file,
                rag,
                ai_console,
                console_style,
                use_panel,
                new,
                cont,
                yaml,
                out,
                this_file,
                is_multi,
            )
            input_file_count += 1

    elif helpme_mode == "PER_FILE":
        # Per file mode, which makes the request to each file in the path.
        this_path = resolve_and_ensure_path(perfile, check_exists=True)
        # Set the `file_type` variable for display only.
        file_type = "." + str(file_ext)
        if file_ext is None or file_ext == "":
            file_type = "All types"

        # if the `--cont` flag is set, include the previous exchanges as additional context.
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
            for root, dirs, files in os.walk(resolve_and_ensure_path(perfile)):
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
                yaml_file_path = create_output_directory("responses.yaml")
                with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
                    yaml_file.write("logs:\n")
                    yaml_file.write(yaml_buffer)
                    yaml_file.close()

            # Save the responses to the `out` file.
            if out is not None and out != "" and out != "None":
                try:
                    output_file_path = create_output_directory(out)
                    with open(output_file_path, "w", encoding="utf-8") as out_file:
                        out_file.write(f"{out_buffer_2}")
                        out_file.close()
                except:
                    print(f"Failed to write the output to file: {out}")

    elif helpme_mode == "ALL_FILES":
        # All files mode, which makes all files in the path to be included as context.
        this_path = resolve_and_ensure_path(allfiles, check_exists=True)
        # Set the `file_type` variable for display only.
        file_type = "." + str(file_ext)
        if file_ext is None or file_ext == "":
            file_type = "All types"

        # Ask the user to confirm.
        # Use original_question instead of question because question might be
        # modified by the question_out_wrapper.
        confirm_string = (
            f"Adding all files found in the path below to context:\n"
            + f"Question: {original_question}\nPath: {this_path}\nFile type: {file_type}\n"
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
            for root, dirs, files in os.walk(resolve_and_ensure_path(allfiles)):
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
                yaml_file_path = create_output_directory("responses.yaml")
                # output_filename = output_file_path + "/responses.yaml"
                # Prepare output to be saved in the YAML file.
                yaml_buffer = (
                    f"  - question: {question}\n"
                    + f"    response: {this_output}\n"
                    + f"    path: {this_path}\n"
                )
                with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
                    yaml_file.write("logs:\n")
                    yaml_file.write(yaml_buffer)
                    yaml_file.close()

            # Save the response to the `out` file.
            if output_file_path:
                try:
                    with open(output_file_path, "w", encoding="utf-8") as out_file:
                        out_file.write(f"{this_output}\n")
                        out_file.close()
                except:
                    print(f"Failed to write the output to file: {output_file_path}")

    elif helpme_mode == "LIST_FILE":
        # List file mode, which reads a text file that contains a list of input files.
        this_list_file = resolve_and_ensure_path(list_file, check_exists=True)
        print(f"Input list file: {this_list_file}")
        print()
        list_of_files = []
        try:
            with open(this_list_file, "r", encoding="utf-8") as file:
                for line in file.readlines():
                    # print(line.strip())
                    list_of_files.append(line.strip())
        except:
            print(f"[Error] Cannot access the input list file: {this_list_file}")
            exit(1)
        input_file_count = 0
        is_multi = False
        for this_file in list_of_files:
            if len(list_of_files) > 1:
                if use_panel is True and input_file_count > 0:
                    print()
                print(f"Input file: {this_file}")
                if use_panel is True:
                    print()
            if input_file_count > 0:
                is_multi = True
            helpme_single_file_mode(
                console,
                question,
                product_config,
                history_file,
                rag,
                ai_console,
                console_style,
                use_panel,
                new,
                cont,
                yaml,
                out,
                this_file,
                is_multi,
            )
            input_file_count += 1

    elif helpme_mode == "TERMINAL_OUTPUT":
        # Terminal output mode, which reads the terminal output as context.
        terminal_output = ""
        # Set the default filename created from the `script` command.
        file_path = "/tmp/docs_agent_console_input"
        # Set the maximum number of lines to read from the terminal.
        lines_limit = -150
        # For the new 1.5 pro model, increase the limit to 5000 lines.
        if this_model.startswith("gemini-1.5") or this_model.startswith("gemini-2.0"):
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
                    if re.search("^\\[\\?2004", line):
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
            yaml_file_path = create_output_directory("responses.yaml")
            # Prepare output to be saved in the YAML file.
            yaml_buffer = (
                f"  - question: {question}\n" + f"    response: {this_output}\n"
            )
            with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
                yaml_file.write("logs:\n")
                yaml_file.write(yaml_buffer)
                yaml_file.close()

        # Save the response to the `out` file.
        if output_file_path:
            try:
                with open(output_file_path, "w", encoding="utf-8") as out_file:
                    out_file.write(f"{this_output}\n")
                    out_file.close()
            except:
                print(f"Failed to write the output to file: {output_file_path}")

    # When the --sleep flag is provided, sleep for the specified duration.
    if sleep > 0:
        time.sleep(int(sleep))


def helpme_single_file_mode(
    console,
    question,
    product_config,
    history_file,
    rag,
    ai_console,
    console_style,
    use_panel,
    new,
    cont,
    yaml,
    out,
    file,
    is_multi,
):
    this_file = resolve_and_ensure_path(file)
    this_output = ""

    # if the `--cont` flag is set, include the previous exchanges as additional context.
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
    file_type = identify_file_type(this_file)
    if file_type == "image":
        file_content = "This is an image file.\n"
    elif file_type == "audio":
        file_content = "This is an audio file.\n"
    elif file_type == "video":
        file_content = "This is a video file.\n"
    else:
        file_content = open_file(this_file)
    # If the `--new` flag is set, overwrite the history file.
    write_mode = "a"
    if new:
        write_mode = "w"
        # However, if there are multiple files as input, do not overwrite the history file.
        if is_multi is True:
            write_mode = "a"
    # Record this exchange in the history file.
    with open(history_file, write_mode, encoding="utf-8") as out_file:
        out_file.write(f"QUESTION: {question}\n\n")
        out_file.write(f"FILE NAME: {file}\n")
        out_file.write(f"FILE CONTENT:\n\n{file_content}\n")
        out_file.write(f"RESPONSE:\n\n{this_output}\n\n")
        out_file.close()

    # Save this exchange in a YAML file.
    if yaml is True:
        yaml_file_path = create_output_directory("responses.yaml")
        # Prepare output to be saved in the YAML file.
        yaml_buffer = (
            f"  - question: {question}\n"
            + f"    response: {this_output}\n"
            + f"    file: {this_file}\n\n"
        )
        yaml_write_mode = "w"
        if is_multi is True:
            yaml_write_mode = "a"
        with open(yaml_file_path, yaml_write_mode, encoding="utf-8") as yaml_file:
            yaml_file.write("logs:\n")
            yaml_file.write(yaml_buffer)
            yaml_file.close()

    # Save the response to the `out` file.
    if out:
        output_file_path = create_output_directory(out)
        if not output_file_path:
            click.echo("Error: Could not determine or create a valid output directory.")
            exit(1)
        try:
            out_write_mode = "w"
            if is_multi is True:
                out_write_mode = "a"
            with open(output_file_path, out_write_mode, encoding="utf-8") as out_file:
                out_file.write(f"Input file: {this_file}\n\n")
                out_file.write(f"{this_output}\n\n")
                out_file.close()
        except:
            print(f"Failed to write the output to file: {output_file_path}")


cli = click.CommandCollection(
    sources=[cli_helpme],
    help="With Docs Agent, you can interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()
