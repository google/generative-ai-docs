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
from bs4 import BeautifulSoup
import os
import re
import json
import frontmatter
import read_config
import uuid

### Makrdown splitter ###
# By default, use the custom Markdown splitter
# (instead of splitting Markdown by CHUNK_SIZE limit.)
USE_CUSTOM_MARKDOWN_SPLITTER = True

#### Chunk size ####
# By default, split Markdown files into 3000 chracters per chunk.
CHUNK_SIZE = 3000

#### Input variables for the script ####
#
# Note: The hardcoded values below are overwritten
#       if the `input-values.yaml` file is found.
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

#### Read the `input-values-yaml` file ####
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

print("Started the markdown-to-plain-text.py script.")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_path(rel_or_abs_path: str, base_dir=BASE_DIR):
    path = rel_or_abs_path.strip()
    if path.startswith("/"):
        return path
    else:
        return os.path.join(base_dir, path)


MY_OUTPUT_PATH = resolve_path(MY_OUTPUT_PATH)
os.makedirs(MY_OUTPUT_PATH, exist_ok=True)

print("Set the output directory: " + MY_OUTPUT_PATH)
print("Processing files from " + str(input_len) + " sources.")


# This function converts a Markdown string to plain text.
def markdown_to_text(markdown_string):
    # Remove <!-- --> lines in Markdown
    markdown_string = re.sub(r"<\!--(.*?)-->", "", markdown_string)

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # Extract text
    soup = BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(string=True))

    # Remove [][] in Markdown
    text = re.sub(r"\[(.*?)\]\[(.*?)\]", "\\1", text)

    # Remove {: } in devsite Markdown
    text = re.sub(r"\{:(.*?)\}", "", text)

    # Remove {. } in g3doc Markdown
    text = re.sub(r"\{.(.*?)\}", "", text)

    # Remove a single line `sh` in g3doc Markdown
    text = re.sub(r"(?m)^sh$", "", text)

    # Remove a single line ````sh` in g3doc Markdown
    # text = re.sub(r'(?m)^```sh$', '', text)

    # Remove code snippets
    text = re.sub(r"<pre>(.*?)</pre>", "\\1", text)
    text = re.sub(r"<code>(.*?)</code>", "\\1", text)
    text = re.sub(r"(?m)<var>(.*?)</var>", "\\1", text)
    text = re.sub(
        r"(^|)(Important|Note|Caution|Tip|Warning|Important|Key Point|Key Term):\s?",
        "",
        text,
    )
    text = re.sub(
        r"(^|)(Objective|Success|Beta|Preview|Deprecated):\s?",
        "",
        text,
    )
    text = re.sub(r"(Project|Book):(.*)\n", "", text)
    text = text.strip() + "\n"
    return text


# Function to verify that include exists and exports its content
def read_markdown(file):
    try:
        with open(file, "r", encoding="utf-8") as mdfile:
            output = mdfile.read()
            return output
    except FileNotFoundError:
        print("[FileNotFound] Missing the include file: " + file)


