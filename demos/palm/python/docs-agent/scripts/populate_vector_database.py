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
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from chromadb.api.types import D, Embeddings
import google.generativeai as palm
from ratelimit import limits, sleep_and_retry
import read_config

import markdown_splitter
from aqa import AQA

### Notes on how to use this script ###
#
# Prerequisites:
# - Have plain text files stored in the PLAIN_TEXT_DIR directory
#   (see `markdown_to_plain_text.py`)
#
# Do the following:
# 1. If you are not using the config.yaml file,
#    edit PLAIN_TEXT_DIR in this script (see below).
# 2. Run:
#    $ python3 ./scripts/populate-vector-database.py
#
# To test, run:
# $ python3 ./script/test-vector-database.py
#

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
### Select the input directory of plain text files, this will be overridden by
### the config.yaml file.
### Set up the path to the local LLM ###
LOCAL_VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_stores/chroma")
COLLECTION_NAME = "docs_collection"
PALM_API_ENDPOINT = "generativelanguage.googleapis.com"
EMBEDDING_MODEL = None
DB_TYPE = "LOCAL_DB"

IS_CONFIG_FILE = True
if IS_CONFIG_FILE:
    config_values = read_config.ReadConfig()
    PLAIN_TEXT_DIR = config_values.returnConfigValue("output_path")
    input_len = config_values.returnInputCount()
    LOCAL_VECTOR_DB_DIR = config_values.returnConfigValue("vector_db_dir")
    COLLECTION_NAME = config_values.returnConfigValue("collection_name")
    PALM_API_ENDPOINT = config_values.returnConfigValue("api_endpoint")
    EMBEDDING_MODEL = config_values.returnConfigValue("embedding_model")
    DB_TYPE = config_values.returnConfigValue("db_type")
    PRODUCT_NAME = config_values.returnConfigValue("product_name")

### Select the file index that is generated with your plain text files, same directory
INPUT_FILE_INDEX = "file_index.json"

# Select the type of embeddings to use, PALM or LOCAL
EMBEDDINGS_TYPE = "PALM"

### Set up the PaLM API key from the environment ###
API_KEY = os.getenv("PALM_API_KEY")
if API_KEY is None:
    sys.exit("Please set the environment variable PALM_API_KEY to be your API key.")

# Gemini API call limit is 1500 per minute. Reduce to 1400
API_CALLS = 1400
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
    palm.configure(api_key=API_KEY, client_options={"api_endpoint": PALM_API_ENDPOINT})
    # Scan the list of PaLM models.
    models = [
        m
        for m in palm.list_models()
        if "embedText" in m.supported_generation_methods
        or "embedContent" in m.supported_generation_methods
    ]
    if EMBEDDING_MODEL != None:
        # If `embedding_model` is specified in the `config.yaml` file, select that model.
        found_model = False
        for m in models:
            if m.name == EMBEDDING_MODEL:
                MODEL = m
                print("[INFO] Embedding model is set to " + str(m.name) + "\n")
                found_model = True
        if found_model is False:
            sys.exit("[ERROR] Cannot find the embedding model: " + str(EMBEDDING_MODEL))
    else:
        # By default, pick the first model on the list (likely "models/embedding-gecko-001")
        MODEL = models[0]
elif EMBEDDINGS_TYPE == "LOCAL":
    MODEL = os.path.join(BASE_DIR, "models/all-mpnet-base-v2")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL)
else:
    MODEL = os.path.join(BASE_DIR, "models/all-mpnet-base-v2")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL)

chroma_client = chromadb.PersistentClient(path=LOCAL_VECTOR_DB_DIR)

