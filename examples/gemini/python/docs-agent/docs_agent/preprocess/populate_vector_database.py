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

"""Populate vector databases with embeddings generated from text chunks."""

import json
import os
import re
import sys

from absl import logging

import flatdict
import tqdm

from docs_agent.preprocess.splitters import markdown_splitter
from docs_agent.storage.google_semantic_retriever import SemanticRetriever
from docs_agent.utilities import config
from docs_agent.utilities.config import ConfigFile
from docs_agent.utilities.config import ProductConfig
from docs_agent.utilities.helpers import end_path_backslash
from docs_agent.utilities.helpers import resolve_path
from docs_agent.storage.chroma import  ChromaEnhanced


class chromaAddSection:
    def __init__(
        self, section: markdown_splitter.Section, doc_title: str, metadata: dict = {}
    ):
        self.section = section
        self.doc_title = doc_title
        self.metadata = metadata


# Get the total number of files in a directory and its subdirectories.
def get_file_count_in_a_dir(path):
    file_count = sum(len(files) for _, _, files in os.walk(path))
    return file_count


# Return the relative path after the `docs-agent/data` path
def get_relative_path_and_filename(full_path: str):
    path_and_filename = full_path
    match = re.search(r".*\/docs-agent\/data\/(.*)$", full_path)
    if match:
        path_and_filename = match[1]
    return path_and_filename


# Prepare progres bars for showing files being processed and uploaded.
def init_progress_bars(file_count):
    print()
    main = tqdm.tqdm(
        total=file_count,
        position=0,
        bar_format="{percentage:3.0f}% | {n_fmt}/{total_fmt} | {elapsed}/{remaining} | {desc}",
    )
    new_file = tqdm.tqdm(position=1, desc="Total new files 0", bar_format="{desc}")
    unchanged_file = tqdm.tqdm(
        position=2, desc="Total unchanged files 0", bar_format="{desc}"
    )
    return main, new_file, unchanged_file


# Open a file and return its content.
def get_file_content(full_path):
    content_file = ""
    with open(full_path, "r", encoding="utf-8") as auto:
        content_file = auto.read()
        content_file.strip()
        auto.close()
    return content_file

# Upload a text chunk to an online stroage using the Semantic Retrieval API.
def upload_an_entry_to_a_corpus(
    semantic, corpus_name, document_name_in_corpus, this_item, is_this_first_chunk
):
    document_name = document_name_in_corpus
    # Check if a document for this chunk exists.
    if is_this_first_chunk == True:
        origin_uuid = ""
        if hasattr(this_item.section, "origin_uuid"):
            origin_uuid = this_item.section.origin_uuid
        try:
            # Create a new document
            document_name = semantic.create_a_doc(
                corpus_name=corpus_name,
                page_title=this_item.section.page_title,
                uuid=origin_uuid,
            )
        except:
            logging.error(
                f"Cannot create a new document using the Semantic Retrieval API: {str(this_item.section.page_title)}"
            )
    uuid_dict = {"UUID": this_item.section.uuid}
    dict_with_uuid = this_item.metadata | uuid_dict
    try:
        # Create a new chunk
        semantic.create_a_chunk(
            doc_name=document_name,
            text=this_item.section.content,
            metadata=dict_with_uuid,
        )
        logging.info("Added the text chunk using the Semantic Retrieval API.")
    except:
        logging.error(dict_with_uuid)
        logging.error(this_item.section)
        logging.error("Cannot add the text chunk using the Semantic Retrieval API.")
    return document_name


