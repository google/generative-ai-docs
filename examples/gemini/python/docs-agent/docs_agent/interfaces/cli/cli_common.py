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

"""Docs Agent CLI common options"""

import click
import typing
from functools import wraps
from docs_agent.utilities.config import return_config_and_product


def common_options(func):
    @wraps(func)
    @click.option(
        "--config_file",
        help="Specify a configuration file. Defaults to config.yaml.",
        default=None,
    )
    @click.option(
        "--product",
        help="Specify a product. Defaults to use all products. For web app, defaults to use the first product in config.yaml.",
        default=None,
        multiple=True,
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@click.group(invoke_without_command=True)
@common_options
@click.pass_context
def cli_common(ctx, config_file, product):
    """With Docs Agent, you can populate vector databases,
    manage online corpora, and interact with Google's Gemini
    models."""
    ctx.ensure_object(dict)
    # Print config.yaml if agent is run without a command.
    if ctx.invoked_subcommand is None:
        click.echo("Docs Agent configuration:\n")
        show_config()


@cli_common.command()
def show_config(config_file: typing.Optional[str] = "config.yaml", product: list[str] = [""]):
    """Print the Docs Agent configuration."""
    # Loads configurations from common options
    loaded_config, product_config = return_config_and_product(
        config_file=config_file, product=product
    )
    for item in product_config.products:
        print("==========================")
        print(item)
