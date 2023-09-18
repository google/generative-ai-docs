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

"""Populate the vector database with embeddings generated from text chunks"""

import os
import sys
import re
import json
import chromadb
import flatdict
import uuid
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.api.types import Documents, Embeddings
import google.generativeai as palm
from ratelimit import limits, sleep_and_retry
import read_config

### Notes on how to use this script ###
#
# Prerequisites:
# - Have plain text files stored in the PLAIN_TEXT_DIR directory
#   (see `markdown_to_plain_text.py`)
#
# Do the following:
# 1. If you are not using a `input-values.yaml` file,
#    edit PLAIN_TEXT_DIR in this script (see below).
# 2. Run:
#    $ python3 ./scripts/populate-vector-database.py
#
# To test, run:
# $ python3 ./script/test-vector-database.py
#

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
### Select the input directory of plain text files, this will be overridden by
### `input-values.yaml`
### Set up the path to the local LLM ###
LOCAL_VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_stores/chroma")
COLLECTION_NAME = "docs_collection"

IS_CONFIG_FILE = True
if IS_CONFIG_FILE:
    config_values = read_config.ReadConfig()
    PLAIN_TEXT_DIR = config_values.returnConfigValue("output_path")
    input_len = config_values.returnInputCount()
    LOCAL_VECTOR_DB_DIR = config_values.returnConfigValue("vector_db_dir")
    COLLECTION_NAME = config_values.returnConfigValue("collection_name")

### Select the file index that is generated with your plain text files, same directory
INPUT_FILE_INDEX = "file_index.json"

# Select the type of embeddings to use, PALM or LOCAL
EMBEDDINGS_TYPE = "PALM"

### Set up the PaLM API key from the environment ###
API_KEY = os.getenv("PALM_API_KEY")
if API_KEY is None:
    sys.exit("Please set the environment variable PALM_API_KEY to be your API key.")

# PaLM API call limit to 300 per minute
API_CALLS = 280
API_CALL_PERIOD = 60

# Enable relative directories.
if not BASE_DIR.endswith("/"):
    BASE_DIR = BASE_DIR + "/"

if not PLAIN_TEXT_DIR.endswith("/"):
    PLAIN_TEXT_DIR = PLAIN_TEXT_DIR + "/"

FULL_BASE_DIR = BASE_DIR + PLAIN_TEXT_DIR
print("Plain text directory: " + FULL_BASE_DIR + "\n")

FULL_INDEX_PATH = PLAIN_TEXT_DIR + INPUT_FILE_INDEX
try:
    with open(FULL_INDEX_PATH, "r", encoding="utf-8") as index_file:
        index = json.load(index_file)
except FileNotFoundError:
    msg = "The file " + FULL_INDEX_PATH + "does not exist."

if EMBEDDINGS_TYPE == "PALM":
    palm.configure(api_key=API_KEY)
    # This returns models/embedding-gecko-001"
    models = [
        m for m in palm.list_models() if "embedText" in m.supported_generation_methods
    ]
    # MODEL = "models/embedding-gecko-001"
    MODEL = models[0]
elif EMBEDDINGS_TYPE == "LOCAL":
    MODEL = os.path.join(BASE_DIR, "models/all-mpnet-base-v2")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL)
else:
    MODEL = os.path.join(BASE_DIR, "models/all-mpnet-base-v2")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL)

chroma_client = chromadb.Client(
    Settings(chroma_db_impl="duckdb+parquet", persist_directory=LOCAL_VECTOR_DB_DIR)
)


# Create embed function for PaLM
# API call limit to 5 qps
@sleep_and_retry
@limits(calls=API_CALLS, period=API_CALL_PERIOD)
def embed_function(texts: Documents) -> Embeddings:
    # Embed the documents using any supported method
    return [
        palm.generate_embeddings(model=MODEL, text=text)["embedding"] for text in texts
    ]


if EMBEDDINGS_TYPE == "PALM":
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embed_function
    )
elif EMBEDDINGS_TYPE == "LOCAL":
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=emb_fn
    )
else:
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=emb_fn
    )

documents = []
metadatas = []
ids = []
i = 0
updated_count = 0
new_count = 0
unchanged_count = 0

