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

"""Process Markdown files into plain text"""

from markdown import markdown
import shutil
from bs4 import BeautifulSoup
import os
import re
import json
import frontmatter
import read_config
import tokenCount
import markdown_splitter
import html_splitter
from modules import palm as palmModule
import uuid

# This function pre-processes files before they are actually chunked.
# This allows it to resolve includes of includes, Jinja templates, etc...
# TODO support Jinja, for this need to support data filters as well
# {% set doc | jsonloads %} and {% set teams | yamlloads %}
def pre_process_doc_files(configs, inputpath, counter, excludepath, include_path_html, temp_path):
    temp_output = os.path.join(temp_path, MY_OUTPUT_PATH)
    # Delete directory if it exits, then create it.
    if os.path.exists(temp_output):
        shutil.rmtree(temp_output)
        os.makedirs(temp_output)
    else:
        os.makedirs(temp_output)
    for root, dirs, files in os.walk(resolve_path(inputpath, BASE_DIR)):
        if IS_CONFIG_FILE:
            if "exclude_path" in configs[counter]:
                dirs[:] = [d for d in dirs if d not in excludepath]
        for file in files:
            # Process only Markdown files that do not begin with _(those should
            # be imported)
            # Construct a new sub-directory for storing output plain text files
            dir_path = os.path.join(temp_output, os.path.relpath(root, inputpath))
            is_exist = os.path.exists(dir_path)
            if not is_exist:
                #print(f"New path: {dir_path}")
                os.makedirs(dir_path)
            relative_path = make_relative_path(file=file, root=root, inputpath=inputpath)
            final_filename = temp_output + "/" + relative_path
            if file.startswith("_") and file.endswith(".md"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                # Read the input Markdown content
                    content = auto.read()
                    auto.close()
                # Do things
                #print(f"MD: {temp_output}/{relative_path}")
                # Process includes lines in Markdown
                file_with_include = markdown_splitter.process_markdown_includes(
                    content, root
                )
                # Process include lines in HTML
                file_with_include = html_splitter.process_html_includes(
                    file_with_include, include_path_html
                )
                with open(final_filename, "w", encoding="utf-8") as new_file:
                    #print(f"Saving {final_filename}")
                    new_file.write(content)
                    new_file.close()
            elif file.startswith("_") and (file.endswith(".html") or file.endswith(".htm")):
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                # Read the input HTML content
                    content = auto.read()
                    auto.close()
                # Do things
                #print(f"HTML: {file}")
                with open(final_filename, "w", encoding="utf-8") as new_file:
                    new_file.write(content)
                    new_file.close()
            else:
                # Just copy files that that we don't need to preprocess
                # Such as images or files without underscores
                #print(f"Non-formatted file: {file}")
                initial_file = os.path.join(root, file)
                #print(f"Copying {initial_file} to {final_filename}")
                shutil.copyfile(initial_file, final_filename)
    # Return the temporary directory, which can then be deleted once files are fully processed
    return temp_output

# This function processes files in the `input_path` directory
# into plain text files.
# Supports: Markdown files
# Includes are processed again since preprocess resolves the includes in
# Files prefixed with _ which indicates they are not standalone
def process_files_from_source(configs, inputpath, counter, excludepath, include_path_html):
    f_count = 0
    md_count = 0
    html_count = 0
    file_index = []
    full_file_metadata = {}
    for root, dirs, files in os.walk(resolve_path(inputpath, BASE_DIR)):
        if IS_CONFIG_FILE:
            if "exclude_path" in configs[counter]:
                dirs[:] = [d for d in dirs if d not in excludepath]
            if "url_prefix" in configs[counter]:
                namespace_uuid = uuid.uuid3(
                    uuid.NAMESPACE_DNS, configs[counter]["url_prefix"]
                )
                url_prefix = configs[counter]["url_prefix"]
            if "path" in configs[counter]:
                # This value is used to use the correct source and not a
                # temporary directory
                original_input = configs[counter]["path"]
        for file in files:
            # Construct a new sub-directory for storing output plain text files
            new_path = resolved_output_path + re.sub(
                resolve_path(inputpath, BASE_DIR), "", os.path.join(root, "")
            )
            is_exist = os.path.exists(new_path)
            if not is_exist:
                os.makedirs(new_path)
            relative_path = make_relative_path(file=file, root=root, inputpath=inputpath)
            if file.endswith(".md") and not file.startswith("_"):
                md_count += 1
                # Add filename to a list
                file_index.append(relative_path)
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                    # Read the input Markdown content
                    to_file = auto.read()
                    # Process includes lines in Markdown
                    file_with_include = markdown_splitter.process_markdown_includes(
                        to_file, root
                    )
                    # Process include lines in HTML
                    file_with_include = html_splitter.process_html_includes(
                        file_with_include, include_path_html
                    )
                    # This is an estimate of the token count
                    page_token_estimate = tokenCount.returnHighestTokens(
                        file_with_include
                    )
                    if USE_CUSTOM_MARKDOWN_SPLITTER == "token_splitter":
                        # Returns an array of Section objects along with a Page
                        # Object that contains metadata
                        (
                            page_sections,
                            page,
                        ) = markdown_splitter.process_markdown_page(file_with_include)
                        chunk_number = 0
                        for section in page_sections:
                            filename_to_save = make_chunk_name(new_path=new_path, file=file, index=chunk_number, extension="md")
                            #print(page)
                            #print(section)
                            # Generate UUID for each plain text chunk and collect its metadata,
                            # which will be written to the top-level `file_index.json` file.
                            md_hash = uuid.uuid3(namespace_uuid, section.content)
                            uuid_file = uuid.uuid3(namespace_uuid, filename_to_save)
                            origin_uuid = uuid.uuid3(namespace_uuid, relative_path)
                            # If no URL came from frontmatter, assign URL from config
                            if page.URL == "":
                                page.URL = markdown_splitter.add_scheme_url(url=url_prefix, scheme="https")
                            # Adds additional info so that the section can know its origin
                            full_file_metadata[filename_to_save] = {
                                "UUID": str(uuid_file),
                                "origin_uuid": str(origin_uuid),
                                "source": str(original_input),
                                "source_file": str(relative_path),
                                "source_id": int(counter),
                                "page_title": str(section.page_title),
                                "section_title": str(section.section_title),
                                "section_name_id": str(section.name_id),
                                "section_id": int(section.id),
                                "section_level": int(section.level),
                                "previous_id": int(section.previous_id),
                                "URL": str(page.URL),
                                "md_hash": str(md_hash),
                                "token_estimate": float(section.token_count),
                                "full_token_estimate": float(page_token_estimate),
                                "parent_tree": list(section.parent_tree),
                                "metadata": dict(page.metadata),
                            }
                            with open(
                                filename_to_save, "w", encoding="utf-8"
                            ) as new_file:
                                new_file.write(section.content)
                                new_file.close()
                            chunk_number += 1
                        auto.close()
                    elif USE_CUSTOM_MARKDOWN_SPLITTER == "process_sections":
                        # Use a custom splitter to split into small chunks
                        to_file, metadata = markdown_splitter.process_page_and_section_titles(to_file)
                        to_file = markdown_splitter.process_markdown_includes(to_file, root)
                        docs = markdown_splitter.process_document_into_sections(to_file)
                        #doc = []
                        chunk_number = 0
                        for doc in docs:
                            filename_to_save = make_chunk_name(new_path=new_path, file=file, index=chunk_number, extension="md")
                            # Clean up Markdown and HTML syntax
                            content = markdown_splitter.markdown_to_text(doc)
                            # Generate UUID for each plain text chunk and collect its metadata,
                            # which will be written to the top-level `file_index.json` file.
                            md_hash = uuid.uuid3(namespace_uuid, file_with_include)
                            uuid_file = uuid.uuid3(namespace_uuid, filename_to_save)
                            full_file_metadata[filename_to_save] = {
                                "UUID": str(uuid_file),
                                "source": original_input,
                                "source_file": relative_path,
                                "source_id": counter,
                                "URL": url_prefix,
                                "md_hash": str(md_hash),
                                "metadata": metadata,
                            }
                            with open(filename_to_save, "w", encoding="utf-8") as new_file:
                                new_file.write(content)
                                new_file.close()
                            chunk_number += 1
                        auto.close()
                    else:
                        # Exits if no valid markdown splitter
                        print("Select a valid USE_CUSTOM_MARKDOWN_SPLITTER option\n")
                        exit()
            elif (file.endswith(".htm") or file.endswith(".html")) and not file.startswith("_"):
                html_count += 1
                # Add filename to a list
                file_index.append(relative_path)
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                    # Read the input HTML content
                    to_file = auto.read()
                    # Process includes lines in HTML
                    file_with_include = html_splitter.process_html_includes(
                        to_file, include_path_html
                    )
                    #print (to_file)
    # Counts actually processed files
    f_count = md_count + html_count
    print("Processed " + str(f_count) + " files from the source: " + inputpath)
    print(str(md_count) + " Markdown files.")
    print(str(html_count) + " HTML files.")
    #print("Processed " + str(f_count) + " Markdown files from the source: " + inputpath)
    return f_count, md_count, html_count, file_index, full_file_metadata

# Write the recorded input variables into a file: `file_index.json`
def save_file_index_json(src_file_index):
    json_out_file = resolved_output_path + "/file_index.json"
    with open(json_out_file, "w", encoding="utf-8") as outfile:
        json.dump(src_file_index, outfile)
    print(
        "Created " + json_out_file + " to store the complete list of processed files."
    )

# Given a file, root, and inputpath, make a relative path
def make_relative_path(file: str, root: str, inputpath: str) -> str:
    file_slash = "/" + file
    relative_path = os.path.relpath(root + file_slash, inputpath)
    return relative_path

# Given a path, file, chunk index, and an optional path extension (to save chunk)
# Create a chunk name
def make_chunk_name(new_path: str, file: str, index: int, extension: str = "md") -> str:
    # Grab the filename without the .md extension
    new_filename = os.path.join(new_path, file)
    match = re.search(r"(.*)\.md$", new_filename)
    new_filename_no_ext = match[1]
    # Save clean plain text to a new filename appended with an index
    filename_to_save = (new_filename_no_ext + "_" + str(index) + "." + extension)
    return filename_to_save

def main():
    #### Main ####
    source_file_index = {}
    input_counter = 0
    total_file_count = 0
    total_md_count = 0
    total_html_count = 0
    # Main for-loop
    for input_counter in range(input_len):
        full_file_metadata = {}
        # file_index = []
        exclude = []
        # Process config.yaml into input variables.
        if IS_CONFIG_FILE:
            # Reads all the input values defined in the configuration file
            config_values = config.returnConfigValue("input")
            if "path" in config_values[input_counter]:
                input_path = config_values[input_counter]["path"]
            if "url_prefix" in config_values[input_counter]:
                url_prefix = config_values[input_counter]["url_prefix"]
            if "exclude_path" in config_values[input_counter]:
                exclude = config_values[input_counter]["exclude_path"]
            if "include_path_html" in config_values[input_counter]:
                include_path_html = config_values[input_counter]["include_path_html"]
            else:
                include_path_html = config_values[input_counter]["path"]
        else:
            input_path = MY_INPUT_PATH[input_counter]
            url_prefix = URL_PREFIX[input_counter]
        # Pre-process files in input dirs. This resolves includes, particularly
        # in files prefixed by _. Return the temp_output directory which can be
        # used as an input to process files
        temp_output = pre_process_doc_files(config_values, input_path, input_counter, exclude, include_path_html, "/tmp")
        print(f"Temp: {temp_output}")
        # Process Markdown files in the `input` path
        file_count, md_count, html_count, file_index, full_file_metadata = process_files_from_source(
            config_values, temp_output, input_counter, exclude, include_path_html
        )
        # Clear the temp_output
        shutil.rmtree(temp_output)
        if not input_path.endswith("/"):
            input_path = input_path + "/"
        input_path = resolve_path(input_path, BASE_DIR)
        # Record the input variables used in this path.
        file_list = {}
        for file in file_index:
            file_obj = {file: {"source": input_path, "URL": url_prefix}}
            file_list[file] = file_obj
        source_file_index[input_counter] = full_file_metadata
        input_counter += 1
        total_file_count += file_count
        total_md_count += md_count
        total_html_count += html_count
    # Write the recorded input variables into `file_index.json`.
    save_file_index_json(source_file_index)
    print(
        "Processed a total of "
        + str(total_file_count)
        + " files from "
        + str(input_counter)
        + " sources.\n"
        + str(total_md_count)
        + " Markdown files.\n"
        + str(total_html_count)
        + " HTML files."
    )

def resolve_path(rel_or_abs_path: str, base_dir: str):
    path = rel_or_abs_path.strip()
    if path.startswith("/"):
        return path
    else:
        return os.path.join(base_dir, path)

if __name__ == "__main__":
    ### Markdown splitter ###
    # By default, use the custom Markdown splitter
    # (instead of splitting Markdown by CHUNK_SIZE limit.)
    # Options: process_sections, token_splitter
    USE_CUSTOM_MARKDOWN_SPLITTER = "token_splitter"
    #### Chunk size ####
    # By default, split Markdown files into 3000 chracters per chunk.
    CHUNK_SIZE = 3000
    #### Input variables for the script ####
    #
    # Note: The hardcoded values below are overwritten
    #       if the config.yaml file is found.
    #
    # MY_INPUT_PATH: An array of directories that contain source Markdown files.
    # URL_PREFIX: An array of prefixes to be used to create URLs for source Markdown files.
    # MY_OUTPUT_PATH: The target directory where processed plain text files will be stored.
    MY_INPUT_PATH = ["data/raw/markdown-src-01", "data/raw/markdown-src-02"]
    URL_PREFIX = [
        "https://my-example.com/markdown-src-01",
        "https://my-example.com/markdown-src-02",
    ]
    MY_OUTPUT_PATH = "data/plain_docs"
    # Initialize PaLM object with model to use
    palm = palmModule.PaLM(text_model="models/text-bison-001", find_models=False)
    #### Read the config.yaml file ####
    # At a minimum, INPUT_YAML must configure the following values:
    # output_path: The target directory where processed plain text files will be stored.
    # input:
    #  - path: A directory that contains source Markdown files.
    #    url_prefix: A prefix to be used to create URLs for the source Markdown files.
    IS_CONFIG_FILE = True
    if IS_CONFIG_FILE:
        config = read_config.ReadConfig()
        MY_OUTPUT_PATH = config.returnConfigValue("output_path")
        input_len = config.returnInputCount()
        condition_text = config.returnConfigValue("condition_text")
    # Need to estimate approximate max token count using prompts from config file
    # This helps in optimizing the max token count of chunks of text. Add extra
    # tokens for the line spaces that are added to prompt.
    # max_token_count_prompt = tokenCount.estimateTokensAverage(condition_text) + 5
    # max_token_count_api = palm.tokenCount(condition_text) + 5
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resolved_output_path = resolve_path(MY_OUTPUT_PATH, BASE_DIR)
    # Remove the existing output, to make sure stale files are removed
    if (os.path.exists(resolved_output_path)):
        shutil.rmtree(resolved_output_path)
    os.makedirs(resolved_output_path, exist_ok=True)
    print("Set the output directory: " + resolved_output_path)
    print("Processing files from " + str(input_len) + " sources.")
    print("Started the files_to_plain_text.py script.")
    main()