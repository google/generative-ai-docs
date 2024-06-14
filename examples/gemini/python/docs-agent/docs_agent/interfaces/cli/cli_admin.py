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
import sys
import typing
from docs_agent.utilities import config
from docs_agent.utilities.config import ReadDbConfigs
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
from docs_agent.storage.google_semantic_retriever import SemanticRetriever
from docs_agent.storage.chroma import ChromaEnhanced
from docs_agent.memory.logging import write_logs_to_csv_file
from docs_agent.interfaces.cli.cli_common import common_options
from docs_agent.interfaces.cli.cli_common import show_config
import socket
import os


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
    type=click.Choice(
        ["web", "full", "widget", "widget-pro", "experimental"],
        case_sensitive=False,
    ),
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
@click.option(
    "--model",
    help="Specify a model to use. Overrides the model (language_model) for all loaded product configurations.",
    default=None,
    multiple=False,
)
@common_options
def benchmark(
    config_file: typing.Optional[str],
    product: list[str] = [""],
    model: typing.Optional[str] = None,
):
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


cli = click.CommandCollection(
    sources=[cli_admin],
    help="With Docs Agent admin, you can populate vector databases, manage online corpora, and maintain Docs Agent.",
)


if __name__ == "__main__":
    cli()