# Delete entries in the Chroma database if we cannot find matches in the current dataset.
def delete_unmatched_entries_in_chroma(
    product_config: ProductConfig, chroma_client, collection
):
    print()
    print(f"Scanning the Chroma database to identify entries to be deleted.")
    # Arrays to store IDs, text chunk filename, and md hashes of
    # the existing entries in the local Chroma vector database.
    existing_online_entry_ids = []
    existing_online_entry_text_chunk_filenames = []
    existing_online_entry_md_hashes = []
    # Get all entries in the vector database.
    all_entries = collection.get()
    for entry in all_entries["ids"]:
        # logging.error(f"ID: {entry}")
        existing_online_entry_ids.append(str(entry))
    for entry in all_entries["metadatas"]:
        # logging.error(f"Metadata: {entry}")
        text_chunk_filename = ""
        md_hash = ""
        if "text_chunk_filename" in entry:
            text_chunk_filename = entry["text_chunk_filename"]
        if "md_hash" in entry:
            md_hash = entry["md_hash"]
        # logging.error(f"Text chunk filename: {text_chunk_filename}")
        # logging.error(f"MD HASH: {md_hash}")
        existing_online_entry_text_chunk_filenames.append(str(text_chunk_filename))
        existing_online_entry_md_hashes.append(str(md_hash))

    # Examine the new candidate entries in the current `data` directory.
    candidate_entries = {}
    (index_object, full_index_path) = load_index(input_path=product_config.output_path)
    for product in index_object:
        dictionary_input = index_object[product]
    # Extract the text chunk name and hash from each chunk data.
    for item in dictionary_input:
        chunk_data = dictionary_input[item]
        text_chunk_filename = ""
        text_chunk_md_hash = ""
        # print(f"Candidate text chunk data: {chunk_data}")
        if "text_chunk_filename" in chunk_data:
            text_chunk_filename = chunk_data["text_chunk_filename"]
        if "md_hash" in chunk_data:
            text_chunk_md_hash = chunk_data["md_hash"]
        # print(f"Candidate text chunk filename: {text_chunk_filename}")
        if text_chunk_filename != "":
            candidate_entries[text_chunk_filename] = text_chunk_md_hash

    # Compare the existing online entries to the candidate entries.
    to_be_deleted_online_entry_ids = []
    index = 0
    for index, item in enumerate(existing_online_entry_text_chunk_filenames):
        existing_text_chunk = item
        existing_md_hash = existing_online_entry_md_hashes[index]
        existing_id = existing_online_entry_ids[index]
        if existing_text_chunk in candidate_entries:
            candidate_md_hash = candidate_entries[existing_text_chunk]
            if existing_md_hash != candidate_md_hash:
                logging.info(
                    f"The entry {existing_text_chunk} in the Chroma database "
                    + "will be deleted because its content has changed."
                )
                to_be_deleted_online_entry_ids.append(existing_id)
        else:
            logging.info(
                f"The entry {existing_text_chunk} in the Chroma database "
                + "will be deleted because it is no longer found in the current dataset."
            )
            to_be_deleted_online_entry_ids.append(existing_id)

    # Delete identified entries in the Chroma database.
    if to_be_deleted_online_entry_ids:
        collection.delete(ids=to_be_deleted_online_entry_ids)
        deleted_entries_count = len(to_be_deleted_online_entry_ids)
        print(f"Deleted entries count: {deleted_entries_count}")
    else:
        print(f"Keeping all existing entries in the Chroma database.")
    return to_be_deleted_online_entry_ids


