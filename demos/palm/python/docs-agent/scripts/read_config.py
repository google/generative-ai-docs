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
import pathlib

# The configuration file config.yaml exists in the root of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_YAML = os.path.join(BASE_DIR, "config.yaml")
### Set up the path to the local LLM ###
LOCAL_VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_stores/chroma")

# Define the required keys to run scripts and chatbot
required_keys = ["output_path", "input", "product_name", "vector_db_dir"]
# Define any supported optional keys to run scripts and chatbot
optional_keys = ["docs_agent_config", "log_level"]
# Define any required keys that define the properties of input paths
required_input_keys = ["path", "url_prefix"]
# Define any optional keys that define the properties of input paths
optional_input__keys = ["md_extension", "exlude_path", "include_path_html"]

class Input:
    def __init__(self, path: str, url_prefix: str = None, include_path_html: str = None,
    ):
        self.path = path
        self.url_prefix = url_prefix
        self.include_path_html = include_path_html

class Config:
    def __init__(self, product_name: str, output_path: str, vector_db_dir: str, collection_name: str, api_endpoint: str, embedding_model: str, input: list
    ):
        self.product_name = product_name
        self.output_path = output_path
        self.vector_db_dir = vector_db_dir
        self.collection_name = collection_name
        self.api_endpoint = api_endpoint
        self.embedding_model = embedding_model
        self.input = input

    def __str__(self):
        return f"Product: {self.product_name}\n\
Output path: {self.output_path}\n\
Vector db path: {self.vector_db_dir}, Collection Name: {self.collection_name}, API endpoint: {self.api_endpoint}, Embedding Model: {self.embedding_model}\n\
Inputs: {input}\n\n"

class ReadConfig:
    # Tries to ingest the configuration file and validate its keys
    def __init__(self, yaml_config: str = INPUT_YAML):
        try:
            with open(yaml_config, "r", encoding="utf-8") as inp_yaml:
                self.config_values = yaml.safe_load(inp_yaml)
                self.IS_CONFIG_FILE = True
                self.is_config_file = True
                #print("Reading the config file: " + INPUT_YAML)
                # Check that the required keys exist
                self.validateKeys()
        except FileNotFoundError:
            print("The config file " + yaml_config + " does not exist.")
            # Exits the scripts if there is no valid config file
            return sys.exit(1)

    # Function to return the configuration object for the specific input
    def returnConfigObject(self, input: int = 0)->Config:
        product_name = self.returnConfigValue("product_name")
        output_path = self.returnConfigValue("output_path")
        vector_db_dir = self.returnConfigValue("vector_db_dir")
        collection_name = self.returnConfigValue("collection_name")
        api_endpoint = self.returnConfigValue("api_endpoint")
        embedding_model = self.returnConfigValue("embedding_model")
        config_obj = Config(product_name=product_name, output_path=output_path, vector_db_dir=vector_db_dir, collection_name=collection_name, api_endpoint=api_endpoint, embedding_model= embedding_model, input=[1,2])
        return config_obj

    # Function to return the full configuration file
    def returnFullConfig(self):
        return self.config_values

    # Function to return the path of the configuration file
    def returnConfigFile(self, yaml_config: str = INPUT_YAML, set_base_dir: str = BASE_DIR):
        configFilePath = set_base_dir + yaml_config
        return configFilePath

    # Function to count the quantity of input paths
    def returnInputCount(self):
        count = len(self.returnConfigValue("input"))
        return count

    # Function to return the attributes of a specific input
    def returnInputValues(self, input: int = 0)->Input:
        path = self.returnConfigValue("path")
        url_prefix = self.returnConfigValue("url_prefix")
        include_path_html = self.returnConfigValue("include_path_html")
        input_obj = Input(path=path, url_prefix=url_prefix, include_path_html=include_path_html)
        return input_obj

    # Validates that a configuration file contains the required or optional keys
    def validateKeys(self):
        for key in required_keys:
            if key in self.config_values:
                # Validates lists such as input with their respective keys
                if key == "input":
                    count = 0
                    for input in self.config_values["input"]:
                        count += 1
                        for required_key in required_input_keys:
                            if required_key not in input:
                                print(
                                    "Missing input configuration key: "
                                    + required_key
                                    + " from input source "
                                    + str(count)
                                )
            else:
                print("Missing required configuration key: " + key)
        for key in optional_keys:
            if key not in self.config_values and self.returnConfigValue("log_level") == "VERBOSE":
                print("Missing optional configuration key: " + key)

    # Checks if a key exists and returns its value
    # Supports check of "all" or "required". required - avoids output for optional keys
    def returnConfigValue(self, key, check: str = "required"):
        self.check = check
        if key in self.config_values:
            return self.config_values[key]
        elif check == "all":
            print("Error: " + key + " does not exist in the " + INPUT_YAML + " file.")
            return ""