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

# The configuration file config.yaml exists in the root of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_YAML = os.path.join(BASE_DIR, "config.yaml")
### Set up the path to the local LLM ###
LOCAL_VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_stores/chroma")

# Define the required keys to run scripts and chatbot
required_keys = ["output_path", "input", "product_name", "vector_db_dir"]
# Define any supported optional keys to run scripts and chatbot
optional_keys = []
# Define any required keys that define the properties of input paths
required_input_keys = ["path", "url_prefix"]
# Define any optional keys that define the properties of input paths
optional_input__keys = ["md_extension", "exlude_path"]


class ReadConfig:
    # Tries to ingest the configuration file and validate its keys
    def __init__(self):
        try:
            with open(INPUT_YAML, "r", encoding="utf-8") as inp_yaml:
                self.config_values = yaml.safe_load(inp_yaml)
                self.IS_CONFIG_FILE = True
                print("Configuration defined in: " + INPUT_YAML)
                # Check that the required keys exist
                self.validateKeys()
        except FileNotFoundError:
            print("The file " + INPUT_YAML + " does not exist.")
            # Exits the scripts if there is no valid config file
            return sys.exit(1)

    # Function to return the full configuration file
    def returnFullConfig(self):
        return self.config_values

    # Function to return the path of the configuration file
    def returnConfigFile(self):
        configFilePath = BASE_DIR + INPUT_YAML
        return configFilePath

    # Function to count the quantity of input paths
    def returnInputCount(self):
        count = len(self.returnConfigValue("input"))
        return count

    # Validates that a configuratioon file contains the required or optional keys
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
            if key not in self.config_values:
                print("Missing optional configuration key: " + key)

    # Checks if a key exists and returns its value
    def returnConfigValue(self, key):
        if key in self.config_values:
            return self.config_values[key]
        else:
            print("Error: " + key + " does not exist in the " + INPUT_YAML + " file.")
