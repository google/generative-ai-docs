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

import shutil
import os
import re
import json
import typing
import uuid
from absl import logging

import tqdm
from docs_agent.utilities import config
from docs_agent.utilities.config import ProductConfig, ConfigFile, Input
from docs_agent.models.tokenCount import returnHighestTokens
from docs_agent.utilities.helpers import (
    resolve_path,
    add_scheme_url,
    end_path_backslash,
    start_path_no_backslash,
)
from docs_agent.preprocess.splitters import (
    markdown_splitter,
    html_splitter,
    fidl_splitter,
)


# Construct a URL from a URL prefix and a relative path.
def construct_a_url(url_prefix: str, relative_path: str):
    temp_url = end_path_backslash(add_scheme_url(url=url_prefix, scheme="https"))
    built_url = temp_url + start_path_no_backslash(relative_path)
    strip_ext_url = re.search(r"(.*)\.md$", built_url)
    built_url = strip_ext_url[1]
    return built_url


# This function pre-processes files before they are actually chunked.
# This allows it to resolve includes of includes, Jinja templates, etc...
# TODO support Jinja, for this need to support data filters as well
# {% set doc | jsonloads %} and {% set teams | yamlloads %}
# Returns the temp_output which can then be deleted
def pre_process_doc_files(
    product_config: ProductConfig, inputpathitem: Input, temp_path: str
) -> str:
    temp_output = os.path.join(temp_path, product_config.output_path)
    # Delete directory if it exits, then create it.
    print(f"Temp output: {temp_output}")
    print("===========================================")
    if os.path.exists(temp_output):
        shutil.rmtree(temp_output)
        os.makedirs(temp_output)
    else:
        os.makedirs(temp_output)
    # Prepare progress bar
    file_count = sum(
        len(files) for _, _, files in os.walk(resolve_path(inputpathitem.path))
    )
    progress_bar = tqdm.tqdm(
        total=file_count,
        position=0,
        bar_format="{percentage:3.0f}% | {n_fmt}/{total_fmt} | {elapsed}/{remaining}| {desc}",
    )
    for root, dirs, files in os.walk(resolve_path(inputpathitem.path)):
        if inputpathitem.exclude_path is not None:
            dirs[:] = [d for d in dirs if d not in inputpathitem.exclude_path]
        for file in files:
            # Displays status bar
            progress_bar.set_description_str(
                f"Pre-processing file {file}", refresh=True
            )
            progress_bar.update(1)
            # Process only Markdown files that do not begin with _(those should
            # be imported)
            # Construct a new sub-directory for storing output plain text files
            dir_path = os.path.join(
                temp_output, os.path.relpath(root, inputpathitem.path)
            )
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            relative_path = make_relative_path(
                file=file, root=root, inputpath=inputpathitem.path
            )
            final_filename = temp_output + "/" + relative_path
            if file.startswith("_") and file.endswith(".md"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                    # Read the input Markdown content
                    content = auto.read()
                    auto.close()
                # Process includes lines in Markdown
                file_with_include = markdown_splitter.process_markdown_includes(
                    content, root
                )
                # Process include lines in HTML
                file_with_include = html_splitter.process_html_includes(
                    file_with_include, inputpathitem.include_path_html
                )
                with open(final_filename, "w", encoding="utf-8") as new_file:
                    new_file.write(content)
                    new_file.close()
            elif file.startswith("_") and (
                file.endswith(".html") or file.endswith(".htm")
            ):
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                    # Read the input HTML content
                    content = auto.read()
                    auto.close()
                with open(final_filename, "w", encoding="utf-8") as new_file:
                    new_file.write(content)
                    new_file.close()
            else:
                # Just copy files that that we don't need to preprocess
                # Such as images or files without underscores
                initial_file = os.path.join(root, file)
                # Errors with .gsheet, skip gsheet for now
                if not (file.endswith(".gsheet")):
                    shutil.copyfile(initial_file, final_filename)
    # Return the temporary directory, which can then be deleted once files are fully processed
    return temp_output


# This function processes a Markdown file and
# splits it into smaller text chunks.
def process_markdown_file(
    filename: str,
    root: str,
    inputpathitem: Input,
    splitter: str,
    new_path: str,
    file: str,
    namespace_uuid: uuid.UUID,
    relative_path: str,
    url_prefix: str,
):
    file_metadata = {}
    # Read the input Markdown content
    to_file = ""
    with open(filename, "r", encoding="utf-8") as auto:
        to_file = auto.read()
        auto.close()
    # Process includes lines in Markdown
    file_with_include = markdown_splitter.process_markdown_includes(to_file, root)
    # Process include lines in HTML
    file_with_include = html_splitter.process_html_includes(
        file_with_include, inputpathitem.include_path_html
    )
    # Estimate of the token count
    page_token_estimate = returnHighestTokens(file_with_include)
    # Get the original input path
    original_input = inputpathitem.path
    if splitter == "token_splitter":
        # Returns an array of Section objects along with a Page
        # Object that contains metadata
        (
            page_sections,
            page,
        ) = markdown_splitter.process_markdown_page(
            markdown_text=file_with_include, header_id_spaces="-"
        )
        # Process this page's sections into plain text chunks.
        chunk_number = 0
        for section in page_sections:
            filename_to_save = make_chunk_name(
                new_path=new_path,
                file=file,
                index=chunk_number,
                extension="md",
            )
            # Get the text chunk filename string (after `docs-agent/data`).
            text_chunk_filename = get_relative_path_and_filename(filename_to_save)
            # Generate UUID for each plain text chunk and collect its metadata,
            # which will be written to the top-level `file_index.json` file.
            md_hash = uuid.uuid3(namespace_uuid, section.content)
            uuid_file = uuid.uuid3(namespace_uuid, filename_to_save)
            origin_uuid = uuid.uuid3(namespace_uuid, relative_path)
            # If no URL came from frontmatter, assign URL from config
            if page.URL == "":
                page.URL = end_path_backslash(
                    add_scheme_url(url=url_prefix, scheme="https")
                )
            # Strip extension of .md from url
            # Makes sure that relative_path starts without backslash
            # page.url will have backslash
            built_url = page.URL + start_path_no_backslash(relative_path)
            strip_ext_url = re.search(r"(.*)\.md$", built_url)
            built_url = strip_ext_url[1]
            # Build the valid URL for a section including header
            # Do not add a # if section 1
            if section.name_id != "" and int(section.level) != 1:
                built_url = built_url + "#" + section.name_id
            # Adds additional info so that the section can know its origin
            file_metadata[filename_to_save] = {
                "UUID": str(uuid_file),
                "origin_uuid": str(origin_uuid),
                "source": str(original_input),
                "source_file": str(relative_path),
                "page_title": str(section.page_title),
                "section_title": str(section.section_title),
                "section_name_id": str(section.name_id),
                "section_id": int(section.id),
                "section_level": int(section.level),
                "previous_id": int(section.previous_id),
                "URL": str(built_url),
                "md_hash": str(md_hash),
                "text_chunk_filename": str(text_chunk_filename),
                "token_estimate": float(section.token_count),
                "full_token_estimate": float(page_token_estimate),
                "parent_tree": list(section.parent_tree),
                "metadata": dict(page.metadata),
            }
            with open(filename_to_save, "w", encoding="utf-8") as new_file:
                new_file.write(section.content)
                new_file.close()
            chunk_number += 1
    elif splitter == "process_sections":
        # Use a custom Markdown splitter to split a Markdown file
        # into small text chunks
        to_file = markdown_splitter.process_markdown_includes(to_file, root)
        # Add the page title and section title into each text chunk
        (
            to_file,
            metadata,
        ) = markdown_splitter.process_page_and_section_titles(to_file)
        # Process this page's sections into plain text chunks.
        docs = markdown_splitter.process_document_into_sections(to_file)
        # Process each text chunk.
        chunk_number = 0
        for doc in docs:
            filename_to_save = make_chunk_name(
                new_path=new_path,
                file=file,
                index=chunk_number,
                extension="md",
            )
            # Get the text chunk filename string (after `docs-agent/data`).
            text_chunk_filename = get_relative_path_and_filename(filename_to_save)
            # Generate UUID for each plain text chunk and collect its metadata,
            # which will be written to the top-level `file_index.json` file.
            md_hash = uuid.uuid3(namespace_uuid, file_with_include)
            uuid_file = uuid.uuid3(namespace_uuid, filename_to_save)
            # Clean up Markdown and HTML syntax
            content = markdown_splitter.markdown_to_text(doc)
            # Contruct a URL
            built_url = construct_a_url(url_prefix, relative_path)
            # Get the page title
            page_title = "None"
            if "title" in metadata:
                page_title = metadata["title"]
            # Construct metadata.
            file_metadata[filename_to_save] = {
                "UUID": str(uuid_file),
                "origin_uuid": str(uuid_file),
                "source": str(original_input),
                "source_file": str(relative_path),
                "page_title": str(page_title),
                "section_title": str("None"),
                "section_name_id": str("None"),
                "section_id": int(1),
                "section_level": int(1),
                "previous_id": int(1),
                "URL": str(built_url),
                "md_hash": str(md_hash),
                "text_chunk_filename": str(text_chunk_filename),
                "token_estimate": float(1.0),
                "full_token_estimate": float(page_token_estimate),
                "metadata": dict(metadata),
            }
            with open(filename_to_save, "w", encoding="utf-8") as new_file:
                new_file.write(content)
                new_file.close()
            chunk_number += 1
    else:
        # Exits if no valid markdown splitter
        logging.error(
            f"Select a valid markdown_splitter option in your configuration for your product\n"
        )
        exit()
    return file_metadata


# This function processes a FIDL file (.fidl) into small text chunks.
def process_fidl_file(
    filename: str,
    root: str,
    inputpathitem: Input,
    splitter: str,
    new_path: str,
    file: str,
    namespace_uuid: uuid.UUID,
    relative_path: str,
    url_prefix: str,
):
    # Local variables
    file_metadata = {}
    library_name = ""
    filename_prefix = "index"
    chunk_number = 0
    # Get the original input path
    original_input = inputpathitem.path
    # Read the input FIDL content
    to_file = ""
    with open(filename, "r", encoding="utf-8") as auto:
        to_file = auto.read()
        auto.close()
    # Split the FIDL file into a list of FIDL protocols.
    fidl_protocols = fidl_splitter.split_file_to_protocols(to_file)
    # Iterate the list of FIDL protocols.
    for fidl_protocol in fidl_protocols:
        # Identify the new FIDL chunk file path and name.
        filename_to_save = make_file_chunk_name(
            new_path=new_path, filename_prefix=filename_prefix, index=chunk_number
        )
        # Get the text chunk filename string (after `docs-agent/data`).
        text_chunk_filename = get_relative_path_and_filename(filename_to_save)
        # Prepare metadata for this FIDL protocol chunk.
        md_hash = uuid.uuid3(namespace_uuid, fidl_protocol)
        uuid_file = uuid.uuid3(namespace_uuid, filename_to_save)
        origin_uuid = uuid.uuid3(namespace_uuid, relative_path)
        # Contruct the URL for this FIDL protocol.
        match_library = re.search(r"^Library\sname:\s+(.*)\n", fidl_protocol)
        if match_library:
            library_name = match_library.group(1)
        # If no library name is found,
        # the library name from the previous protocol is used.
        fidl_url = url_prefix + library_name
        file_metadata[filename_to_save] = {
            "UUID": str(uuid_file),
            "origin_uuid": str(origin_uuid),
            "source": str(original_input),
            "source_file": str(relative_path),
            "source_id": int(chunk_number),
            "page_title": str(library_name),
            "section_title": str(library_name),
            "section_name_id": str("None"),
            "section_id": int(1),
            "section_level": int(1),
            "previous_id": int(1),
            "URL": str(fidl_url),
            "md_hash": str(md_hash),
            "text_chunk_filename": str(text_chunk_filename),
            "token_estimate": float(1.0),
            "full_token_estimate": float(1.0),
        }
        # Save the FIDL protocol content as a text chunk.
        with open(filename_to_save, "w", encoding="utf-8") as new_file:
            new_file.write(fidl_protocol)
            new_file.close()
        chunk_number += 1
    return file_metadata


# This function processes a HTML file into small text chunks.
def process_html_file(
    filename: str,
    root: str,
    inputpathitem: Input,
    splitter: str,
    new_path: str,
    file: str,
    namespace_uuid: uuid.UUID,
    relative_path: str,
    url_prefix: str,
):
    # Local variables
    file_metadata = {}
    # Read the input HTML content
    to_file = ""
    with open(filename, "r", encoding="utf-8") as auto:
        to_file = auto.read()
        auto.close()
    # Process includes lines in HTML
    file_with_include = html_splitter.process_html_includes(
        to_file, inputpathitem.include_path_html
    )
    return file_metadata


# This function processes files specified in the `inputs` field
# in the config.yaml file into small plain text files.
# Includes are processed again since preprocess resolves the includes in
# files prefixed with _, which indicates they are not standalone.
# inputpath is optional to walk a temporary directory that has been pre-processed.
# If not, it defaults to path of inputpathitem.
def process_files_from_input(
    product_config: ProductConfig,
    inputpathitem: Input,
    splitter: str,
    inputpath: typing.Optional[str] = None,
    input_path_count: int = 0,
):
    # If inputpath isn't specified assign path from item
    if inputpath is None:
        inputpath = inputpathitem.path
    file_count = 0
    md_count = 0
    html_count = 0
    fidl_count = 0
    file_index = []
    full_file_metadata = {}
    resolved_output_path = resolve_path(product_config.output_path)
    chunk_group_name = "text_chunks_" + "{:03d}".format(input_path_count)
    # Get the total file count.
    file_count = sum(len(files) for _, _, files in os.walk(resolve_path(inputpath)))
    # Set up a status bar for the terminal display.
    progress_bar = tqdm.tqdm(
        total=file_count,
        position=0,
        bar_format="{percentage:3.0f}% | {n_fmt}/{total_fmt} | {elapsed}/{remaining}| {desc}",
    )
    # Process each input path provided in config.yaml.
    for root, dirs, files in os.walk(resolve_path(inputpath)):
        if inputpathitem.exclude_path is not None:
            dirs[:] = [d for d in dirs if d not in inputpathitem.exclude_path]
        if inputpathitem.url_prefix is not None:
            # Makes sure that URL ends in backslash
            url_prefix = end_path_backslash(inputpathitem.url_prefix)
            namespace_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, url_prefix)
        # Process the files found in this input path provided in config.yaml.
        for file in files:
            # Displays status bar
            progress_bar.set_description_str(f"Processing file {file}", refresh=True)
            progress_bar.update(1)
            # Skip this file if it starts with `_`.
            if file.startswith("_"):
                continue
            # Get the full path to this input file.
            filename_to_open = os.path.join(root, file)
            # Construct a new sub-directory for storing output plain text files.
            new_path = (
                resolved_output_path
                + "/"
                + chunk_group_name
                + re.sub(resolve_path(inputpath), "", os.path.join(root, ""))
            )
            is_exist = os.path.exists(new_path)
            if not is_exist:
                os.makedirs(new_path)
            # Get the relative path to this input file.
            relative_path = make_relative_path(
                file=file, root=root, inputpath=inputpath
            )
            # Select Splitter mode: Markdown, FIDL, or HTML.
            if splitter == "token_splitter" or splitter == "process_sections":
                if file.endswith(".md"):
                    # Add filename to a list
                    file_index.append(relative_path)
                    # Increment the Markdown file count.
                    md_count += 1
                    # Process a Markdown file.
                    this_file_metadata = process_markdown_file(
                        filename_to_open,
                        root,
                        inputpathitem,
                        splitter,
                        new_path,
                        file,
                        namespace_uuid,
                        relative_path,
                        url_prefix,
                    )
                    # Merge this file's metadata to the global metadata.
                    full_file_metadata.update(this_file_metadata)
            elif splitter == "fidl_splitter":
                if file.endswith(".fidl"):
                    # Add filename to a list
                    file_index.append(relative_path)
                    # Increment the FIDL file count.
                    fidl_count += 1
                    # Process a FIDL protocol file.
                    this_file_metadata = process_fidl_file(
                        filename_to_open,
                        root,
                        inputpathitem,
                        splitter,
                        new_path,
                        file,
                        namespace_uuid,
                        relative_path,
                        url_prefix,
                    )
                    # Merge this file's metadata to the global metadata.
                    full_file_metadata.update(this_file_metadata)
            else:
                if file.endswith(".htm") or file.endswith(".html"):
                    # Add filename to a list
                    file_index.append(relative_path)
                    # Increment the HTML file count.
                    html_count += 1
                    # Process a HTML file.
                    this_file_metadata = process_html_file(
                        filename_to_open,
                        root,
                        inputpathitem,
                        splitter,
                        new_path,
                        file,
                        namespace_uuid,
                        relative_path,
                        url_prefix,
                    )
                    # Merge this file's metadata to the global metadata.
                    full_file_metadata.update(this_file_metadata)

    # The processing of input files is finished.
    progress_bar.set_description_str(f"Finished processing files.", refresh=False)
    # Count all processed files.
    file_count = md_count + html_count + fidl_count
    # Print the summary of the processed files.
    print()
    print("Processed " + str(file_count) + " files from the source: " + str(inputpath))
    print(str(md_count) + " Markdown files.")
    print(str(html_count) + " HTML files.")
    if fidl_count > 0:
        print(str(fidl_count) + " FIDL files.")
    print()
    return file_count, md_count, html_count, file_index, full_file_metadata


