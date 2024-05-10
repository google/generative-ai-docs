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

"""Docs Agent CLI"""

import click
import sys
import typing
from functools import wraps
from docs_agent.utilities import config
from docs_agent.utilities.config import ReadDbConfigs, ConfigFile
from docs_agent.utilities.config import return_config_and_product
from docs_agent.utilities.helpers import (
    parallel_backup_dir,
    return_pure_dir,
    end_path_backslash,
    start_path_no_backslash,
    resolve_path,
)
from docs_agent.preprocess import files_to_plain_text as chunker
from docs_agent.preprocess import populate_vector_database as populate_script
from docs_agent.benchmarks import run_benchmark_tests as benchmarks
from docs_agent.interfaces import chatbot as chatbot_flask
from docs_agent.interfaces import run_console as console
from docs_agent.storage.google_semantic_retriever import SemanticRetriever
from docs_agent.storage.chroma import ChromaEnhanced
from docs_agent.memory.logging import write_logs_to_csv_file
import socket
import os
import string
import re
import time


def common_options(func):
    @wraps(func)
    @click.option(
        "--config_file",
        help="Specify a configuration file. Defaults to config.yaml.",
        default=None,
    )
    @click.option(
        "--product",
        help="Specify a product. Defaults to all products. For chatbot, defaults to the first product in config.yaml.",
        default=None,
        multiple=True,
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_admin(ctx, config_file, product):
    """With Docs Agent, you can populate vector databases,
    manage online corpora, and interact with Google's Gemini
    models."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_client(ctx, config_file, product):
    """With Docs Agent, you can interact with Google's Gemini
    models as well as content stored in Google Semantic Retriever Corpora."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


cli = click.CommandCollection(
    sources=[cli_admin, cli_client],
    help="With Docs Agent, you can populate vector databases, manage online corpora, and interact with Google's Gemini models.",
)


@cli_admin.command()
@common_options
def chunk(config_file: typing.Optional[str], product: list[str] = [""]):
    """Convert files to plain text chunks."""
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    chunker.process_all_products(config_file=product_config)
    click.echo("\nFiles are successfully converted into text chunks.")


@cli_admin.command()
@click.option(
    "--enable_delete_chunks",
    is_flag=True,
    help="Delete stale chunks in the existing databases.",
)
@common_options
def populate(
    config_file: typing.Optional[str],
    enable_delete_chunks: bool = False,
    product: list[str] = [""],
):
    """Populate a vector database using text chunks."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    # If `--enable_delete_chunks` flag is set, update the config object.
    if enable_delete_chunks:
        for product in product_config.products:
            product.enable_delete_chunks = "True"

    populate_script.process_all_products(config_file=product_config)
    for item in product_config.products:
        click.echo(f"\nText chunks are successfully added to {item.db_type}.")


@cli_admin.command()
@click.option("--hostname", default=socket.gethostname(), show_default=True)
@click.option("--port", default=5000, show_default=True, type=int)
@click.option("--debug", default=True, show_default=True, type=bool)
@click.option(
    "--app_mode",
    default=None,
    show_default=True,
    type=click.Choice(["web", "widget", "1.5", "experimental"], case_sensitive=False),
    help="Specify a mode for the chatbot.",
)
@click.option(
    "--enable_show_logs",
    is_flag=True,
    help="Enable a page view that shows log files.",
)
@click.option(
    "--enable_logs_to_markdown",
    is_flag=True,
    help="Save each question-and-response pair to a Markdown file.",
)
@common_options
def chatbot(
    hostname: str,
    port: str,
    debug: str,
    app_mode: str,
    enable_show_logs: str,
    enable_logs_to_markdown: str,
    config_file: typing.Optional[str],
    product: list[str] = [""],
):
    """Launch the Flask-based chatbot app."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    # Launch the web app using the first product in the `config.yaml` file.
    product = product_config.products[0]
    # Check the `--app_mode` flag
    if app_mode == None and hasattr(product, "app_mode"):
        app_mode = product.app_mode
    elif app_mode != None:
        # Update the app_mode field in the product config object.
        product.app_mode = app_mode
    # Check the `--app_port` flag
    app_port = int(port)
    if app_port == 5000 and hasattr(product, "app_port"):
        app_port = int(product.app_port)
    # If `--enable_show_logs` flag is set, update the product config object.
    if enable_show_logs:
        product.enable_show_logs = "True"
    # If `--enable_logs_to_markdown` flag is set, update the product config object.
    if enable_logs_to_markdown:
        product.enable_logs_to_markdown = "True"
    app = chatbot_flask.create_app(product=product, app_mode=app_mode)
    click.echo(
        f"Launching the chatbot UI for product {product.product_name} in {app_mode} mode."
    )
    app.run(host=hostname, port=app_port, debug=debug)


@cli_admin.command()
@common_options
def show_config(config_file: typing.Optional[str], product: list[str] = [""]):
    """Print the Docs Agent configuration."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    for item in product_config.products:
        print("==========================")
        print(item)


@cli_client.command(name="tellme")
@click.argument("words", nargs=-1)
@click.option(
    "--model",
    help="Specify a model to use. Overrides the model (language_model) for all loaded product configurations.",
    default=None,
    multiple=False,
)
@common_options
def tellme(words, config_file: typing.Optional[str], product: list[str] = [""], model: typing.Optional[str] = None):
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
    question = ""
    for word in words:
        question += word + " "
    console.ask_model(question.strip(), product_config)


@cli_client.command()
@click.argument("words", nargs=-1)
@click.option(
    "--model",
    help="Specify a model to use. Overrides the model (language_model) for all loaded product configurations.",
    default=None,
    multiple=False,
)
@click.option(
    "--file",
    type=click.Path(),
    help="Specify a file to be included as context.",
)
@click.option(
    "--path",
    type=click.Path(),
    help="Specify a path where the request will be applied to all files found in the directory.",
)
@click.option(
    "--file_ext",
    help="Works with --path. Specify the file type to be selected. By default it is set to None.",
)
@click.option(
    "--rag",
    is_flag=True,
    help="Add entries found in the knowledge database as context.",
)
@click.option(
    "--yaml",
    is_flag=True,
    help="Works with --path. Store the output as a responses.yaml file.",
)
@click.option(
    "--new",
    is_flag=True,
    help="Works with --file. Clear the previous responses buffer.",
)
@click.option(
    "--cont",
    is_flag=True,
    help="Use the previous responses buffer as context.",
)
@common_options
def helpme(
    words,
    config_file: typing.Optional[str],
    file: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    file_ext: typing.Optional[str] = None,
    rag: bool = False,
    yaml: bool = False,
    new: bool = False,
    cont: bool = False,
    product: list[str] = [""],
    model: typing.Optional[str] = None,
):
    """Ask the AI model to perform a task from the terminal."""
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

    # Get the question string.
    question = ""
    for word in words:
        question += word + " "
    question = question.strip()

    # Set the filename for recording exchanges with the Gemini models.
    history_file = "/tmp/docs_agent_responses"

    # 4 different mode: Terminal output (default), All files, Single file,
    # and Previous exchanges
    helpme_mode = "TERMINAL_OUTPUT"
    if path:
        helpme_mode = "ALL_FILES"
    elif file and file != "None":
        helpme_mode = "SINGLE_FILE"
    elif cont:
        helpme_mode = "PREVIOUS_EXCHANGES"

    if helpme_mode == "PREVIOUS_EXCHANGES":
        # Continue mode, which uses the previous exchangs as the main context.
        this_output = console.ask_model_with_file(
            question.strip(),
            product_config,
            context_file=history_file,
            rag=rag,
            return_output=True,
        )
        print()
        print(f"{this_output}")
        print()
        with open(history_file, "a", encoding="utf-8") as out_file:
            out_file.write(f"QUESTION: {question}\n\n")
            out_file.write(f"RESPONSE:\n\n{this_output}\n")
            out_file.close()
    elif helpme_mode == "SINGLE_FILE":
        # Single file mode.
        this_file = os.path.realpath(os.path.join(os.getcwd(), file))
        this_output = ""
        if cont:
            # if the `--cont` flag is set, inlcude the previous exchanges as additional context.
            this_output = console.ask_model_with_file(
                question.strip(),
                product_config,
                file=this_file,
                context_file=history_file,
                rag=rag,
                return_output=True,
            )
        else:
            # By default, do not inlcude any additional context.
            this_output = console.ask_model_with_file(
                question.strip(),
                product_config,
                file=this_file,
                rag=rag,
                return_output=True,
            )
        print()
        print(f"{this_output}")
        print()
        # Read the file content to be included in the history file.
        file_content = ""
        with open(this_file, "r", encoding="utf-8") as target_file:
            file_content = target_file.read()
            target_file.close()
        # If the `--new` flag is set, overwrite the history file.
        write_mode = "a"
        if new:
            write_mode = "w"
        # Record this exchange in the history file.
        with open(history_file, write_mode, encoding="utf-8") as out_file:
            out_file.write(f"QUESTION: {question}\n\n")
            out_file.write(f"FILE NAME: {file}\n")
            out_file.write(f"FILE CONTENT:\n\n{file_content}\n")
            out_file.write(f"RESPONSE:\n\n{this_output}\n")
            out_file.close()
    elif helpme_mode == "ALL_FILES":
        # All files mode, which makes the request to all files in the path.
        # Set the `file_type` variable for display only.
        file_type = "." + str(file_ext)
        if file_ext == None:
            file_type = "All types"

        # Ask the user to confirm.
        if click.confirm(
            f"Making a request to all files found in the path below:\n"
            + f"Question: {question}\nPath:  {path}\nFile type: {file_type}\n"
            + f"Do you want to continue?",
            abort=True,
        ):
            print()
            out_buffer = ""
            for root, dirs, files in os.walk(resolve_path(path)):
                for file in files:
                    file_path = os.path.realpath(os.path.join(root, file))
                    if file_ext == None:
                        # Apply to all files.
                        print(f"# File: {file_path}")
                        this_output = console.ask_model_with_file(
                            question,
                            product_config,
                            file=file_path,
                            rag=rag,
                            return_output=True,
                        )
                        this_output = this_output.strip()
                        print()
                        print(f"{this_output}")
                        print()
                        if yaml is True:
                            out_buffer += (
                                f"  - question: {question}\n"
                                + f"    response: {this_output}\n"
                                + f"    file: {file_path}\n"
                            )
                        time.sleep(2)
                    elif file.endswith(file_ext):
                        print(f"# File: {file_path}")
                        this_output = console.ask_model_with_file(
                            question,
                            product_config,
                            file=file_path,
                            rag=rag,
                            return_output=True,
                        )
                        this_output = this_output.strip()
                        print()
                        print(f"{this_output}")
                        print()
                        if yaml is True:
                            out_buffer += (
                                f"  - question: {question}\n"
                                + f"    response: {this_output}\n"
                                + f"    file: {file_path}\n"
                            )
                        time.sleep(2)

            if yaml is True:
                output_filename = "./responses.yaml"
                with open(output_filename, "w", encoding="utf-8") as out_file:
                    out_file.write("benchmarks:\n")
                    out_file.write(out_buffer)
                    out_file.close()
    else:
        # Terminal output mode, which reads the terminal ouput as context.
        terminal_output = ""
        # Set the default filename created from the `script` command.
        file_path = "/tmp/docs_agent_console_input"
        # Set the maximum number of lines to read from the terminal.
        lines_limit = -150
        # For the new 1.5 pro model, increase the limit to 5000 lines.
        if this_model.startswith("models/gemini-1.5-pro"):
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


@cli_admin.command()
@click.option(
    "--model",
    help="Specify a model to use. Overrides the model (language_model) for all loaded product configurations.",
    default=None,
    multiple=False,
)
@common_options
def benchmark(config_file: typing.Optional[str], product: list[str] = [""],  model: typing.Optional[str] = None):
    """Run the Docs Agent benchmark test."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product, model=model
    )
    benchmarks.run_benchmarks()