# Delete entries in the online corpus if we cannot find matches in the current dataset.
def delete_unmatched_entries_in_online_corpus(
    product_config: ProductConfig, semantic_object, corpus_name
):
    print()
    print(f"Scanning the online corpus to identify chunks to be deleted.")
    print(f"(This may take some time.)")
    # Get all chunks in the online corpus.
    all_chunks = []
    all_docs = semantic_object.get_all_docs(corpus_name=corpus_name, print_output=False)
    for doc in all_docs:
        doc_name = str(doc.name)
        chunks = semantic_object.get_all_chunks(doc_name=doc_name, print_output=False)
        for chunk in chunks:
            all_chunks.append(chunk)

    # Examine the new candidate entries in the current `data` directory.
    candidate_entries = {}
    (index_object, full_index_path) = load_index(input_path=product_config.output_path)
    for product in index_object:
        dictionary_input = index_object[product]
    # Extract the text chunk name and hash from each chunk data.
    for item in dictionary_input:
        chunk_data = dictionary_input[item]
        text_chunk_filename = ""
        text_chunk_md_hash = ""
        # print(f"Candidate text chunk data: {chunk_data}")
        if "text_chunk_filename" in chunk_data:
            text_chunk_filename = chunk_data["text_chunk_filename"]
        if "md_hash" in chunk_data:
            text_chunk_md_hash = chunk_data["md_hash"]
        # print(f"Candidate text chunk filename: {text_chunk_filename}")
        if text_chunk_filename != "":
            candidate_entries[text_chunk_filename] = text_chunk_md_hash

    # Compare the existing online entries to the candidate entries.
    to_be_deleted_online_chunk_names = []
    for chunk in all_chunks:
        existing_chunk_name = chunk.name
        existing_md_hash = ""
        existing_text_chunk_filename = ""
        metadata = chunk.custom_metadata
        for item in metadata:
            if item.key == "md_hash":
                # print(f"md_hash: {item.string_value}")
                existing_md_hash = item.string_value
            elif item.key == "text_chunk_filename":
                # print(f"text_chunk_filename: {item.string_value}")
                existing_text_chunk_filename = item.string_value
        if existing_text_chunk_filename in candidate_entries:
            candidate_md_hash = candidate_entries[existing_text_chunk_filename]
            if existing_md_hash != candidate_md_hash:
                logging.info(
                    f"{existing_text_chunk_filename} in the online corpus "
                    + "will be deleted because its content has changed."
                )
                to_be_deleted_online_chunk_names.append(existing_chunk_name)
        else:
            logging.info(
                f"{existing_text_chunk_filename} in the online corpus will be "
                + "deleted because it is no longer found in the current dataset."
            )
            to_be_deleted_online_chunk_names.append(existing_chunk_name)

    # Delete identified chunks in the online corpus.
    if to_be_deleted_online_chunk_names:
        # Initialize a progress bar object.
        progress_bar = tqdm.tqdm(
            position=0, desc="Deleting the chunk", bar_format="{desc}"
        )
        # Loop for deleting chunks online.
        for chunk_name in to_be_deleted_online_chunk_names:
            # progress_bar.update(1)
            progress_bar.set_description_str(
                f"Deleting the chunk {chunk_name}", refresh=True
            )
            semantic_object.delete_a_chunk(chunk_name)
        delete_count = len(to_be_deleted_online_chunk_names)
        progress_bar.set_description_str(
            f"Deleted chunks count: {delete_count}", refresh=False
        )
    else:
        print(f"Keeping all existing chunks in the online corpus.")
    return to_be_deleted_online_chunk_names