# Write the recorded input variables into a file: `file_index.json`
def save_file_index_json(output_path, output_content):
    json_out_file = resolve_path(output_path) + "/file_index.json"
    with open(json_out_file, "w", encoding="utf-8") as outfile:
        json.dump(output_content, outfile)
    # print("Created " + json_out_file + " to store the complete list of processed files.")


# Given a file, root, and inputpath, make a relative path
def make_relative_path(
    file: str, inputpath: str, root: typing.Optional[str] = None
) -> str:
    file_slash = "/" + file
    if root is None:
        relative_path = os.path.relpath(file_slash, inputpath)
    else:
        relative_path = os.path.relpath(root + file_slash, inputpath)
    return relative_path


# Given a path, filename_prefix, chunk index, and an optional path extension (to save chunk)
# Create a file chunk name
def make_file_chunk_name(
    new_path: str, filename_prefix: str, index: int, extension: str = "md"
) -> str:
    filename_to_save = filename_prefix + "_" + str(index) + "." + extension
    full_filename = os.path.join(new_path, filename_to_save)
    return full_filename


# Given a path, file, chunk index, and an optional path extension (to save chunk)
# Create a chunk name
def make_chunk_name(new_path: str, file: str, index: int, extension: str = "md") -> str:
    new_filename = os.path.join(new_path, file)
    filename_to_save = new_filename
    # Grab the filename without the .md extension
    match = re.search(r"(.*)\.md$", new_filename)
    if match:
        new_filename_no_ext = match[1]
        # Save the filename appended with an index.
        filename_to_save = new_filename_no_ext + "_" + str(index) + "." + extension
    return filename_to_save