@cli_admin.command()
@common_options
def list_corpora(config_file: typing.Optional[str], product: list[str] = [""]):
    """List all existing online corpora."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    semantic = SemanticRetriever()
    response = semantic.list_existing_corpora()
    click.echo(f"Found the following corpora:\n")
    click.echo(f"{response}")
    while hasattr(response, "next_page_token") and response.next_page_token != "":
        response = semantic.list_existing_corpora(response.next_page_token)
        click.echo(f"{response}")


@cli_admin.command()
@click.option("--name", default=None)
@common_options
def delete_corpus(
    name: str, config_file: typing.Optional[str], product: list[str] = [""]
):
    """Delete an online corpus."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    semantic = SemanticRetriever()
    # product_file = product_config.products[0]
    if name == None:
        click.echo("Usage: agent delete-corpus --name <CORPUS_NAME>")
    else:
        click.echo("Deleting " + name)
        if click.confirm("Do you want to continue?", abort=True):
            semantic.delete_a_corpus(corpus_name=name, force=True)
            click.echo("Successfuly deleted " + name)
            corpora_response = semantic.list_existing_corpora()
            click.echo(f"Corpora list:\n{corpora_response}")


@cli_admin.command()
@click.option("--name", default=None)
@common_options
def open_corpus(
    name: str, config_file: typing.Optional[str], product: list[str] = [""]
):
    """Share an online corpus with everyone."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    semantic = SemanticRetriever()
    # product_file = product_config.products[0]
    if name == None:
        click.echo("Usage: agent open-corpus --name <CORPUS_NAME>")
    else:
        click.echo("Sharing " + name)
        if click.confirm("Do you want to continue?", abort=True):
            semantic.open_a_corpus(corpus_name=name)
            click.echo("Successfully shared " + name)


@cli_admin.command()
@click.option("--name", default=None)
@click.option("--email", default=None)
@click.option("--role", default="READER")
@common_options
def share_corpus(
    name: str,
    email: str,
    role: str,
    config_file: typing.Optional[str],
    product: list[str] = [""],
):
    """Share an online corpus with a user."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    semantic = SemanticRetriever()
    # product_file = product_config.products[0]
    if name == None:
        click.echo(
            "Usage: agent share-corpus --name <CORPUS_NAME> --email <EMAIL> --role READER (or WRITER)"
        )
    else:
        click.echo("Sharing " + name + " with " + email + " as " + role + " role.")
        if click.confirm("Do you want to continue?", abort=True):
            semantic.share_a_corpus(corpus_name=name, email=email, role=role)
            click.echo("Successfully shared " + name)


