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
from tqdm import tqdm
from time import sleep
from absl import logging
from ratelimit import limits, sleep_and_retry

from chromadb.utils import embedding_functions
from chromadb.api.types import D, Embeddings

from docs_agent.models.google_genai import Gemini
from docs_agent.utilities import config
from docs_agent.utilities.config import ProductConfig, ReadConfig, Input
from docs_agent.utilities.helpers import (
    get_project_path,
    resolve_path,
    end_path_backslash,
    add_scheme_url,
)
from docs_agent.preprocess.splitters import markdown_splitter
from docs_agent.storage.google_semantic_retriever import SemanticRetriever


# Main function
def main():
    process_all_products()


class chromaAddSection:
    def __init__(
        self, section: markdown_splitter.Section, doc_title: str, metadata: dict = {}
    ):
        self.section = section
        self.doc_title = doc_title
        self.metadata = metadata


# Read plain text files (.md) from an input dir and
# add their content to the vector database.
# Embeddings are generated automatically as they are added to the database.
def populateToDbFromProduct(product_config: ProductConfig):
    """Populates the vector database with product documentation.

    Args:
        product_config: A ProductConfig object containing configuration details.
    """
    # Initialize Gemini object for embed function
    gemini_new = Gemini(models_config=product_config.models)
    # Use a chromadb function to initialize db
    embedding_function_gemini = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=product_config.models.api_key,
        model_name=product_config.models.embedding_model,
        task_type="RETRIEVAL_DOCUMENT",
    )

    # Temporary - This enables us to start chroma even with google_semantic_retriever
    # returning None
    for item in product_config.db_configs:
        if "chroma" in item.db_type:
            chroma_client = chromadb.PersistentClient(
                path=resolve_path(item.vector_db_dir)
            )
            collection = chroma_client.get_or_create_collection(
                name=item.collection_name,
                embedding_function=embedding_function_gemini,
            )
        # Hacky way of getting corpus_name from other db_type configs
        if "google_semantic_retriever" in item.db_type:
            corpus_name = item.corpus_name
    if product_config.db_type == "google_semantic_retriever":
        print("Initializing the Semantic Retrieval API for creating an online storage.")
        semantic = SemanticRetriever()
        for item in product_config.db_configs:
            if "google_semantic_retriever" in item.db_type:
                if semantic.does_this_corpus_exist(item.corpus_name) == False:
                    semantic.create_a_new_corpus(item.corpus_display, item.corpus_name)
    index, full_index_path = load_index(input_path=product_config.output_path)
    # Pre-calculates file count
    file_count = sum(len(files) for _, _, files in os.walk(product_config.output_path))
    # Prepare progress bars
    progress_bar = tqdm(
        total=file_count,
        position=0,
        bar_format="{percentage:3.0f}% | {n_fmt}/{total_fmt} | {elapsed}/{remaining} | {desc}",
    )
    progress_new_file = tqdm(position=1, desc="Total new files 0", bar_format="{desc}")
    progress_unchanged_file = tqdm(
        position=2, desc="Total unchanged files 0", bar_format="{desc}"
    )
    progress_update_file = tqdm(
        position=3, desc="Total updated files 0", bar_format="{desc}"
    )
    total_files = 0
    updated_count = 0
    new_count = 0
    unchanged_count = 0
    add_id_array = []
    add_content_array = []
    add_title_array = []
    add_metadata_array = []
    add_embedding_array = []
    delete_id_array = []
    for root, dirs, files in os.walk(product_config.output_path):
        # Makes the output path a fully resolved path
        fully_resolved_output = end_path_backslash(
            resolve_path(product_config.output_path)
        )
        for file in files:
            # Displays status bar, sleep helps to stick the progress
            progress_bar.update(1)
            progress_bar.set_description_str(f"Processing file {file}", refresh=True)
            # Persists every nth time and if there was an actual update or added file.
            # However, we don't need to persist, which takes time, if there are no updates.
            # Persist is now automatic
            full_file_name = resolve_path(os.path.join(root, "")) + file
            if file.endswith(".md"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                    # Extract the original filename used (without a file extension)
                    content_file = auto.read()
                    auto.close()
                content_file.strip()
                counter = 0
                for product in index:
                    # Returns Section object along with any additional metadata in a seperate dictionary, and a doc_title
                    # Title is built from page title and section title
                    # Can update progress bar with section info for debug
                    chroma_add_item = findFileinDict(
                        input_file_name=full_file_name,
                        dictionary_input=index[product],
                        content_file=content_file,
                    )
                # Skip if the file size is larger than 10000 bytes (API limit)
                if (
                    chroma_add_item.section.content != ""
                    and len(chroma_add_item.section.content) < 10000
                    and chroma_add_item.section.md_hash != ""
                    and chroma_add_item.section.uuid != ""
                ):
                    # The query looks for the UUID, which is unique and
                    # compares to see if the hash has changed
                    # Extract any id whose content may have changed
                    counter += 1
                    # Prepare for arrays, right now use a single value array
                    # TODO batch embedding creation
                    if counter == 1 or counter == len(index):
                        id_to_update = collection.get(
                            include=["metadatas"],
                            ids=chroma_add_item.section.uuid,
                            where={"md_hash": {"$ne": chroma_add_item.section.md_hash}},
                        )["ids"]
                        id_to_not_change = collection.get(
                            include=["metadatas"],
                            ids=chroma_add_item.section.uuid,
                            where={"md_hash": {"$eq": chroma_add_item.section.md_hash}},
                        )["ids"]
                        # Delete and Re-add content
                        if id_to_update != []:
                            # Add ids once to delete array, and then to add array
                            delete_id_array.append(chroma_add_item.section.uuid)
                            add_id_array.append(chroma_add_item.section.uuid)
                            add_content_array.append(chroma_add_item.section.content)
                            add_title_array.append(chroma_add_item.doc_title)
                            add_metadata_array.append(chroma_add_item.metadata)
                            try:
                                add_embedding_array.append(
                                    gemini_new.embed(
                                        content=chroma_add_item.section.content,
                                        task_type="RETRIEVAL_DOCUMENT",
                                        title=chroma_add_item.doc_title,
                                    )[0]
                                )
                            except:
                                next
                            if len(outdated) == 1 or counter == len(index):
                                logging.info(f"{str(len(outdated))} updated files.")
                                collection.delete(ids=oudated)
                                # Add a new entry
                                collection.add(
                                    documents=add_content_array,
                                    embeddings=add_embedding_array,
                                    metadatas=add_metadata_array,
                                    ids=add_id_array,
                                )
                                updated_count += len(id_to_update)
                                progress_bar_updated_file.update(1)
                                progress_bar_updated_file.set_description_str(
                                    f"Updated files {updated_count}", refresh=True
                                )
                                ### Also add this text chunk using the Semantic Retrieval API
                                if (
                                    product_config.db_type
                                    == "google_semantic_retriever"
                                ):
                                    # logging.error(f"Added a semantic chunk.")
                                    uuid_dict = {"UUID": chroma_add_item.section.uuid}
                                    dict_with_uuid = (
                                        chroma_add_item.metadata | uuid_dict
                                    )
                                    semantic.create_a_doc_chunk(
                                        corpus_name=corpus_name,
                                        page_title=chroma_add_item.section.page_title,
                                        metadata=dict_with_uuid,
                                        text=chroma_add_item.section.content,
                                    )
                                    logging.info(
                                        "Added the text chunk using the Semantic Retrieval API."
                                    )
                        # If section remained static
                        elif id_to_not_change != []:
                            qty_change = len(id_to_not_change)
                            progress_unchanged_file.update(qty_change)
                            unchanged_count += qty_change
                            progress_unchanged_file.set_description_str(
                                f"Total unchanged file {unchanged_count}",
                                refresh=True,
                            )
                        else:
                            add_id_array.append(chroma_add_item.section.uuid)
                            add_content_array.append(chroma_add_item.section.content)
                            add_title_array.append(chroma_add_item.doc_title)
                            add_metadata_array.append(chroma_add_item.metadata)
                            add_embedding_array.append(
                                gemini_new.embed(
                                    content=chroma_add_item.section.content,
                                    task_type="RETRIEVAL_DOCUMENT",
                                    title=chroma_add_item.doc_title,
                                )[0]
                            )
                            if len(add_id_array) == 1:
                                collection.add(
                                    documents=add_content_array,
                                    embeddings=add_embedding_array,
                                    metadatas=add_metadata_array,
                                    ids=add_id_array,
                                )
                                new_count += len(add_id_array)
                                progress_new_file.update(len(add_id_array))
                                progress_new_file.set_description_str(
                                    f"Total new files {new_count}", refresh=True
                                )
                                # Reset all arrays
                                add_id_array = []
                                add_content_array = []
                                add_title_array = []
                                add_metadata_array = []
                                add_embedding_array = []
                            ### Also add this text chunk using the Semantic Retrieval API
                            if product_config.db_type == "google_semantic_retriever":
                                uuid_dict = {"UUID": chroma_add_item.section.uuid}
                                dict_with_uuid = chroma_add_item.metadata | uuid_dict
                                try:
                                    semantic.create_a_doc_chunk(
                                        corpus_name=corpus_name,
                                        page_title=chroma_add_item.section.page_title,
                                        metadata=dict_with_uuid,
                                        text=chroma_add_item.section.content,
                                    )
                                    logging.info(
                                        "Added the text chunk using the Semantic Retrieval API."
                                    )
                                except:
                                    logging.error(dict_with_uuid)
                                    logging.error(chroma_add_item.section)
                                    logging.error(
                                        "Cannot add the text chunk using the Semantic Retrieval API."
                                    )
                    total_files += 1
                else:
                    if chroma_add_item.section.content == "":
                        logging.info(f"Skipped {file} because the file is empty.")
                    else:
                        logging.info(
                            f"Skipped {file} because the file is is too large {str(len(chroma_add_item.section.content))}"
                        )
            # Skips logging a warning if the file being walked is the index file
            elif full_file_name == full_index_path:
                next
            else:
                # Logs missing extensions from input directory that may be
                # processed
                file_name, extension = os.path.splitext(file)
                logging.warning(
                    f"Skipped {file} because there is no configured parser for extension {extension}"
                )

    print("")
    print(f"===========================================")
    print("Total number of entries: " + str(total_files))


def findFileinDict(input_file_name: str, dictionary_input: dict, content_file):
    metadata_dict_final = {}
    if input_file_name in dictionary_input:
        # If metadata exists, add these to a dictionary that is then
        # merged with other metadata values
        if "metadata" in dictionary_input[input_file_name]:
            # Save and flatten dictionary
            metadata_dict_extra = extract_extra_metadata(
                input_dictionary=dictionary_input[input_file_name]["metadata"]
            )
        else:
            metadata_dict_extra = {}
        section = markdown_splitter.DictionarytoSection(
            dictionary_input[input_file_name]
        )
        if "URL" in metadata_dict_extra:
            section.url = metadata_dict_extra["URL"]
        # Merges dictionaries with main metadata and additional metadata
        section.content = content_file
        # Combines Section db in dictionary with extra
        metadata_dict_final = section.encodeToChromaDBNoContent() | metadata_dict_extra
        # Overide title if it exists from frontmatter
        if "title" in metadata_dict_final:
            doc_title = str(metadata_dict_final["title"])
        else:
            doc_title = section.createChunkTitle()
        # print("Title: " + doc_title)
    else:
        doc_title = ""
        section = markdown_splitter.DictionarytoSection(metadata_dict_final)
        logging.info(f"{input_file_name} not found.")
    chroma_add = chromaAddSection(
        section=section, metadata=metadata_dict_final, doc_title=doc_title
    )
    return chroma_add


def load_index(
    input_path: str, input_index_name: str = "file_index.json"
) -> tuple[dict, str]:
    """Loads the file index.

    Args:
        input_path: The path to the input directory.

    Returns:
        A tuple containing the loaded index and the full index path.
    """
    full_index_path = resolve_path(end_path_backslash(input_path) + input_index_name)
    try:
        with open(full_index_path, "r", encoding="utf-8") as index_file:
            print("Using file index: " + full_index_path + "\n")
            index = json.load(index_file)
            return index, full_index_path
    except FileNotFoundError:
        logging.error(
            f"The file {full_index_path} does not exist. Re-chunk your project with docsAgent chunk"
        )
        return sys.exit(1)


# Given a ReadConfig object, process all products
# Default Read config defaults to source of project with config.yaml
# temp_process_path is where temporary files will be processed and then deleted
# defaults to /tmp
def process_all_products(
    config_file: ReadConfig = config.ReadConfig().returnProducts(),
):
    print(
        f"Starting to verify files to populate database for {str(len(config_file.products))} products.\n"
    )
    for product in config_file.products:
        print(f"===========================================")
        print(f"Processing product: {product.product_name}")
        print(f"Input directory: {resolve_path(product.output_path)}")
        print(f"Database operation db type: {product.db_type}")
        for item in product.db_configs:
            print(f"{item}")
        print(f"===========================================")
        populateToDbFromProduct(product_config=product)


def extract_extra_metadata(input_dictionary):
    metadata_dict_extra = flatdict.FlatterDict(
        input_dictionary,
        delimiter="_",
    )
    metadata_dict_extra = dict(metadata_dict_extra)
    return metadata_dict_extra


if __name__ == "__main__":
    main()