# Return the relative path after the `docs-agent/data` path
def get_relative_path_and_filename(full_path: str):
    path_and_filename = full_path
    match = re.search(r".*\/docs-agent\/data\/(.*)$", full_path)
    if match:
        path_and_filename = match[1]
    return path_and_filename


# Given a path, it resolves the path to an absolute path, and if it exists,
# deletes it, before re-creating it (essentially making a fresh directory)
# It then returns the absolute path name
def resolve_and_clear_path(path: str) -> str:
    resolved_output_path = resolve_path(path)
    # Remove the existing output, to make sure stale files are removed
    if os.path.exists(resolved_output_path):
        shutil.rmtree(resolved_output_path)
    os.makedirs(resolved_output_path, exist_ok=True)
    return resolved_output_path


# Processes all inputs from a given ProductConfig object
def process_inputs_from_product(input_product: ProductConfig, temp_process_path: str):
    source_file_index = {}
    total_file_count = 0
    total_md_count = 0
    total_html_count = 0
    final_file_metadata = {}
    input_path_count = 0
    for input_path_item in input_product.inputs:
        print(f"\nInput path {input_path_count}: {input_path_item.path}")
        temp_output = pre_process_doc_files(
            product_config=input_product,
            inputpathitem=input_path_item,
            temp_path=temp_process_path,
        )
        # Process Markdown files in the `input` path, when using pre_proces_doc_files
        # temp_output should be used as inputpath parameter
        (
            file_count,
            md_count,
            html_count,
            file_index,
            full_file_metadata,
        ) = process_files_from_input(
            product_config=input_product,
            inputpathitem=input_path_item,
            inputpath=temp_output,
            splitter=input_product.markdown_splitter,
            input_path_count=input_path_count,
        )
        # Clear the temp_output
        shutil.rmtree(temp_output)
        input_path = input_path_item.path
        if not input_path.endswith("/"):
            input_path = input_path + "/"
        input_path = resolve_path(input_path)
        # Record the input variables used in this path.
        file_list = {}
        for file in file_index:
            file_obj = {file: {"source": input_path, "URL": input_path_item.url_prefix}}
            file_list[file] = file_obj
        # Make a single dictionary per product, append each input
        final_file_metadata = final_file_metadata | full_file_metadata
        # source_file_index[input_product.product_name] = full_file_metadata
        total_file_count += file_count
        total_md_count += md_count
        total_html_count += html_count
        input_path_count += 1
    source_file_index[input_product.product_name] = final_file_metadata
    # Write the recorded input variables into `file_index.json`.
    save_file_index_json(
        output_path=input_product.output_path, output_content=source_file_index
    )
    print(
        "\n[Summary]"
        + f"\nProduct: {input_product.product_name}"
        + "\nSources: "
        + str(len(input_product.inputs))
        + "\nTotal number of processed source files: "
        + str(total_file_count)
        + "\nMarkdown files: "
        + str(total_md_count)
        + "\nHTML files: "
        + str(total_html_count)
    )