# This function converts Markdown page (#), section (##), and subsection (###)
# headings into plain English.
def process_page_and_section_titles(markdown_text):
    updated_markdown = ""
    page_title = ""
    section_title = ""
    subsection_title = ""
    new_line = ""
    metadata = {}
    # Processes the frontmatter in a markdown file
    data = frontmatter.loads(markdown_text)
    if "title" in data:
        page_title = data["title"]
        markdown_text = data.content
        metadata = data.metadata
    if "URL" in data:
        final_url = data["URL"]
        metadata["URL"] = final_url
    for line in markdown_text.split("\n"):
        new_line = ""
        skip_this_line = False
        if line.startswith("#"):
            match = re.search(r"^(\#*)\s+(.*)$", line)
            heading = ""
            captured_title = ""
            if match:
                heading = match[1]
                # Remove {: } in devsite Markdown
                captured_title = re.sub(r"\{:(.*?)\}", "", match[2])
                # Special case of RFC pages.
                if re.search(r"^\{\{\s+(.*)\.(.*)\s+\}\}$", captured_title):
                    heading = ""
                    page_title = "RFC"
                    skip_this_line = True

            # Detect Markdown heading levels
            if heading == "#":
                page_title = captured_title.strip()
                metadata["title"] = page_title
                subsection_title = ""
                section_title = ""
            elif heading == "##":
                section_title = captured_title.strip()
                subsection_title = ""
            elif heading == "###":
                subsection_title = captured_title.strip()

            # Convert Markdown headings into plain English
            # (but keep `#` for the `process_document_into_sections()`
            # function to detect these headings for splitting).
            if page_title:
                new_line = (
                    '# The "'
                    + page_title
                    + '" page contains the following content:\n\n'
                )

            if section_title:
                new_line = (
                    '# The "'
                    + page_title
                    + '" page has the "'
                    + section_title
                    + '" section that contains the following content:\n'
                )

            if subsection_title:
                new_line = (
                    '# On the "'
                    + page_title
                    + '" page, the "'
                    + section_title
                    + '" section has the "'
                    + subsection_title
                    + '" subsection that contains the following content:\n'
                )

        if skip_this_line is False:
            if new_line:
                updated_markdown += new_line + "\n"
            else:
                updated_markdown += line + "\n"
    return updated_markdown, metadata


# This function replaces Markdown's includes sections with content.
def process_includes(markdown_text, root):
    updated_markdown = ""
    for line in markdown_text.split("\n"):
        new_line = ""
        # Replaces Markdown includes with content
        if line.startswith("<<"):
            include_match = re.search("^<<(.*?)>>", line)
            if include_match:
                include_file = os.path.abspath(root + "/" + include_match[1])
                new_line = read_markdown(include_file)
        if new_line:
            updated_markdown += new_line + "\n"
        else:
            updated_markdown += line + "\n"
    return updated_markdown


# This function divides Markdown content into sections and
# returns an array containing these sections.
# But this function requires pre-processed Markdown headings from
# the `process_page_and_section_titles()` function, which simplifies
# three levels of Markdown headings (#, ##, and ###) into just a single #.
def process_document_into_sections(markdown_text):
    sections = []
    buffer = ""
    first_section = True
    for line in markdown_text.split("\n"):
        if line.startswith("#"):
            match = re.search(r"^(\#*)\s+(.*)$", line)
            heading = ""
            if match:
                heading = match[1]
            if heading == "#":
                if first_section is True:
                    # Ignore the first detection of `#`.
                    first_section = False
                else:
                    # When a new `#` is detected, store the text in `buffer` into
                    # an array entry and clear the buffer for the next section.
                    sections.append(buffer)
                    buffer = ""
        buffer += line + "\n"
    # Add the last section on the page.
    sections.append(buffer)
    return sections


