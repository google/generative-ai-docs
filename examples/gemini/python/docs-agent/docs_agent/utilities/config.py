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

"""Read the configuration file to import user settings"""

import os
import sys
import yaml
import typing

from absl import logging
from docs_agent.utilities.helpers import get_project_path


class DbConfig:
    def __init__(
        self,
        # Currently 'chroma' or 'google_semantic_retriever'
        db_type: str,
        # These for 'chroma'
        vector_db_dir: typing.Optional[str] = None,
        collection_name: typing.Optional[str] = None,
        # These for 'google_semantic_retriever'
        corpus_name: typing.Optional[str] = None,
        # Only used when creating a corpus
        corpus_display: typing.Optional[str] = None,
    ):
        self.db_type = db_type
        self.vector_db_dir = vector_db_dir
        self.collection_name = collection_name
        self.corpus_name = corpus_name
        self.corpus_display = corpus_display

    def __str__(self):
        return f"Database type: {self.db_type}\n\
Vector database dir: {self.vector_db_dir}\n\
Collection name: {self.collection_name}\n\
Corpus name: {self.corpus_name}\n\
Corpus display: {self.corpus_display}\n"

    def return_vector_db_dir(self):
        return self.vector_db_dir


class ReadDbConfigs:
    # Tries to ingest a list of dictionaries with Input values
    def __init__(self, input_list: list[dict]):
        self.input_list = input_list

    def returnDbConfigs(self) -> list[DbConfig]:
        inputs = []
        for item in self.input_list:
            try:
                # Using .get let's you specify optional keys
                db_type = item["db_type"]
                if db_type == "chroma":
                    input_item = DbConfig(
                        db_type=db_type,
                        vector_db_dir=item["vector_db_dir"],
                        collection_name=item["collection_name"],
                    )
                elif db_type == "google_semantic_retriever":
                    input_item = DbConfig(
                        db_type=db_type,
                        corpus_name=item["corpus_name"],
                        corpus_display=item.get("corpus_display", None),
                    )
                else:
                    logging.error(f"You specified an unsupported db_type {db_type}")
                inputs.append(input_item)
            except KeyError as error:
                logging.error(f"The input is missing a key {error}")
                # Exits the scripts if there is missing input keys
                return sys.exit(1)
        return inputs

    def return_chroma_db(self):
        for item in self.input_list:
            if item["vector_db_dir"]:
                return item["vector_db_dir"]
            else:
                return None

    def __str__(self):
        return self.input_list


class Input:
    def __init__(
        self,
        path: str,
        url_prefix: typing.Optional[str] = None,
        include_path_html: typing.Optional[str] = None,
        exclude_path: typing.Optional[str] = None,
    ):
        self.path = path
        self.url_prefix = url_prefix
        self.include_path_html = include_path_html
        self.exclude_path = exclude_path

    def __str__(self):
        return f"Path: {self.path}\n\
URL prefix: {self.url_prefix}\n\
Include path html: {self.include_path_html}\n\
Exclude path: {self.exclude_path}\n"


class ReadInputs:
    # Tries to ingest a list of dictionaries with Input values
    def __init__(self, input_list: list[dict]):
        self.input_list = input_list

    def returnInputs(self) -> list[Input]:
        inputs = []
        for item in self.input_list:
            try:
                # Using .get let's you specify optional keys
                input_item = Input(
                    path=item["path"],
                    url_prefix=item["url_prefix"],
                    include_path_html=item.get("include_path_html", None),
                    exclude_path=item.get("exclude_path", None),
                )
                inputs.append(input_item)
            except KeyError as error:
                logging.error(f"The input is missing a key {error}")
                # Exits the scripts if there is missing input keys
                return sys.exit(1)
        return inputs

    def __str__(self):
        return self.input_list


class Models:
    def __init__(
        self,
        language_model: str,
        embedding_model: str,
        api_endpoint: typing.Optional[str] = None,
        api_key: typing.Optional[str] = None,
        embedding_api_call_limit: typing.Optional[int] = None,
        embedding_api_call_period: typing.Optional[int] = None,
    ):
        self.language_model = language_model
        self.embedding_model = embedding_model
        # Set up the Google API key from the environment.
        if api_key is None:
            api_key_var = os.getenv("GOOGLE_API_KEY")
            self.api_key = api_key_var
            if api_key_var is None:
                logging.error(
                    "Please set the environment variable GOOGLE_API_KEY to be your API key."
                )
        else:
            self.api_key = api_key
        if api_endpoint is None:
            self.api_endpoint = "generativelanguage.googleapis.com"
        else:
            self.api_endpoint = api_endpoint
        if embedding_api_call_limit is None:
            self.embedding_api_call_limit = 1400
        else:
            self.embedding_api_call_limit = embedding_api_call_limit
        if embedding_api_call_period is None:
            self.embedding_api_call_period = 60
        else:
            self.embedding_api_call_period = embedding_api_call_period

    def __str__(self):
        return f"Language model: {self.language_model}\n\
Embedding model: {self.embedding_model}\n\
API key: {self.api_key}\n\
API endpoint: {self.api_endpoint}\n\
Embedding API call limit: {str(self.embedding_api_call_limit)}\n\
Embedding API call period: {str(self.embedding_api_call_period)}\n"