# Read plain text files (.md) from the PLAIN_TEXT_DIR dir and
# add their content to the vector database.
# Embeddings are generated automatically as they are added to the database.
for root, dirs, files in os.walk(PLAIN_TEXT_DIR):
    for file in files:
        file_update = False
        # Persists every nth time and if there was an actual update or added file.
        # However, we don't need to persist, which takes time, if there are no updates.
        if i % 100 == 0 and file_update == True:
            chroma_client.persist()
        if file.endswith(".md"):
            with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                print("Process an entry into the database: " + str(i))
                print("Opening a file: " + file)
                # Extract the original filename used (without a file extension)
                match = re.search(r"(.*)\.md$", file)
                filename_no_ext = match[1]
                toFile = auto.read()
                # Contruct the URL
                match2 = re.search(r"(.*)_\d*$", filename_no_ext)
                filename_for_url = match2[1]
                clean_filename = re.sub(PLAIN_TEXT_DIR, "", os.path.join(root, ""))
                url = clean_filename + filename_for_url + ".md"
                url_path = ""
                md_hash = ""
                uuid_file = ""
                # Build the full filename to match entries in file_index.json
                # Using the full path avoids mismatches
                full_file_name = FULL_BASE_DIR + clean_filename + file
                metadata_dict_extra = {}
                # Reads the metadata associated with files
                for key in index:
                    if full_file_name in index[key]:
                        if (
                            "URL" in index[key][full_file_name]
                            and "source_id" in index[key][full_file_name]
                        ):
                            # This ensures the URL is retrived from the correct file.
                            # Avoids issues with common file names such as README.md
                            if int(key) == index[key][full_file_name]["source_id"]:
                                if index[key][full_file_name]["URL"]:
                                    url_path = index[key][full_file_name]["URL"]
                                else:
                                    print("No valid URL value for: " + file)
                        # If metadata exists, add these to a dictionary that is then
                        # merged with other metadata values
                        if "metadata" in index[key][full_file_name]:
                            # Save and flatten dictionary
                            metadata_dict_extra = flatdict.FlatterDict(
                                index[key][full_file_name]["metadata"], delimiter="_"
                            )
                            metadata_dict_extra = dict(metadata_dict_extra)
                        else:
                            metadata_dict_extra = {}
                        if "UUID" in index[key][full_file_name]:
                            uuid_file = index[key][full_file_name]["UUID"]
                        if "md_hash" in index[key][full_file_name]:
                            md_hash = str(index[key][full_file_name]["md_hash"])
                # Add a trailing "/" to the url path in case the configuration file
                # didn't have it.
                # Do not add slashes to PSAs.
                if (
                    not url_path.endswith("/")
                    and not url_path.startswith("PSA")
                    and not url.startswith("/")
                ):
                    url_path = url_path + "/"
                url = url_path + url
                # Remove .md at the end of URLs by default.
                match3 = re.search(r"(.*)\.md$", url)
                url = match3[1]
                # Creates a dictionary with basic metadata values
                # (i.e. source, URL, and md_hash)
                metadata_dict_main = {
                    "source": filename_no_ext,
                    "url": url,
                    "md_hash": md_hash,
                }
                # Merges dictionaries with main metadata and additional metadata
                metadata_dict_final = metadata_dict_main | metadata_dict_extra
                str_uuid_file = str(uuid_file)
                print("UUID: " + str_uuid_file)
                print("Markdown hash: " + str(md_hash))
                print("URL: " + url)
                if toFile and toFile.strip():
                    # Skip if the file size is larger than 10000 bytes (API limit)
                    filesize = len(toFile)
                    if filesize < 10000:
                        if md_hash != "" and str_uuid_file != "":
                            query = {}
                            # The query looks for the UUID, which is unique and
                            # compares to see if the hash has changed
                            query = collection.get(
                                include=["metadatas"],
                                ids=str_uuid_file,
                                where={"md_hash": {"$ne": md_hash}},
                            )
                            # Extract any id whose content may have changed
                            id_to_remove = query["ids"]
                            if id_to_remove != []:
                                print("Out of date content.")
                                # Delete the existing entry
                                collection.delete(ids=id_to_remove)
                                # Add a new entry
                                collection.add(
                                    documents=toFile,
                                    metadatas=metadata_dict_final,
                                    ids=str_uuid_file,
                                )
                                print("Updated.")
                                updated_count += 1
                                file_update = True
                            else:
                                query_2 = collection.get(
                                    include=["metadatas"],
                                    ids=str_uuid_file,
                                    where={"md_hash": {"$eq": md_hash}},
                                )
                                id_up_to_date = query_2["ids"]
                                if id_up_to_date != []:
                                    print("Up to date content.")
                                    unchanged_count += 1
                                else:
                                    collection.add(
                                        documents=toFile,
                                        metadatas=metadata_dict_final,
                                        ids=str_uuid_file,
                                    )
                                    print("Added content.")
                                    new_count += 1
                                    file_update = True
                        i += 1
                    else:
                        print(
                            "[Warning] Skipped "
                            + file
                            + " because the file size is too large!"
                        )
                else:
                    print("[Warning] Empty file!")
                print("")
                auto.close()
chroma_client.persist()
# results = collection.query(
#     query_texts=["What are some differences between apples and oranges?"],
#     n_results=3,
# )
# print("\nTesting:")
# print(results)

print("")
print("Total number of entries: " + str(i))
print("New entries: " + str(new_count))
print("Updated entries: " + str(updated_count))
print("Unchanged entries: " + str(unchanged_count))