# Create embed function for PaLM
# API call limit to 5 qps
@sleep_and_retry
@limits(calls=API_CALLS, period=API_CALL_PERIOD)
# Input the document along with the page title
def embed_function(input: D, title: str = None) -> Embeddings:
    # Embed the documents using any supported method
    if str(MODEL.name) == "models/embedding-001":
        # Use the new `embed_content()` method if it's the new Gemini embedding model.
        # Set task_type to RETRIEVAL_DOCUMENT to store docs
        return [
            palm.embed_content(model=MODEL, content=input, task_type="RETRIEVAL_DOCUMENT", title=title)["embedding"]
        ]
    else:
        return [
            palm.generate_embeddings(model=MODEL, text=input)["embedding"]
        ]

# Use a chromadb function to initialize db
embedding_function_gemini = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=API_KEY, model_name="models/embedding-001", task_type="RETRIEVAL_DOCUMENT")

if EMBEDDINGS_TYPE == "PALM":
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_function_gemini
    )
elif EMBEDDINGS_TYPE == "LOCAL":
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=emb_fn
    )
else:
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=emb_fn
    )

# Main function
def main():
    # documents = []
    # metadatas = []
    # ids = []
    i = 0
    updated_count = 0
    new_count = 0
    unchanged_count = 0

    # Initialize variables for the Semantic Retrieval API
    corpus_display = PRODUCT_NAME + " documentation"
    corpus_name = "corpora/" + PRODUCT_NAME.lower().replace(" ", "-")

    # If using an online stroage using the Semantic Retrieval API,
    # try to create a new corpus.
    if DB_TYPE == "ONLINE_STORAGE":
        print("Initializing the Semantic Retrieval API for creating an online storage.")
        aqa = AQA()
        # List existing corpora
        aqa.list_existing_corpora()
        # Delete an existing corpus
        # aqa.delete_a_corpus(corpus_name)
        aqa.create_a_new_corpus(corpus_display, corpus_name)
        # exit(0)

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
                    auto.close()
                    # Contruct the URL
                    match2 = re.search(r"(.*)_\d*$", filename_no_ext)
                    filename_for_url = match2[1]
                    clean_filename = re.sub(PLAIN_TEXT_DIR, "", os.path.join(root, ""))
                    url = clean_filename + filename_for_url + ".md"
                    url_path = ""
                    md_hash = ""
                    uuid_file = ""
                    origin_uuid = ""
                    section_name_id = ""
                    # Build the full filename to match entries in file_index.json
                    # Using the full path avoids mismatches
                    full_file_name = FULL_BASE_DIR + clean_filename + file
                    metadata_dict_extra = {}
                    # Flag to see if there is a predefined URL from frontmatter
                    final_url = False
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
                                # Extracts user specified URL
                                if "URL" in metadata_dict_extra:
                                    final_url = True
                                    final_url_value = metadata_dict_extra["URL"]
                            else:
                                metadata_dict_extra = {}
                            attr_main = ["URL", "md_hash"]
                            # Matches keys for Section object
                            attr_section = [
                                "section_id",
                                "section_name_id",
                                "section_title",
                                "page_title",
                                "section_level",
                                "previous_id",
                                "parent_tree",
                                "token_estimate",
                            ]
                            attr_array_values = {}
                            # attr_array_int = ["UUID"]
                            for key_metadata in attr_section:
                                if key_metadata in index[key][full_file_name]:
                                    attr_array_values[key_metadata] = str(
                                        index[key][full_file_name][key_metadata]
                                    )
                                else:
                                    attr_array_values[key_metadata] = ""
                            if "UUID" in index[key][full_file_name]:
                                uuid_file = index[key][full_file_name]["UUID"]
                            if "md_hash" in index[key][full_file_name]:
                                md_hash = str(index[key][full_file_name]["md_hash"])
                            if "origin_uuid" in index[key][full_file_name]:
                                origin_uuid = index[key][full_file_name]["origin_uuid"]
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
                    # Replaces the URL if it comes from frontmatter
                    if final_url:
                        url = final_url_value
                    # Creates a dictionary with basic metadata values
                    # (i.e. source, URL, and md_hash)
                    # Add protocol to URL
                    metadata_dict_main = {
                        "source": filename_no_ext,
                        "origin_uuid": origin_uuid,
                        "url": markdown_splitter.add_scheme_url(url=url, scheme="https"),
                        "md_hash": md_hash,
                    }
                    # Merges dictionaries with main metadata and additional metadata
                    metadata_dict_final = metadata_dict_main | metadata_dict_extra
                    str_uuid_file = str(uuid_file)
                    if toFile:
                        toFile.strip()
                        # Skip if the file size is larger than 10000 bytes (API limit)
                        filesize = len(toFile)
                        if filesize < 10000:
                            # Build the section object to be saved in the database
                            section_to_db = markdown_splitter.Section(
                                attr_array_values["section_id"],
                                attr_array_values["section_name_id"],
                                attr_array_values["page_title"],
                                attr_array_values["section_title"],
                                attr_array_values["section_level"],
                                attr_array_values["previous_id"],
                                attr_array_values["parent_tree"],
                                attr_array_values["token_estimate"],
                                toFile,
                            )
                            # Converts Section object into a metadata dictionary
                            # of Section for chroma db
                            if attr_array_values["section_id"] != "":
                                metadata_for_chroma = section_to_db.encodeToChromaDBNoContent()
                            else:
                                metadata_for_chroma = {}
                            # Adds a section header to the URL, except header 1
                            if (section_to_db.name_id != "" and int(section_to_db.level) != 1):
                                url += "#" + section_to_db.name_id
                                metadata_dict_final.update({"url": url})
                            metadata_dict_final = metadata_dict_final | metadata_for_chroma
                            print("UUID: " + str_uuid_file)
                            # Added from AQA change - Check
                            doc_title = "None"
                            if "title" in metadata_dict_extra:
                                doc_title = str(metadata_dict_extra["title"])
                            doc_title = section_to_db.page_title
                            if (section_to_db.page_title == section_to_db.section_title):
                                doc_title = section_to_db.page_title
                            else:
                                doc_title = section_to_db.page_title + " - " + section_to_db.section_title
                            print("Title: " + doc_title)
                            # Make a section object from the metadata dictionary
                            # final_section = markdown_splitter.Section.decodeFromChromaDB(metadata_dict_final)
                            # print(final_section)
                            print (metadata_dict_final)
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
                                        documents=section_to_db.content,
                                        # Title is built from page title and section title
                                        embeddings=embed_function(input=section_to_db.content, title=doc_title)[0],
                                        metadatas=metadata_dict_final,
                                        ids=str_uuid_file,
                                    )
                                    print("Updated.")
                                    updated_count += 1
                                    file_update = True
                                    ### Also add this text chunk using the Semantic Retrieval API
                                    if DB_TYPE == "ONLINE_STORAGE":
                                        aqa.create_a_doc_chunk(
                                            corpus_name, doc_title, url, toFile
                                        )
                                        print(
                                            "Added the text chunk using the Semantic Retrieval API."
                                        )
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
                                            documents=section_to_db.content,
                                            # Title is built from page title and section title
                                            embeddings=embed_function(input=section_to_db.content, title=doc_title)[0],
                                            metadatas=metadata_dict_final,
                                            ids=str_uuid_file,
                                        )
                                        print("Added content.")
                                        new_count += 1
                                        file_update = True
                                        ### Also add this text chunk using the Semantic Retrieval API
                                        if DB_TYPE == "ONLINE_STORAGE":
                                            aqa.create_a_doc_chunk(
                                                corpus_name, doc_title, url, toFile
                                            )
                                            print(
                                                "Added the text chunk using the Semantic Retrieval API."
                                            )
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

    print("")
    print("Total number of entries: " + str(i))
    print("New entries: " + str(new_count))
    print("Updated entries: " + str(updated_count))
    print("Unchanged entries: " + str(unchanged_count))

if __name__ == "__main__":
    main()