@cli_admin.command()
@click.option("--name", default=None)
@common_options
def remove_corpus_permission(
    name: str, config_file: typing.Optional[str], product: list[str] = [""]
):
    """Remove a user permission from an online corpus."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    semantic = SemanticRetriever()
    # product_file = product_config.products[0]
    if name == None:
        click.echo("Usage: agent remove-corpus-permission --name <PERMISSION_NAME>")
    else:
        click.echo("Removing " + name)
        if click.confirm("Do you want to continue?", abort=True):
            semantic.delete_permission(permission_name=name)
            click.echo("Successfully removed " + name)


@cli_admin.command()
@click.option("--name", default=None)
@common_options
def get_all_docs(
    name: str, config_file: typing.Optional[str], product: list[str] = [""]
):
    """Get the list of all docs in an online corpus."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    semantic = SemanticRetriever()
    if name == None:
        click.echo("Usage: agent get_all_docs --name <CORPUS_NAME>")
    else:
        click.echo("Getting the list of all docs from " + name)
        semantic.get_all_docs(corpus_name=name, print_output=True)


@cli_admin.command()
@common_options
def cleanup_dev(
    config_file: typing.Optional[str],
    product: list[str] = [""],
):
    """Delete all databases in this Docs Agent development environment."""
    print("Cleaning up the Docs Agent development environment.")
    print("Found the following database configuration:")
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    chroma_dir = ""
    corpus_name = ""
    product = product_config.products[0]
    for db in product.db_configs:
        if hasattr(db, "vector_db_dir") and db.vector_db_dir != None:
            print(f"Chroma database: {db.vector_db_dir}")
            chroma_dir = db.vector_db_dir
        if hasattr(db, "corpus_name") and db.corpus_name != None:
            print(f"Corpus name: {db.corpus_name}")
            corpus_name = db.corpus_name
    if chroma_dir != "":
        command = "rm -fr " + chroma_dir
        if click.confirm(
            f"\nDeleting the Chroma database {chroma_dir} ({command}).\nDo you want to continue?",
            abort=True,
        ):
            os.system(command)
            print("Done.")
    if corpus_name != "":
        if click.confirm(
            f"\nDeleting the corpus named {corpus_name}.\nDo you want to continue?",
            abort=True,
        ):
            semantic = SemanticRetriever()
            semantic.delete_a_corpus(corpus_name=corpus_name)
            print("Done.")