# Read plain text files (.md) from an input dir and
# add their content to the vector database.
# Embeddings are generated automatically as they are added to the database.
def populateToDbFromProduct(product_config: ProductConfig):
    """Populates the vector database with product documentation.
    Args:
        product_config: A ProductConfig object containing configuration details.
    """
    logging.info("Starting populateToDbFromProduct")
    # Initialize variables
    chroma_collection = None
    semantic = None
    corpus_name = ""

    # Initialize Chroma database and collection
    for db_conf in product_config.db_configs:
        if "chroma" in db_conf.db_type:
            logging.info("Initializing Chroma.")
            try:
                chroma = ChromaEnhanced(
                    chroma_dir=resolve_path(db_conf.vector_db_dir),
                    models_config=product_config.models,
                )
                logging.info(f"Attempting to get or create collection '{db_conf.collection_name}'")
                chroma_collection = chroma.client.get_or_create_collection(
                    name=db_conf.collection_name,
                    embedding_function=chroma.embedding_function_instance,
                )
                logging.info(f"Successfully got or created collection '{db_conf.collection_name}'")
                # Delete unmatched entries in Chroma
                if (
                    hasattr(product_config, "enable_delete_chunks")
                    and product_config.enable_delete_chunks == "True"
                ):
                    delete_unmatched_entries_in_chroma(
                        product_config, chroma.client, chroma_collection
                    )
                break
            except Exception as e:
                logging.error(f"Failed to initialize Chroma DB or collection '{db_conf.collection_name}': {e}", exc_info=True)
                return

    # Initialize Semantic Retrieval API (if enabled)
    if ("google_semantic_retriever" in product_config.db_type):
        logging.info("Initializing the Semantic Retrieval API for an online storage.")
        semantic = SemanticRetriever()
        for db_conf in product_config.db_configs:
            if "google_semantic_retriever" in db_conf.db_type:
                corpus_name = db_conf.corpus_name
                try:
                    if not semantic.does_this_corpus_exist(corpus_name):
                        semantic.create_a_new_corpus(db_conf.corpus_display, corpus_name)
                    elif (
                        hasattr(product_config, "enable_delete_chunks")
                        and product_config.enable_delete_chunks == "True"
                    ):
                        delete_unmatched_entries_in_online_corpus(
                            product_config, semantic, corpus_name
                        )
                    break
                except Exception as e:
                    logging.error(f"Failed to initialize Semantic Retriever Corpus '{corpus_name}': {e}", exc_info=True)
                    semantic = None
                break

    # Check for Chroma collection initialization
    if chroma_collection is None and any("chroma" in db_conf.db_type for db_conf in product_config.db_configs):
        logging.error("Chroma collection could not be initialized. Aborting population.")
        return

    # Load the index file
    logging.info(f"Loading file index... {product_config.output_path}")
    index, full_index_path = load_index(input_path=product_config.output_path)
    logging.info("File index loaded.")
    # Resolve the output path
    resolved_walk_path = resolve_path(product_config.output_path)
    logging.info(f"Starting file processing in directory: {resolved_walk_path}")
    if not os.path.isdir(resolved_walk_path):
        logging.error(f"Target directory does not exist or is not a directory: {resolved_walk_path}")
        return

    # Get the file count in the directory
    file_count = get_file_count_in_a_dir(resolved_walk_path)
    logging.info(f"Using os.walk file count ({file_count}) for main progress bar.")
    # Initialize progress bars
    progress_bar, progress_new_file, progress_unchanged_file = init_progress_bars(file_count)

    # Counters
    total_files_processed = 0
    new_count = 0
    unchanged_count = 0
    skipped_invalid_uuid_count = 0
    skipped_other_count = 0

    # Semantic Retriever state
    document_name_in_corpus = ""
    dict_document_names_in_corpus = {}

    # Loop through the files in the directory
    for root, dirs, files in os.walk(resolved_walk_path):
        for file in files:
            # Update main progress bar based on os.walk count total
            progress_bar.update(1)
            progress_bar.set_description_str(f"Processing file {file}", refresh=True)
            full_file_name = os.path.join(root, file)
            # Skip the index file itself
            if full_file_name == full_index_path:
                continue
            if file.endswith(".md"):
                try:
                    content_file = get_file_content(full_file_name)
                    chroma_add_item = findFileinDict(
                        input_file_name=full_file_name,
                        index_object=index,
                        content_file=content_file,
                    )
                    # Check for invalid content
                    if not chroma_add_item.section.content:
                        logging.warning(f"Skipping {file}: Content is empty.")
                        skipped_other_count += 1
                        continue
                    if len(chroma_add_item.section.content) >= 10000:
                        logging.warning(f"Skipping {file}: Content too large ({len(chroma_add_item.section.content)} bytes).")
                        skipped_other_count += 1
                        continue
                    if not chroma_add_item.section.md_hash:
                         logging.warning(f"Skipping {file}: Missing md_hash in index data.")
                         skipped_other_count += 1
                         continue

                    # Check for invalid UUID
                    uuid_value = chroma_add_item.section.uuid
                    if not isinstance(uuid_value, str) or not uuid_value:
                        logging.error(f"File {file}: Invalid UUID detected ({repr(uuid_value)}). Skipping operation for this file.")
                        skipped_invalid_uuid_count += 1
                        continue
                    id_to_not_change = []
                    # Check for Chroma collection existence
                    if chroma_collection:
                        try:
                            ids_to_check = [uuid_value]
                            get_result = chroma_collection.get(
                                ids=ids_to_check,
                                where={"md_hash": {"$eq": chroma_add_item.section.md_hash}},
                                include=[],
                            )
                            id_to_not_change = get_result["ids"]
                        except Exception as e:
                            if "does not exist" in str(e).lower():
                                 id_to_not_change = []
                            else:
                                 logging.warning(f"File {file}: Error in Chroma to get for ID {uuid_value}: {e}")
                                 id_to_not_change = []

                    # Check for existing entry with same hash
                    if id_to_not_change:
                        # Exists with same hash -> Unchanged
                        qty_change = len(id_to_not_change)
                        unchanged_count += qty_change
                        total_files_processed += qty_change
                        progress_unchanged_file.update(qty_change)
                        progress_unchanged_file.set_description_str(f"Total unchanged files {unchanged_count}", refresh=True)
                    else:
                        # New or updated entry
                        if chroma_collection:
                            try:
                                doc_list = [chroma_add_item.section.content]
                                meta_list = [chroma_add_item.metadata]
                                id_list = [uuid_value]
                                # Upsert the entry
                                chroma_collection.upsert(
                                    documents=doc_list,
                                    metadatas=meta_list,
                                    ids=id_list,
                                )
                                new_count += 1
                                total_files_processed += 1
                                progress_new_file.update(1)
                                progress_new_file.set_description_str(f"Total new/updated files {new_count}", refresh=True)

                            except Exception as e:
                                # Keep this error log
                                logging.error(f"Error during collection.upsert for ID {uuid_value}: {e}", exc_info=True)
                                skipped_other_count += 1
                        else:
                             logging.warning(f"File {file}: Skipping add/upsert because Chroma collection is not available.")
                             skipped_other_count += 1

                        # Check for Semantic Retriever initialization
                        if semantic and corpus_name:
                            file_page_prefix = full_file_name
                            is_this_first_chunk = True
                            match_file_page = re.search(r"(.*)_\d+\.md$", full_file_name)
                            if match_file_page:
                                file_page_prefix = match_file_page.group(1)
                                if file_page_prefix in dict_document_names_in_corpus:
                                    document_name_in_corpus = dict_document_names_in_corpus[file_page_prefix]
                                    is_this_first_chunk = False
                                else:
                                     document_name_in_corpus = ""

                            try:
                                document_name = upload_an_entry_to_a_corpus(
                                    semantic,
                                    corpus_name,
                                    document_name_in_corpus,
                                    chroma_add_item,
                                    is_this_first_chunk,
                                )
                                dict_document_names_in_corpus[file_page_prefix] = document_name
                            except Exception as e:
                                logging.error(f"Failed to upload chunk for {file} to Semantic Retriever: {e}", exc_info=True)

                except Exception as e:
                    # Keep this error log for file-level processing errors
                    logging.error(f"Error processing file {full_file_name}: {e}", exc_info=True)
                    skipped_other_count += 1
            else:
                 # Skip non-markdown files
                 pass

    # Close all progress bars
    progress_bar.set_description_str(f"Finished processing.", refresh=True)
    progress_bar.close()
    progress_new_file.close()
    progress_unchanged_file.close()

    # Simplified final summary print
    print(f"\nProcessing Summary:")
    print(f"  Total files found for database: {total_files_processed}")
    print(f"  New or updated files:   {new_count}")
    print(f"  Unchanged files:     {unchanged_count}")
    # Optionally report skipped counts if they are non-zero, otherwise omit for cleaner output
    if skipped_invalid_uuid_count > 0:
        print(f"  Skipped (Invalid UUID):  {skipped_invalid_uuid_count}")
    if skipped_other_count > 0:
        print(f"  Skipped (Other reasons): {skipped_other_count}")

    print(f"\nFinished processing and generating embeddings for all files.")
    if any("chroma" in db_conf.db_type for db_conf in product_config.db_configs):
        print("Finalized generation of embeddings for all files in Chroma DB.")


def findFileinDict(input_file_name: str, index_object, content_file):
    metadata_dict_final = {}
    for product in index_object:
        dictionary_input = index_object[product]
    if input_file_name in dictionary_input:
        chunk_data = dictionary_input[input_file_name]
        # Extract the text chunk name from the index object.
        text_chunk_filename = ""
        if "text_chunk_filename" in chunk_data:
            text_chunk_filename = chunk_data["text_chunk_filename"]
            # logging.error(f"Chunk name: {text_chunk_filename}")
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
        # Add the text chunk filename to the metadata.
        if text_chunk_filename != "":
            metadata_dict_final["text_chunk_filename"] = text_chunk_filename
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


# Load the file index information from the file_index.json file.
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
            logging.info("Using file index: " + full_index_path + "\n")
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
    config_file: ConfigFile = config.ReadConfig().returnProducts(),
):
    print(
        f"Starting to verify files to populate database for {str(len(config_file.products))} products.\n"
    )
    for product in config_file.products:
        print(f"===========================================")
        print(f"Processing product: {product.product_name}")
        print(f"Input directory: {resolve_path(product.output_path)}")
        print(f"Database operation db type: {product.db_type}")
        print()
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
