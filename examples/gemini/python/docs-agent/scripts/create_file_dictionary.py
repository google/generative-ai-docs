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
"""
This script extracts image paths and alt text from markdown, html, or a directory of files.

Usage:
  python create_file_dictionary.py <input_file>

Example:
  python create_file_dictionary.py my_document.md
  python create_file_dictionary.py my_document.html
  python create_file_dictionary.py my_documents_folder
"""

import os
import sys

from docs_agent.preprocess.extract_image_path import parse_md_html_files_for_images
from docs_agent.utilities.helpers import resolve_path
from docs_agent.utilities.helpers import save_file
from docs_agent.utilities.helpers import create_output_directory


def main(input_path: str = sys.argv[1]):
    """Main function to extract image paths and alt text, and update markdown files.

    Args:
        input_path: The path to the input file or directory.
    """
    # Create a file containing image paths and current alt text for input md files
    # extract_image_files(input_path)
    file_dictionary = walk_directory(input_path)
    create_output_directory("agent_out")
    print(f"Saving file dictionary to: agent_out/file_alt_text.yaml")
    save_file(output_path="agent_out/file_alt_text.yaml", content=file_dictionary)
    # Create a file containing image paths to be given to Docs Agent task
    save_image_paths(file_dictionary)


def walk_directory(input_path: str) -> dict:
    """Walks through the input path (file or directory) and generates a dictionary
    containing image paths and alt text for each markdown or html file.

    Args:
        input_path: The path to the input file or directory.

    Returns:
        A dictionary containing the files list.
    """
    if input_path.startswith("~/"):
        input_path = os.path.expanduser(input_path)
    input_path = os.path.realpath(os.path.join(os.getcwd(), input_path))
    files_list = []
    if os.path.isdir(input_path):
        for root, _, files in os.walk(resolve_path(input_path)):
            for file in files:
                file_path = os.path.realpath(os.path.join(root, file))
                file_data = generate_dictionary_md_file(file_path)
                # Prevents empty dictionaries from being added
                if file_data and "files" in file_data:
                    files_list.append(file_data["files"])
    else:
        file_data = generate_dictionary_md_file(input_path)
        if file_data and "files" in file_data:
            files_list.append(file_data["files"])

    # Return a dictionary containing the files list
    return {"files": files_list}


def generate_dictionary_md_file(input_file: str) -> dict:
    """Generates a dictionary containing alt text for each image in the input file.

    Args:
        input_file: The path to the input file.

    Returns:
        A dictionary containing the alt text for each image in the input file.
    """
    md_obj = {}
    if input_file.endswith((".md", ".html")):
        image_obj = parse_md_html_files_for_images(input_file)
        md_obj["files"] = {
            "path": resolve_path(input_file),
            "images": image_obj["images"],
        }
    return md_obj


def save_image_paths(input_dictionary: dict) -> None:
    """Returns the image paths from the input dictionary."""
    image_paths = []
    for file_data in input_dictionary["files"]:
        image_paths.extend(file_data["images"]["full_image_paths"])
    create_output_directory("agent_out")
    save_file(output_path="agent_out/image_paths.txt", content="\n".join(image_paths))


main()
