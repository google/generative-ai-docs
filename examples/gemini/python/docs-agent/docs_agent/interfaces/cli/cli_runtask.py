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

"""Docs Agent CLI client - run agent"""

import click
import typing
from absl import logging
from docs_agent.utilities import config
from docs_agent.interfaces import run_console as console
from docs_agent.utilities.helpers import get_project_path
from docs_agent.utilities.config import return_config_and_product
from docs_agent.utilities.tasks import return_tasks_config
from docs_agent.utilities.tasks import combine_yaml_files, TaskConfigFile
from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_helpme import helpme
from docs_agent.interfaces.cli.cli_tellme import tellme
from docs_agent.interfaces.cli.cli_posix import posix
import os
import re
import time

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.style import Style


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_runtask(ctx, config_file, product):
    """With Docs Agent, you can interact with Google's Gemini
    models and manage online corpora on Google Cloud."""
    ctx.ensure_object(dict)
    # Print config.yaml if task is run without a command.
    # if ctx.invoked_subcommand is None:
    #     click.echo("Docs Agent configuration:\n")
    #     show_config()


@cli_runtask.command(name="runtask")
@click.argument("words", nargs=-1)
@click.option(
    "--model",
    help="Specify a model to use. Overrides the model for all configured help me tasks and configuration. model setting is not overwritten for tellme tasks.",
    default=None,
    multiple=False,
)
@click.option(
    "--task_config",
    help="Specify a yaml file or path that contains configuration of tasks.",
    default=os.path.join(get_project_path(), "tasks"),
    multiple=False,
)
@click.option(
    "--force",
    is_flag=True,
    help="Do not ask the user to confirm interactively.",
)
@click.option(
    "--task",
    help="Specify a task to run.",
    default=None,
    multiple=True,
)
@click.option(
    "--custom_input",
    help="Specify an input string for the task.",
    default=None,
)
@click.pass_context
def runtask(
    # Words can be used to try to find an agent or match to helpme/tellme
    ctx,
    words,
    task_config: typing.Optional[str],
    task: typing.Optional[str],
    custom_input: typing.Optional[str] = None,
    model: typing.Optional[str] = None,
    force: bool = False,
    # task: typing.Optional[str] = None,
):
    """Perform tasks defined in a yaml file."""
    # Initialize Rich console
    ai_console = Console(width=120)
    console_style = Style(color="default", bold=True)
    use_panel = True
    task_config_user = os.path.join(os.path.expanduser("~/docs_agent"), "tasks")
    # Read the agent config.
    if task_config is None:
        task_config = os.path.join(get_project_path(), "tasks")
    if task_config.endswith(".yaml"):
        tasks_config = return_tasks_config(tasks_file=task_config, task=task)
    else:
        # Checks for --task flag to make sure we run right tasks
        tasks_config = combine_yaml_files(
            path=os.path.join(get_project_path(), "tasks")
        )
        try:
            combined_tasks_config = []
            tasks_config_user = combine_yaml_files(path=task_config_user)
            combined_tasks_config.extend(tasks_config_user.tasks)
            combined_tasks_config.extend(tasks_config.tasks)
            tasks_config = TaskConfigFile(tasks=combined_tasks_config)
        except:
            tasks_config = TaskConfigFile(tasks=tasks_config.tasks)
        if task is not None and task != ():
            for item in task:
                loaded_tasks_config = tasks_config.return_task(task=item)
                if loaded_tasks_config is None:
                    print()
                    print(f"Task {item} not found.")
                    print()
                    print("These are the available tasks:")
                    print()
                    for item in tasks_config.tasks:
                        print()
                        print(f"- {item.name}")
                        if item.description:
                            print(f"  Description: {item.description}")
                        print(f"  Usage: agent runtask --task {item.name}")
                    print()
                    print("You can also ask me to try to find a task for you.")
                    print()
                    print("Usage: agent runtask how can I generate release notes?")
                    exit(1)
                else:
                    tasks_config = loaded_tasks_config
        # This checks if a task is specified and if not, suggest a task.
        elif (task is None or task == ()) and words == "":
            print()
            print(
                f"No task specified. Please specify a task. These are the available tasks:"
            )
            for item in tasks_config.tasks:
                print()
                print(f"- {item.name}")
                if item.description:
                    print(f"  Description: {item.description}")
                print(f"  Usage: agent runtask --task {item.name}")
            exit(1)
    # Get the words before any flags.
    user_query = ""
    if (
        words == ()
        and (task == () or task == None)
        and (
            task_config == ""
            or task_config == None
            or task_config == os.path.join(get_project_path(), "tasks")
        )
    ):
        print()
        print("Please specify a task. These are the available tasks:")
        for item in tasks_config.tasks:
            print()
            print(f"- {item.name}")
            if item.description:
                print(f"  Description: {item.description}")
            print(f"  Usage: agent runtask --task {item.name}")
        exit(1)
    for word in words:
        user_query += word + " "
    if user_query != "":
        # Ask the model and retrieve the response.
        # md_cb_pattern = r"^```(?:\w+)?\s*\n(.*?)(?=^```)```"
        md_cb_regex = r"```\n(.*)\n```\s*((.|\n|\s)*)"
        task_assist = f"Given this question: {user_query}, which name of this list of values: {tasks_config} may be the best match? Return the task name in a markdown code block such as name=<name>. Then, justify your response below that. If you cannot find a good match for the task in the provided list and the user is asking a conceptual question, return name=tellme. If you think the user is asking for help with a task and not a conceptual question, return name=helpme. Return name=tellme if you think the user query is a conceptual question.Return name=helpme if you are unsure."
        # This should be fixed to not rely on product_config
        if model is None:
            model = "models/gemini-1.5-flash-latest"
        loaded_config, product_configs = return_config_and_product(model=model)
        output = console.ask_model_without_context(
            task_assist, product_configs, return_output=True
        )
        try:
            result = re.match(md_cb_regex, output)
            if result is None:
                print(
                    f"The LLM did not return a valid response for {user_query}. Try again."
                )
                exit(1)
            found = re.search("^name=(.*)$", result.group(1))
            if found is None:
                print(
                    f"The LLM did not return a valid response for {user_query}. Try again."
                )
                exit(1)
            # Prints the remaining response from model
            print()
            print(result.group(2))
            if (
                found.group(1) != "helpme"
                and found.group(1) != "tellme"
                and click.confirm(
                    f"Should I execute the {found.group(1)} task?",
                    abort=True,
                )
            ):
                print()
                ctx.invoke(
                    runtask,
                    words="",
                    force=True,
                    task=found.group(1).split(),
                    model="models/gemini-1.5-flash-latest",
                )
                exit(1)
            elif found.group(1) == "helpme":
                #     and click.confirm(
                #     f"Should I try to help you with {user_query}?",
                #     abort=True,
                # ):
                print()
                ctx.invoke(
                    helpme,
                    words=user_query.split(),
                    force=True,
                    new=True,
                    model="models/gemini-1.5-flash-latest",
                )
                print(
                    "Follow-up usage: agent helpme <more text> --cont --models/gemini-1.5-flash-latest"
                )
                exit(1)
            elif found.group(1) == "tellme":
                # and click.confirm(
                #     f"Should I tell you more about your question - {user_query}?",
                #     abort=True,
                # ):
                print()
                # Call helpme instead of tellme until rag is properly hooked in
                ctx.invoke(
                    tellme,
                    words=user_query.split(),
                )
                # print("Follow-up usage: agent helpme <more text> --cont")
                exit(1)
            else:
                print()
                ctx.invoke(
                    helpme,
                    words=user_query.split(),
                    force=True,
                    model="models/gemini-1.5-flash-latest",
                )
                print("Follow-up usage: agent helpme <more text> --cont")
                exit(1)
        except:
            exit(1)
    for curr_task in tasks_config.tasks:
        # Extract the top level model specified in the task config.
        top_level_model = ""
        if model is not None:
            top_level_model = model
        else:
            top_level_model = curr_task.model
        if not top_level_model.startswith("models/gemini"):
            click.echo(
                f"runtask mode is not supported with this model: {top_level_model} for {curr_task.name}"
            )
            exit(1)

        # Extract the preamble in the task config.
        this_preamble = ""
        if (
            hasattr(curr_task, "preamble")
            and curr_task.preamble is not None
            and curr_task.preamble != ""
        ):
            this_preamble = curr_task.preamble

        # Check if a custom input string is provided.
        if custom_input is not None:
            print()
            print(f"Custom input: {custom_input}")
            print(
                f"This input string will replace the <INPUT> placeholder in this task run."
            )

        # Ask the user to confirm.
        if force or click.confirm(
            f"\nPreparing to launch task:\n\n"
            + f"{curr_task}"
            + f"Do you want to launch the task?",
            abort=True,
        ):
            print()
            if use_panel:
                ai_console.print(f"Starting task: {curr_task.name}", style="cyan")
            else:
                print(f"Starting task: {curr_task.name}")
                # print(f"{curr_task}")
            list_of_output_files = ""
            this_step = 0
            for task in curr_task.steps:
                this_step += 1
                # Determine the states of the `is_new` and `is_cont` flags.
                is_new = False
                is_cont = True
                # The first step is always new by default.
                if int(this_step) == 1:
                    is_new = True
                if hasattr(task, "flags"):
                    if (
                        hasattr(task.flags, "new")
                        and task.flags.new is not None
                        and task.flags.new != ""
                    ):
                        if bool(task.flags.new):
                            is_new = True
                        else:
                            is_new = False
                    # `is_cont` is always True, unless specified.
                    if (
                        hasattr(task.flags, "cont")
                        and task.flags.cont is not None
                        and task.flags.cont != ""
                    ):
                        if bool(task.flags.cont):
                            is_cont = True
                        else:
                            is_cont = False

                # If is_new is True, is_cont is always False.
                if is_new:
                    is_cont = False

                # Select the model for this task. Use the top level model by default.
                this_model = top_level_model
                if hasattr(task, "flags"):
                    if hasattr(task.flags, "model"):
                        if task.flags.model is not None and task.flags.model != "":
                            this_model = task.flags.model

                # Determine the values for these fields used by helpme and tellme.
                this_file = None
                this_perfile = None
                this_allfiles = None
                this_file_ext = None
                this_out = None
                this_yaml = None
                this_rag = None
                this_terminal = None
                this_default_input = None
                if hasattr(task, "flags"):
                    if hasattr(task.flags, "file"):
                        this_file = task.flags.file
                    if hasattr(task.flags, "perfile"):
                        this_perfile = task.flags.perfile
                    if hasattr(task.flags, "allfiles"):
                        this_allfiles = task.flags.allfiles
                    if hasattr(task.flags, "file_ext"):
                        this_file_ext = task.flags.file_ext
                    if hasattr(task.flags, "out"):
                        this_out = task.flags.out
                    if hasattr(task.flags, "yaml"):
                        this_yaml = task.flags.yaml
                    if hasattr(task.flags, "rag"):
                        this_rag = task.flags.rag
                    if hasattr(task.flags, "terminal"):
                        this_terminal = task.flags.terminal
                    if hasattr(task.flags, "default_input"):
                        this_default_input = task.flags.default_input

                # Set the out filename to the default name.
                if this_out is None or this_out == "":
                    this_out = (
                        "out-"
                        + curr_task.name
                        + "-step-"
                        + "{:02d}".format(this_step)
                        + ".md"
                    )

                list_of_output_files += (
                    "* Step {:d}:".format(this_step) + " agent_out/" + this_out + "\n"
                )

                # Update the file-related fields if they are set to <INPUT> in the task file.
                if custom_input is not None:
                    # First try to replace them with the custom input value provided by
                    # the --custom_input flag at runtime
                    if this_file == "<INPUT>":
                        this_file = custom_input
                    if this_perfile == "<INPUT>":
                        this_perfile = custom_input
                    if this_allfiles == "<INPUT>":
                        this_allfiles = custom_input
                elif this_default_input is not None:
                    # If no custom_input value is provided at runtime,
                    # try to replace them with the default input value provided in the task file.
                    if this_file == "<INPUT>":
                        this_file = this_default_input
                    if this_perfile == "<INPUT>":
                        this_perfile = this_default_input
                    if this_allfiles == "<INPUT>":
                        this_allfiles = this_default_input
                else:
                    # Error and exit if there is still <INPUT> in any fields.
                    if (
                        this_file == "<INPUT>"
                        or this_perfile == "<INPUT>"
                        or this_allfiles == "<INPUT>"
                    ):
                        print()
                        print(
                            f"Error: Detected <INPUT> in the task fields. You must use the --custom_input flag to specify an input string for the task."
                        )
                        print(
                            f"Usage: agent runtask --task <TASK_NAME> --custom_input <CUSTOM_INPUT_STRING>"
                        )
                        exit(1)

                # If not specified, set the function field to "helpme".
                if task.function is None:
                    task.function = "helpme"

                # If not specified, set the name field to an empty string.
                if task.name is None:
                    task.name = ""

                # Select the command type: helpme, tellme, posix
                if task.function == "helpme":
                    # helpme Task
                    # Render this step information.
                    if use_panel:
                        print()
                        ai_console.print(
                            Panel(
                                f"Prompt (helpme): {task.prompt}",
                                title=f"Step {this_step}. {task.name}",
                                title_align="left",
                                padding=(1, 2),
                            ),
                            style=console_style,
                        )
                        print()
                    else:
                        print()
                        print(f"===================")
                        print(f"Starting task: {task.name}")
                        print(f"Prompt: {task.prompt}")
                        print(f"===================")
                        print()
                    overwrite_words = (
                        "FOLLOW THESE RULES FOR THE USER PROMPT: "
                        + this_preamble
                        + "\n\nUSER PROMPT: "
                        + task.prompt
                    )
                    overwrite_words = overwrite_words.split()
                    ctx.invoke(
                        helpme,
                        words=overwrite_words,
                        force=True,
                        file=this_file,
                        perfile=this_perfile,
                        allfiles=this_allfiles,
                        file_ext=this_file_ext,
                        out=this_out,
                        yaml=this_yaml,
                        rag=this_rag,
                        new=bool(is_new),
                        cont=bool(is_cont),
                        panel=bool(use_panel),
                        terminal=this_terminal,
                        model=this_model,
                    )
                elif task.function == "tellme":
                    # tellme Task
                    # Note: Usually don't want to overwrite model from curr_task.model in
                    # case it is aqa.
                    # Render this step information.
                    if use_panel:
                        print()
                        ai_console.print(
                            Panel(
                                f"Prompt (tellme): {task.prompt}",
                                title=f"Step {this_step}. {task.name}",
                                title_align="left",
                                padding=(1, 2),
                            ),
                            style=console_style,
                        )
                        print()
                    else:
                        print()
                        print(f"===================")
                        print(f"Answering question: {task.name}")
                        print(f"Prompt: {task.prompt}")
                        print(f"===================")
                        print()
                    overwrite_words = (
                        "FOLLOW THESE RULES FOR THE USER PROMPT: "
                        + this_preamble
                        + "\n\nUSER PROMPT: "
                        + task.prompt
                    )
                    overwrite_words = overwrite_words.split()
                    ctx.invoke(
                        tellme,
                        words=overwrite_words,
                        new=bool(is_new),
                        cont=bool(is_cont),
                        model=this_model,
                    )
                elif task.function == "posix":
                    # Render this step information.
                    if use_panel:
                        print()
                        ai_console.print(
                            Panel(
                                f"Command (posix): {task.prompt}",
                                title=f"Step {this_step}. {task.name}",
                                title_align="left",
                                padding=(1, 2),
                            ),
                            style=console_style,
                        )
                        print()
                    else:
                        print()
                        print(f"===================")
                        print(f"Running POSIX command: {task.name}")
                        print(f"Command: {task.prompt}")
                        print(f"===================")
                        print()
                    overwrite_words = task.prompt
                    overwrite_words = overwrite_words.split()
                    ctx.invoke(
                        posix,
                        words=overwrite_words,
                        new=bool(is_new),
                        cont=bool(is_cont),
                    )
                else:
                    logging.error("Unsupported task function: %s", task.function)
                    exit(1)
                time.sleep(3)

        print()
        print("[Output files]\n")
        print(list_of_output_files)


cli = click.CommandCollection(
    sources=[cli_runtask],
    help="With Docs Agent, you can interact with Google's Gemini models.",
)


if __name__ == "__main__":
    cli()