@cli_admin.command()
@click.option("--input_chroma", default=None)
@click.option("--output_dir", default=None)
@common_options
def backup_chroma(
    input_chroma: str,
    output_dir: typing.Optional[str],
    config_file: typing.Optional[str],
    product: list[str] = [""],
):
    """Backup a chroma database to an output directory."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    if input_chroma == None:
        # Get first product
        input_product = product_config.return_first()
        if input_product.db_type == "chroma":
            input_chroma = ReadDbConfigs(input_product.db_configs).return_chroma_db()
        else:
            click.echo(
                f"Your product {input_product.product_name} is not configured for chroma."
            )
            sys.exit(0)
    if output_dir == None:
        output_dir = parallel_backup_dir(input_chroma)
    else:
        pure_path = return_pure_dir(input_chroma)
        output_dir = end_path_backslash(start_path_no_backslash(output_dir)) + pure_path
    # Initialize chroma and then use backup function
    chroma_db = ChromaEnhanced(chroma_dir=input_chroma)
    final_output_dir = chroma_db.backup_chroma(
        chroma_dir=input_chroma, output_dir=output_dir
    )
    if final_output_dir:
        click.echo(f"Successfully backed up {input_chroma} to {final_output_dir}.")
    else:
        click.echo(f"Can't backup chroma database specified: {input_chroma}")


@cli_admin.command()
@click.option("--date", default="None")
@common_options
def write_logs_to_csv(
    date: typing.Optional[str],
    config_file: typing.Optional[str],
    product: list[str] = [""],
):
    """Write captured debug information to a CSV file."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    output_filename = "debug-info-all.csv"
    if date != "None":
        output_filename = "debug-info-" + str(date) + ".csv"
        click.echo(
            f"Writing all debug logs from {date} to the logs/{output_filename} file:\n"
        )
    else:
        click.echo(f"Writing all debug logs to the logs/{output_filename} file:\n")
    # Write the target debug logs to a CSV file.
    write_logs_to_csv_file(log_date=date)
    # Print the content of the CSV file.
    with open("./logs/" + output_filename, "r") as f:
        print(f.read())
        f.close()


if __name__ == "__main__":
    cli()
