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
)
from docs_agent.preprocess import files_to_plain_text as chunker
from docs_agent.preprocess import populate_vector_database as populate_script
from docs_agent.benchmarks import run_benchmark_tests as benchmarks
from docs_agent.interfaces import chatbot as chatbot_flask
from docs_agent.interfaces import run_console as console
from docs_agent.storage.google_semantic_retriever import SemanticRetriever
from docs_agent.storage.chroma import ChromaEnhanced
import socket
import os
import string
import re


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
def chunk(config_file: typing.Optional [str], product: list[str] = [""]):
    """Convert files to plain text chunks."""
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    chunker.process_all_products(config_file=product_config)
    click.echo("The files are successfully converted into text chunks.")


@cli_admin.command()
@common_options
def populate(config_file: typing.Optional [str], product: list[str] = [""]):
    """Populate a vector database using text chunks."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )

    populate_script.process_all_products(config_file=product_config)
    for item in product_config.products:
        click.echo(f"The text chunks are successfully added to {item.db_type}.")


@cli_admin.command()
@click.option("--hostname", default=socket.gethostname(), show_default=True)
@click.option("--port", default=5000, show_default=True, type=int)
@click.option("--debug", default=True, show_default=True, type=bool)
@click.option(
    "--app_mode",
    default=None,
    show_default=True,
    type=click.Choice(["web", "widget", "experimental"], case_sensitive=False),
    help="Specify a mode for the chatbot.",
)
@common_options
def chatbot(
    hostname: str,
    port: str,
    debug: str,
    app_mode: str,
    config_file: typing.Optional [str],
    product: list[str] = [""],
):
    """Launch the Flask-based chatbot app."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )

    product_file = product_config.products[0]
    if app_mode == None:
        app_mode = product_file.app_mode
    app = chatbot_flask.create_app(product=product_file, app_mode=app_mode)
    click.echo(
        f"Launching the chatbot UI for product {product_file.product_name} in {app_mode} mode."
    )
    app.run(host=hostname, port=port, debug=debug)


@cli_admin.command()
@common_options
def show_config(config_file: typing.Optional [str], product: list[str] = [""]):
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
@common_options
def tellme(words, config_file: typing.Optional [str], product: list[str] = [""]):
    """Answer a question related to the product."""
    # Loads configurations from common options
    loaded_config, product_configs = return_config_and_product(
        config_file=config_file, product=product
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
    "--file",
    type=click.Path(),
    help="Only available with Gemini 1.5 Pro. Specify a file with which a task is performed.",
)
@click.option(
    "--rag",
    is_flag=True,
    help="Only works with --file. Augments the context input with content from your configured RAG system.",
)
@common_options
def helpme(
    words,
    config_file: typing.Optional [str],
    file: typing.Optional [str] = None,
    rag: bool = False,
    product: list[str] = [""],
):
    """(Experimental) Ask AI to perform a task using console output.
    Use --file to perform a task on a specific file."""
    # Loads configurations from common options
    loaded_config, product_configs = return_config_and_product(
        config_file=config_file, product=product
    )
    if product == ():
        # Extracts the first product by default
        product_config = ConfigFile(products=[product_configs.products[0]])
    else:
        product_config = product_configs
    question = ""
    for word in words:
        question += word + " "
    if file:
        # This feature is only available in gemini 1.5 pro (large context)
        if product_config.products[0].models.language_model.startswith(
            "models/gemini-1.5-pro"
        ):
            try:
                with open(file, "r", encoding="utf-8") as auto:
                    # Read the input content
                    content = auto.read()
                    auto.close()
                final_file = f"The content of the {file} file:\n" + content
                console.ask_model_with_file(
                    question.strip(), product_config, file=final_file, rag=rag
                )
            except FileNotFoundError:
                click.echo(f"File not found: {file}")
        else:
            click.echo(
                f"File mode is not supported with this model: {product_config.products[0].models.language_model}"
            )
    else:
        terminal_output = ""
        # Set the default filename created from the `script` command.
        file_path = "/tmp/docs_agent_console_input"
        # Set the maximum number of lines to read from the terminal.
        lines_limit = -150
        if product_config.products[0].models.language_model.startswith(
            "models/gemini-1.5-pro"
        ):
            # Read, at the most, 5000 lines printed from the latest command ran on the terminal.
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
        console.ask_model_for_help(question.strip(), context, product_config)


@cli_admin.command()
@common_options
def benchmark(config_file: typing.Optional [str], product: list[str] = [""]):
    """Run the Docs Agent benchmark test."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    benchmarks.run_benchmarks()


@cli_admin.command()
@common_options
def list_corpora(config_file: typing.Optional [str], product: list[str] = [""]):
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
def delete_corpus(name: str, config_file: typing.Optional [str], product: list[str] = [""]):
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
def open_corpus(name: str, config_file: typing.Optional [str], product: list[str] = [""]):
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
    name: str, email: str, role: str, config_file: typing.Optional [str], product: list[str] = [""]
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
    name: str, config_file: typing.Optional [str], product: list[str] = [""]
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
def get_all_docs(name: str, config_file: typing.Optional [str], product: list[str] = [""]):
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
@click.option("--input_chroma", default=None)
@click.option("--output_dir", default=None)
@common_options
def backup_chroma(
    input_chroma: str,
    output_dir: typing.Optional [str],
    config_file: typing.Optional [str],
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


if __name__ == "__main__":
    cli()
