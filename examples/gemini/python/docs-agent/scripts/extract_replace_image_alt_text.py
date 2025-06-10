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
import re

from absl import logging
from docs_agent.interfaces import run_console as console
from docs_agent.preprocess.extract_image_path import extract_image_path_from_html
from docs_agent.preprocess.extract_image_path import extract_image_path_from_markdown
from docs_agent.utilities.config import return_config_and_product
from docs_agent.utilities.helpers import resolve_path
import yaml


def main(input_path: str = sys.argv[1]):
  """
  Main function to extract image paths and alt text, and update markdown files.

  Args:
      input_path: The path to the input file or directory.
  """
  # Create a file containing image paths and alt text
  create_image_paths_file(input_path, replace_alt_text=True)
  # Update the markdown files in place with the new image paths and alt text
  update_markdown_files(yaml_file_path="agent_out/file_alt_text.yaml")


def create_image_paths_file(input_path: str, replace_alt_text: bool = False)-> None:
  """
  Creates a file containing image paths and alt text.

  Args:
      input_path: The path to the input file.
      replace_alt_text: Whether to replace the alt text.
  """
  dir_name = "agent_out"
  if input_path.startswith("~/"):
    input_path = os.path.expanduser(input_path)
  input_path = os.path.realpath(os.path.join(os.getcwd(), input_path))
  paths_plain_text = ""
  file_alt_text = {}
  if os.path.isdir(input_path):
    for root, _, files in os.walk(resolve_path(input_path)):
      for file in files:
        file_path = os.path.realpath(os.path.join(root, file))
        image_obj = parse_files(file_path)
        for path in image_obj["full_image_paths"]:
          paths_plain_text += path + "\n"
        if replace_alt_text:
          file_alt_text.update(generate_alt_text_dictionary(file_path, replace_alt_text=replace_alt_text))
  else:
    image_obj = parse_files(os.path.realpath(input_path))
    for path in image_obj["full_image_paths"]:
      paths_plain_text += path + "\n"
    if replace_alt_text:
      file_alt_text = generate_alt_text_dictionary(input_path, replace_alt_text=replace_alt_text)
  if not os.path.exists(dir_name):
    os.makedirs(dir_name)
  if replace_alt_text:
    save_file(dir_name + "/file_alt_text.yaml", yaml.dump(file_alt_text))
  save_file(dir_name + "/image_paths.txt", paths_plain_text)


def generate_alt_text_dictionary(input_file: str, replace_alt_text: bool = False)-> dict:
  """
  Generates a dictionary containing alt text for each image in the input file.

  Args:
      input_file: The path to the input file.
      replace_alt_text: Whether to replace the alt text.

  Returns:
      A dictionary containing the alt text for each image in the input file.
  """
  prompt = """When you generate a response for alt text, your suggestion should
  not start with Picture of, Image of, or Screenshot of. Your new alt text
  suggestion must be fewer than 125 characters. Do not exceed 125 characters.
  Provide the option that is most suitable for alt text. Output only the alt
  text suggestion. Do not include any explanations or commentary. Do not include
  end punctuation. Using the above information as context, provide concise,
  descriptive alt text for this image that captures its essence and is suitable
  for users with visual impairments. Use any existing alt text found in the
  information above for context."""
  paths_plain_text = ""
  summary = ""
  file_alt_text = {}
  loaded_config, product_config = return_config_and_product(
      config_file="config.yaml", product=[""]
  )
  if input_file.endswith(".md" or input_file.endswith(".html")):
    # file_content = open_file(input_file)
    image_obj = parse_files(input_file)
    if image_obj["full_image_paths"]:
      print(f"Generating summary for: {input_file}")
      summary = console.ask_model_with_file(product_configs=product_config,
                                            question="Summarize this file.",
                                            file=input_file,
                                            return_output=True)
    else:
      print(f"No images found for: {input_file}")
      return file_alt_text
    alt_texts = []
    for path in image_obj["full_image_paths"]:
      paths_plain_text += path + "\n"
      if replace_alt_text:
        print(f"Generating alt text for: {path}")
        alt_text = console.ask_model_with_file(product_configs=product_config,
                                               question= summary + "\n" + prompt,
                                               file=path,
                                               return_output=True
                                               )
        if alt_text is None:
          alt_texts.append("")
        else:
          alt_texts.append(alt_text.strip())
    file_alt_text[input_file] = {"page_summary": summary.strip(),
                                 "image_paths": image_obj["image_paths"],
                                 "full_image_paths": image_obj["full_image_paths"],
                                 "alt_texts": alt_texts}
  return file_alt_text