# This function processes Markdown files in the `input_path` directory
# into plain text files.
def process_markdown_files_from_source(configs, inputpath, counter, excludepath):
    f_count = 0
    for root, dirs, files in os.walk(resolve_path(inputpath)):
        if IS_CONFIG_FILE:
            if "exclude_path" in configs[counter]:
                dirs[:] = [d for d in dirs if d not in excludepath]
            if "url_prefix" in configs[counter]:
                namespace_uuid = uuid.uuid3(
                    uuid.NAMESPACE_DNS, configs[counter]["url_prefix"]
                )
        for file in files:
            f_count += 1
            # Process only Markdown files
            if file.endswith(".md"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as auto:
                    # Construct a new sub-directory for storing output plain text files
                    new_path = MY_OUTPUT_PATH + re.sub(
                        resolve_path(inputpath), "", os.path.join(root, "")
                    )
                    is_exist = os.path.exists(new_path)
                    if not is_exist:
                        os.makedirs(new_path)
                    # Grab the filename without the .md extension
                    new_filename = os.path.join(new_path, file)
                    # Add filename to a list
                    file_slash = "/" + file
                    relative_path = os.path.relpath(root + file_slash, inputpath)
                    file_index.append(relative_path)
                    match = re.search(r"(.*)\.md$", new_filename)
                    new_filename_no_ext = match[1]
                    # Read the input Markdown content
                    to_file = auto.read()
                    # Reformat the page and section titles
                    to_file, metadata = process_page_and_section_titles(to_file)
                    # Process includes lines in Markdown
                    to_file = process_includes(to_file, root)
                    doc = []
                    if USE_CUSTOM_MARKDOWN_SPLITTER is True:
                        # Use a custom splitter to split into small chunks
                        docs = process_document_into_sections(to_file)
                    else:
                        # Use the Markdown splitter to split into small chunks
                        docs = markdown_splitter.create_documents([to_file])
                    i = 0
                    for doc in docs:
                        # Clean up Makrdown and HTML syntax
                        if USE_CUSTOM_MARKDOWN_SPLITTER is True:
                            content = markdown_to_text(doc)
                        else:
                            content = markdown_to_text(doc.page_content)
                        # Save clean plain text to a new filename appended with an index
                        filename_to_save = new_filename_no_ext + "_" + str(i) + ".md"
                        # Generate UUID for each plain text chunk and collect its metadata,
                        # which will be written to the top-level `file_index.json` file.
                        md_hash = uuid.uuid3(namespace_uuid, content)
                        uuid_file = uuid.uuid3(namespace_uuid, filename_to_save)
                        if bool(metadata):
                            full_file_metadata[filename_to_save] = {
                                "UUID": str(uuid_file),
                                "source": input_path,
                                "source_file": relative_path,
                                "source_id": counter,
                                "URL": url_pre,
                                "md_hash": str(md_hash),
                                "metadata": metadata,
                            }
                        else:
                            full_file_metadata[filename_to_save] = {
                                "UUID": str(uuid_file),
                                "source": input_path,
                                "source_file": relative_path,
                                "source_id": counter,
                                "URL": url_pre,
                                "md_hash": str(md_hash),
                            }
                        with open(filename_to_save, "w", encoding="utf-8") as new_file:
                            new_file.write(content)
                            new_file.close()
                        i = i + 1
                    auto.close()
    print("Processed " + str(f_count) + " Markdown files from the source: " + inputpath)
    return f_count


# Write the recorded input variables into a file: `file_index.json`
def save_file_index_json(src_file_index):
    json_out_file = MY_OUTPUT_PATH + "/file_index.json"
    with open(json_out_file, "w", encoding="utf-8") as outfile:
        json.dump(src_file_index, outfile)
    print(
        "Created " + json_out_file + " to store the complete list of processed files."
    )


#### Main ####
source_file_index = {}
input_counter = 0
total_file_count = 0

# Main for-loop
for input_counter in range(input_len):
    full_file_metadata = {}
    file_index = []
    exclude = []
    # Process `input-values.yaml` into input variables.
    if IS_CONFIG_FILE:
        # Reads all the input values defined in the configuration file
        config_values = config.returnConfigValue("input")
        if "path" in config_values[input_counter]:
            input_path = config_values[input_counter]["path"]
        if "url_prefix" in config_values[input_counter]:
            url_pre = config_values[input_counter]["url_prefix"]
        if "exclude_path" in config_values[input_counter]:
            exclude = config_values[input_counter]["exclude_path"]
    else:
        input_path = MY_INPUT_PATH[input_counter]
        url_pre = URL_PREFIX[input_counter]

    # Process Markdown files in the `input` path
    file_count = process_markdown_files_from_source(
        config_values, input_path, input_counter, exclude
    )
    if not input_path.endswith("/"):
        input_path = input_path + "/"
    input_path = resolve_path(input_path)
    # Record the input variables used in this path.
    file_list = {}
    for file in file_index:
        file_obj = {file: {"source": input_path, "URL": url_pre}}
        file_list[file] = file_obj
    source_file_index[input_counter] = full_file_metadata
    input_counter += 1
    total_file_count += file_count

# Write the recorded input variables into `file_index.json`.
save_file_index_json(source_file_index)

print(
    "Processed a total of "
    + str(total_file_count)
    + " Markdown files from "
    + str(input_counter)
    + " sources."
)