class ReadModels:
    # Tries to ingest a list of dictionaries with Models values
    def __init__(self, input_list: list[dict]):
        self.input_list = input_list

    def returnModels(self) -> Models:
        # Check to make sure there is only 1 set of models per product
        if len(self.input_list) > 1:
            logging.error(f"Only 1 set of Models is supported")
            # Exits the scripts if there is missing input keys
            return sys.exit(1)
        models = []
        for item in self.input_list:
            try:
                # Using .get let's you specify optional keys
                model_item = Models(
                    language_model=item["language_model"],
                    embedding_model=item["embedding_model"],
                    api_endpoint=item.get("api_endpoint", None),
                    embedding_api_call_limit=item.get("embedding_api_call_limit", None),
                    embedding_api_call_period=item.get(
                        "embedding_api_call_period", None
                    ),
                )
                models.append(model_item)
            except KeyError as error:
                logging.error(f"The conditions is missing a key {error}")
                # Exits the scripts if there is missing input keys
                return sys.exit(1)
        return models[0]


class Conditions:
    def __init__(
        self,
        condition_text: str,
        fact_check_question: typing.Optional[str] = None,
        model_error_message: typing.Optional[str] = None,
    ):
        default_fact_check_question = (
            "Can you compare the text below to the information provided in this"
            " prompt above and write a short message that warns the readers"
            " about which part of the text they should consider"
            " fact-checking? (Please keep your response concise, focus on only"
            " one important item, but DO NOT USE BOLD TEXT IN YOUR RESPONSE.)"
        )
        default_model_error_message = (
            "Gemini is not able to answer this question at the moment."
            " Rephrase the question and try asking again."
        )
        self.condition_text = condition_text
        if fact_check_question is None:
            self.fact_check_question = default_fact_check_question
        else:
            self.fact_check_question = fact_check_question
        if model_error_message is None:
            self.model_error_message = default_model_error_message
        else:
            self.model_error_message = model_error_message

    def __str__(self):
        return f"Condition text: {self.condition_text}\n\
Fact check question: {self.fact_check_question}\n\
Model error message: {self.model_error_message}\n"


class ReadConditions:
    # Tries to ingest a list of dictionaries with Conditions values
    def __init__(self, input_list: list[dict]):
        self.input_list = input_list

    def returnConditions(self) -> Conditions:
        # Check to make sure there is only 1 set of conditions per product
        if len(self.input_list) > 1:
            logging.error(f"Only 1 set of conditions is supported")
            # Exits the scripts if there is missing input keys
            return sys.exit(1)
        conditions = []
        for item in self.input_list:
            try:
                # Using .get let's you specify optional keys
                condition_item = Conditions(
                    condition_text=item["condition_text"],
                    fact_check_question=item.get("fact_check_question", None),
                    model_error_message=item.get("model_error_message", None),
                )
                conditions.append(condition_item)
            except KeyError as error:
                logging.error(f"The conditions is missing a key {error}")
                # Exits the scripts if there is missing input keys
                return sys.exit(1)
        return conditions[0]


# Class to build a ProductConfig that contains variables to
# run docs agent
class ProductConfig:
    def __init__(
        self,
        product_name: str,
        models: Models,
        output_path: str,
        db_configs: list[DbConfig],
        inputs: list[Input],
        conditions: Conditions,
        log_level: typing.Optional[str] = None,
        docs_agent_config: typing.Optional[str] = None,
        markdown_splitter: str = "token_splitter",
        db_type: str = "chroma",
        app_mode: str = "web",
        enable_show_logs: str = "False",
    ):
        self.product_name = product_name
        self.docs_agent_config = docs_agent_config
        self.markdown_splitter = markdown_splitter
        self.db_type = db_type
        self.output_path = output_path
        self.db_configs = db_configs
        self.models = models
        self.conditions = conditions
        self.log_level = log_level
        self.inputs = inputs
        self.app_mode = app_mode
        self.enable_show_logs = enable_show_logs

    def __str__(self):
        # Extracts the list of Inputs
        inputs = []
        for item in self.inputs:
            inputs.append(str(item))
        input_str = "\n".join(inputs)
        # Extracts the list of DbConfigs
        dbconfigs = []
        for item in self.db_configs:
            dbconfigs.append(str(item))
        db_config_str = "\n".join(dbconfigs)
        return f"Product: {self.product_name}\n\
Docs Agent config: {self.docs_agent_config}\n\
App mode: {self.app_mode}\n\
Enable show logs: {self.enable_show_logs}\n\
Markdown splitter: {self.markdown_splitter}\n\
Database type: {self.db_type}\n\
Output path: {self.output_path}\n\
\nDatabase configs:\n{db_config_str}\n\
Log level: {self.log_level}\n\
\nModels:\n{self.models}\n\
\nInputs:\n{input_str}\n\
Conditions:\n{self.conditions}"