def parse_files(input_file: str) -> dict[list[str], list[str]]:
  """
  Parses a file (markdown or html) to extract image paths.

  Args:
      input_file: The path to the input file.

  Returns:
      A dictionary containing the image paths and full image paths.
  """
  if input_file.endswith(".md"):
    file_content = open_file(input_file)
    image_paths = extract_image_path_from_markdown(file_content)
  elif input_file.endswith(".html") or input_file.endswith(".htm"):
    file_content = open_file(input_file)
    image_paths = extract_image_path_from_html(file_content)
  else:
    image_paths = []
    # This can get noisy so better to log as info.
    logging.info("Skipping this file since it is not a markdown or html file: " + input_file)
  image_obj = {}
  full_image_paths = []
  for image_path in image_paths:
    dir_path = os.path.dirname(input_file)
    if (image_path.startswith("http://") or image_path.startswith("https://")):
      logging.warning(f"Skipping this image path since it is a URL: {image_path}\n")
    if image_path.startswith("./"):
      image_path = image_path.removeprefix("./")
      image_path = os.path.join(dir_path, image_path)
      full_image_paths.append(image_path)
    elif image_path[0].isalpha():
      image_path = os.path.join(dir_path, image_path)
      full_image_paths.append(image_path)
    elif image_path.startswith("/") and "/devsite/" in input_file:
      # If the document is part of devsite, the path needs to be trimmed to the
      # subdirectory (returns devsite tenant path) and then joined with the
      # image path
      devsite_path = trim_path_to_subdir(input_file, "en/")
      image_path = image_path.removeprefix("/")
      image_path = os.path.join(devsite_path, image_path)
      full_image_paths.append(image_path)
    else:
      logging.error(f"Skipping this image path because it cannot be parsed: {image_path}\n")
  image_obj["full_image_paths"] = full_image_paths
  image_obj["image_paths"] = image_paths
  return image_obj


def open_file(file_path):
  """
  Opens a file and returns its content.

  Args:
      file_path: The path to the file.

  Returns:
      The content of the file as a string, or an empty string if the file
      cannot be opened.
  """
  file_content = ""
  try:
    with open(file_path, "r", encoding="utf-8") as auto:
      file_content = auto.read()
      auto.close()
  except:
    logging.error(
        f"Skipping this file because it cannot be opened: {file_path}\n"
    )
  return file_content


def save_file(output_path, content):
  """
  Saves content to a file.

  Args:
      output_path: The path to the output file.
      content: The content to be written to the file.
  """
  try:
    with open(output_path, "w", encoding="utf-8") as auto:
      auto.write(content)
      auto.close()
  except:
    logging.error(
        f"Cannot save the file to: {output_path}\n"
    )


def process_markdown_with_yaml(yaml_file_path: str) -> dict[str, str]:
  """
  Reads a YAML file, processes the referenced Markdown files (replacing
  image paths and adding alt text), and updates the Markdown files
  in place.

  Args:
      yaml_file_path: Path to the YAML file.

  Returns:
      A dictionary containing the modified markdown content.
  """
  try:
    with open(yaml_file_path, "r", encoding="utf-8") as yaml_file:
      yaml_data = yaml.safe_load(yaml_file)
  except (FileNotFoundError, yaml.YAMLError) as e:
    print(f"Error reading or parsing YAML file: {e}")
    return {}

  modified_markdown_files = {}

  for markdown_file_path, markdown_data in yaml_data.items():
    try:
      with open(markdown_file_path, "r", encoding="utf-8") as md_file:
        markdown_content = md_file.read()
    except FileNotFoundError as e:
      print(f"Error reading Markdown file: {markdown_file_path} - {e}")
      # Store empty string for failed files
      modified_markdown_files[markdown_file_path] = ""
      continue  # Skip to the next Markdown file
    # Extract relevant data from YAML, with checks for existence
    if not all(key in markdown_data for key in ["image_paths", "full_image_paths", "alt_texts"]):
      print(f"YAML data for {markdown_file_path} is missing required fields.")
      modified_markdown_files[markdown_file_path] = ""
      continue

    image_paths = markdown_data["image_paths"]
    full_image_paths = markdown_data["full_image_paths"]
    alt_texts = markdown_data["alt_texts"]

    if len(image_paths) != len(full_image_paths) or len(image_paths) != len(alt_texts):
      print(f"Inconsistent image data lengths for {markdown_file_path}.")
      modified_markdown_files[markdown_file_path] = ""
      continue

    # Create a mapping from short image path to full image path and alt text
    image_map = {}
    for i in range(len(image_paths)):
      image_map[image_paths[i]] = (full_image_paths[i], alt_texts[i])

    # Function to replace image paths and add alt text
    def replace_image(match):
      image_path = match.group(1)
      if image_path in image_map:
        full_path, alt_text = image_map[image_path]
        return f"![{alt_text}]({image_path})"
      else:
        print(f"Warning: No full image path found for: {image_path} in {markdown_file_path}")
        return match.group(0)  # Return the original Markdown
    # Regex to find Markdown image syntax
    markdown_content = re.sub(r"!\[.*?\]\((.*?)\)", replace_image, markdown_content)
    modified_markdown_files[markdown_file_path] = markdown_content

  return modified_markdown_files


def update_markdown_files(yaml_file_path: str) -> None:
  """
  Updates markdown files with the new image paths and alt text from the YAML file.

  Args:
      yaml_file_path: Path to the YAML file containing image data.
  """
  modified_markdown = process_markdown_with_yaml(yaml_file_path)

  for file_path, new_content in modified_markdown.items():
    if new_content != "":  # Only update if processing was successful
      try:
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(new_content)
          print(f"Successfully updated: {file_path}")
      except Exception as e:
        print(f"Error writing to {file_path}: {e}")


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