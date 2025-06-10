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
This script extracts image paths from markdown, html, or directory of files.

Usage:
  python extract_image_files.py <input_file>

Example:
  python extract_image_files.py my_document.md
  python extract_image_files.py my_document.html
  python extract_image_files.py my_documents_folder
"""
import os
import sys
from absl import logging

from docs_agent.preprocess.extract_image_path import extract_image_path_from_html
from docs_agent.preprocess.extract_image_path import extract_image_path_from_markdown
from docs_agent.utilities.helpers import resolve_path


def main(input: str = sys.argv[1]):
  """
  Extracts image paths from markdown, html, or directory of files.

  Args:
      input: The path to the input file.
  """
  dir_name = "agent_out"
  if input.startswith("~/"):
    input = os.path.expanduser(input)
  input = os.path.realpath(os.path.join(os.getcwd(), input))
  content = ""
  if os.path.isdir(input):
    for root, _, files in os.walk(resolve_path(input)):
      for file in files:
        file_path = os.path.realpath(os.path.join(root, file))
        content += parse_files(file_path)
  else:
    content += parse_files(input)
  if not os.path.exists(dir_name):
    os.makedirs(dir_name)
  save_file(dir_name + "/image_paths.txt", content)


def parse_files(input: str) -> str:
  """
  Parses the input file and extracts image paths.

  Args:
      input: The path to the input file.

  Returns:
      A string containing the image paths each on a new line.
  """
  if input.endswith(".md"):
    file_content = open_file(input)
    image_paths = extract_image_path_from_markdown(file_content)
  elif input.endswith(".html") or input.endswith(".htm"):
    file_content = open_file(input)
    image_paths = extract_image_path_from_html(file_content)
  else:
    image_paths = []
    # This can get noisy so better to log as info.
    logging.info("Skipping this file since it is not a markdown or html file: " + input)
  content = ""
  for image_path in image_paths:
    dir_path = os.path.dirname(input)
    if (image_path.startswith("http://") or image_path.startswith("https://")):
      logging.warning(f"Skipping this image path since it is a URL: {image_path}\n")
    if image_path.startswith("./"):
      image_path = image_path.removeprefix("./")
      image_path = os.path.join(dir_path, image_path)
      content += image_path + "\n"
    elif image_path[0].isalpha():
      image_path = os.path.join(dir_path, image_path)
      content += image_path + "\n"
    elif image_path.startswith("/") and "/devsite/" in input:
      # If the document is part of devsite, the path needs to be trimmed to the
      # subdirectory (returns devsite tenant path) and then joined with the
      # image path
      devsite_path = trim_path_to_subdir(input, "en/")
      image_path = image_path.removeprefix("/")
      image_path = os.path.join(devsite_path, image_path)
      content += image_path + "\n"
    else:
      logging.error(f"Skipping this image path because it cannot be parsed: {image_path}\n")
  return content


def open_file(file_path):
  file_content = ""
  try:
    with open(file_path, "r", encoding="utf-8") as auto:
      file_content = auto.read()
      auto.close()
  except:
    logging.error(
        f"Skipping this file because it cannot be opened: {input}\n"
    )
  return file_content


def save_file(output_path, content):
  try:
    with open(output_path, "w", encoding="utf-8") as auto:
      auto.write(content)
      auto.close()
  except:
    logging.error(
        f"Cannot save the file to: {output_path}\n"
    )


def trim_path_to_subdir(full_path, subdir):
  """Trims a full path up to a given subdirectory.

  Args:
      full_path: The full path to trim.
      subdir: The subdirectory to trim to (e.g., '/en/').

  Returns:
      The trimmed path, or the original path if the subdirectory is not found.
  """

  try:
      index = full_path.index(subdir)
      return full_path[: index + len(subdir)]
  except ValueError:
      return full_path

main()