# Print the size distribution map of created text chunks.
def get_chunk_size_distribution_from_product(input_product: ProductConfig):
    chunk_size_map = {
        "50": 0,
        "500": 0,
        "1000": 0,
        "1500": 0,
        "2000": 0,
        "2500": 0,
        "3000": 0,
        "4000": 0,
        "5000": 0,
        "6000": 0,
    }
    total_file_count = 0
    chunk_dir = input_product.output_path
    for root, dirs, files in os.walk(resolve_path(chunk_dir)):
        for file in files:
            this_filename = os.path.join(root, file)
            if this_filename.endswith(".md"):
                file_stats = os.stat(this_filename)
                chunk_size = int(file_stats.st_size)
                if chunk_size <= 50:
                    count = chunk_size_map["50"]
                    chunk_size_map["50"] = count + 1
                elif chunk_size > 50 and chunk_size <= 500:
                    count = chunk_size_map["500"]
                    chunk_size_map["500"] = count + 1
                elif chunk_size > 500 and chunk_size <= 1000:
                    count = chunk_size_map["1000"]
                    chunk_size_map["1000"] = count + 1
                elif chunk_size > 1000 and chunk_size <= 1500:
                    count = chunk_size_map["1500"]
                    chunk_size_map["1500"] = count + 1
                elif chunk_size > 1500 and chunk_size <= 2000:
                    count = chunk_size_map["2000"]
                    chunk_size_map["2000"] = count + 1
                elif chunk_size > 2000 and chunk_size <= 2500:
                    count = chunk_size_map["2500"]
                    chunk_size_map["2500"] = count + 1
                elif chunk_size > 2000 and chunk_size <= 3000:
                    count = chunk_size_map["3000"]
                    chunk_size_map["3000"] = count + 1
                elif chunk_size > 3000 and chunk_size <= 4000:
                    count = chunk_size_map["4000"]
                    chunk_size_map["4000"] = count + 1
                elif chunk_size > 4000 and chunk_size <= 5000:
                    count = chunk_size_map["5000"]
                    chunk_size_map["5000"] = count + 1
                else:
                    count = chunk_size_map["6000"]
                    chunk_size_map["6000"] = count + 1
                total_file_count += 1

    # Print the distribution result.
    print("\nSpread of text chunk sizes and counts:")
    prev_size = 0
    for key in list(chunk_size_map):
        count = chunk_size_map[key]
        if int(key) == 50:
            print(f"- Chunks smaller than {key} bytes: {count}")
        elif int(key) == 6000:
            print(f"- Chunks larger than {key} bytes: {count}")
        else:
            print(f"- Chunks between {prev_size} and {key} bytes: {count}")
        prev_size = int(key)
    print(f"\nTotal number of chunks: {total_file_count}")


# Given a ReadConfig object, process all products
# Default Read config defaults to source of project with config.yaml
# temp_process_path is where temporary files will be processed and then deleted
# defaults to /tmp
def process_all_products(
    config_file: ConfigFile = config.ReadConfig().returnProducts(),
    temp_process_path: str = "/tmp",
):
    print(f"Starting chunker for {str(len(config_file.products))} products.\n")
    for index, product in enumerate(config_file.products):
        print(f"===========================================")
        print(f"Processing product: {product.product_name}")
        # logging.error(f"Index: {index}")
        # if index != 0:
        #     old_entries = read_file_index_json(output_path=input_product.output_path)
        #     logging.error(old_entries)
        # else:
        #     old_entries = None
        print("Output directory: " + resolve_and_clear_path(product.output_path))
        print("Processing files from " + str(len(product.inputs)) + " sources.")
        process_inputs_from_product(
            input_product=product, temp_process_path=temp_process_path
        )

        # Print the distribution map of text chunk sizes.
        get_chunk_size_distribution_from_product(input_product=product)


def main():
    #### Main ####
    process_all_products()


if __name__ == "__main__":
    main()