# This class is used to store the content of a list of
# ProductConfig
class ConfigFile:
    def __init__(
        self,
        products: list[ProductConfig],
    ):
        self.products = products

    def __str__(self):
        output = ["Products:"]
        for item in self.products:
            output.append(item)
        return "\n".join(output)

    def return_first(self):
        return self.products[0]


# Class used to read a specific configuration file or defaults
# to a config.yaml file in the root of the project
# printing the object returns the path as a string
# returnProducts() with an optional product flag will return
# all product configurations or the specified one
class ReadConfig:
    # Tries to ingest the configuration file and validate its keys
    # Defaults to the config.yaml file in the source of the project
    def __init__(
        self, yaml_path: str = os.path.join(get_project_path(), "config.yaml")
    ):
        self.yaml_path = yaml_path
        try:
            with open(yaml_path, "r", encoding="utf-8") as inp_yaml:
                self.config_values = yaml.safe_load(inp_yaml)
                # self.yaml_path = yaml_path
        except FileNotFoundError:
            logging.error(f"The config file {self.yaml_path} does not exist.")
            # Exits the scripts if there is no valid config file
            return sys.exit(1)

    def __str__(self):
        return self.yaml_path

    def returnProducts(self, product: typing.Optional[str] = None) -> ConfigFile:
        products = []
        try:
            for item in self.config_values["configs"]:
                name = ""
                try:
                    name = item["product_name"]
                except KeyError as error:
                    logging.error(f"Your configuration is missing a {error}")
                    return sys.exit()
                # Set the default value of `app_mode` to "web"
                supported_app_modes = ["web", "experimental", "widget", "1.5"]
                try:
                    app_mode = item["app_mode"]
                except KeyError:
                    app_mode = "web"
                if app_mode not in supported_app_modes:
                    logging.error(f"Your configuration is using an invalid mode: {app_mode}. Valid modes are {supported_app_modes}")
                    return sys.exit(1)
                try:
                    enable_show_logs = item["enable_show_logs"]
                except KeyError:
                    enable_show_logs = "False"
                try:
                    product_config = ProductConfig(
                        product_name=item["product_name"],
                        docs_agent_config=item["docs_agent_config"],
                        markdown_splitter=item["markdown_splitter"],
                        db_type=item["db_type"],
                        output_path=item["output_path"],
                        db_configs=item["db_configs"],
                        log_level=item["log_level"],
                        models=item["models"],
                        conditions=item["conditions"],
                        inputs=item["inputs"],
                        app_mode=app_mode,
                        enable_show_logs=enable_show_logs,
                    )
                    # This is done for keys with children
                    # Inputs
                    new_inputs = ReadInputs(
                        input_list=item["inputs"]
                    ).returnInputs()
                    product_config.inputs = new_inputs
                    product_config.inputs = new_inputs
                    # Conditions
                    new_conditions = ReadConditions(
                        input_list=item["conditions"]
                    ).returnConditions()
                    product_config.conditions = new_conditions
                    # Models
                    new_models = ReadModels(
                        input_list=item["models"]
                    ).returnModels()
                    product_config.models = new_models
                    # DbConfigs
                    new_db_configs = ReadDbConfigs(
                        input_list=item["db_configs"]
                    ).returnDbConfigs()
                    product_config.db_configs = new_db_configs
                    # Append
                    products.append(product_config)
                except KeyError as error:
                    if name != "":
                        logging.error(
                            f"A product configuration, {name} is missing a key {error}"
                        )
                        return sys.exit(1)
            if product is not None:
                match = False
                for item in products:
                    # If product is found, update products to a single entry in products
                    if item.product_name == product:
                        match = True
                        products = [item]
                        break
                # Exits if product is not found
                if not match:
                    logging.error(
                        f"The product {product} does not exist in {self.yaml_path}"
                    )
                    return sys.exit(1)
            config_file = ConfigFile(products=products)
            return config_file
        except KeyError as error:
            logging.error(
                f"Your configuration is missing a configs key {error} in {self.yaml_path}"
            )
            # Todo print out an example file
            return sys.exit(1)


# Function to make using common_options simpler
def return_config_and_product(config_file: typing.Optional[str] = None, product: list[str] = [""]):
    if config_file is None:
        loaded_config = ReadConfig()
    else:
        loaded_config = ReadConfig(yaml_path=config_file)
    final_products = []
    if product == ():
        product_config = loaded_config.returnProducts()
        final_products = product_config.products
    else:
        for item in product:
            product_config = loaded_config.returnProducts(product=item)
            final_products.append(product_config.products[0])
    product_config = ConfigFile(products=final_products)
    return loaded_config, product_config
