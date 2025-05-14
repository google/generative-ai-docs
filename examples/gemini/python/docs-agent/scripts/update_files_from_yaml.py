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
This script updates markdown files with image paths and alt text from a YAML file.

Usage:
  python update_files_from_yaml.py

Example:
  python update_files_from_yaml.py
"""

import re
import sys

from docs_agent.utilities.helpers import save_file
import yaml


def main(input_path: str = sys.argv[1]):
    """Main function to update markdown files.

    Args:
        input_path: The path to the input file or directory.
    """
    # Update the markdown files in place with the new image paths and alt text
    update_markdown_files(yaml_file_path=input_path)


def process_markdown_with_yaml(yaml_file_path: str) -> dict[str, str]:
    """
    Reads a YAML file, processes the referenced Markdown files (replacing
    image paths and update alt text with LLM alt text), and updates the Markdown
    files in place.

    Args:
        yaml_file_path: Path to the YAML file.

    Returns:
        A dictionary containing the modified markdown content.
    """
    # This allows reading in a response from the LLM that is not a valid YAML
    # file.
    try:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            file_content = file.read()
    except FileNotFoundError as e:
        print(f"Error: YAML file not found: {yaml_file_path} - {e}")
        return {}

    # Extract YAML content using regex.
    match = re.search(r"```yaml\n(.*?)\n```", file_content, re.DOTALL | re.IGNORECASE)
    if not match:
        print("Error: No YAML content found within ```yaml ... ``` tags.")
        return {}

    yaml_content = match.group(1)
    try:
        yaml_data = yaml.safe_load(yaml_content)  # Parse the extracted YAML.
    except yaml.YAMLError as e:
        print(f"Error parsing YAML content: {e}")
        return {}

    modified_markdown_files = {}

    # Iterate through the list of files in the YAML
    if "files" not in yaml_data:
        print("Error: YAML file does not contain a 'files' list.")
        return {}

    # Process each Markdown file listed in 'files'
    for file_data in yaml_data["files"]:
        markdown_file_path = file_data["path"]
        try:
            with open(markdown_file_path, "r", encoding="utf-8") as md_file:
                markdown_content = md_file.read()
        except FileNotFoundError as e:
            print(f"Error reading Markdown file: {markdown_file_path} - {e}")
            modified_markdown_files[markdown_file_path] = ""
            continue

        image_data = file_data.get("images")
        # If no image data is found, skip this file.
        if not image_data or not image_data.get("full_image_paths"):
            continue

        image_paths = image_data.get("image_paths", [])
        full_image_paths = image_data.get("full_image_paths", [])
        alt_texts = image_data.get("alt_texts", [])  # alt_texts, not llm_alt_texts
        image_titles = image_data.get("image_titles", [])
        llm_alt_texts = image_data.get("llm_alt_texts", [])

        # If llm_alt_texts are present, use those; otherwise, fall back to alt_texts,
        # or an empty string if neither exists.
        final_alt_texts = []
        for i in range(max(len(image_paths), len(llm_alt_texts), len(alt_texts))):
            if i < len(llm_alt_texts):
                final_alt_texts.append(llm_alt_texts[i])
            elif i < len(alt_texts):
                final_alt_texts.append(alt_texts[i])
            else:
                final_alt_texts.append("")
        # Ensure image_titles has the same length as other lists
        final_image_titles = []
        for i in range(len(image_paths)):
            if i < len(image_titles):
                final_image_titles.append(image_titles[i])
            else:
                final_image_titles.append("")  # Pad with empty strings

        if not (
            len(image_paths)
            == len(full_image_paths)
            == len(final_alt_texts)
            == len(final_image_titles)
        ):
            print(f"Inconsistent image data lengths for {markdown_file_path}.")
            modified_markdown_files[markdown_file_path] = ""
            continue

        # Build a dictionary mapping image paths to image data
        # (full image path, alt text, image title)
        image_map = {}
        for i in range(len(image_paths)):
            image_map[image_paths[i]] = (
                full_image_paths[i],
                final_alt_texts[i],
                final_image_titles[i],
            )

        def replace_image(match):
            image_path = match.group(2).strip()
            if image_path in image_map:
                _, alt_text, image_title = image_map[image_path]
                # Build the Markdown image tag, handling titles
                if image_title:
                    return f'![{alt_text}]({image_path} "{image_title}")'
                else:
                    return f"![{alt_text}]({image_path})"
            else:
                print(
                    f"Warning: No matching image path found for: {image_path} in {markdown_file_path}"
                )
                return match.group(0)

        # Improved regex to handle existing titles
        markdown_content = re.sub(
            r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\s*\)', replace_image, markdown_content
        )
        modified_markdown_files[markdown_file_path] = markdown_content

    return modified_markdown_files


def update_markdown_files(yaml_file_path: str) -> None:
    """
    Updates the markdown files with the new image paths and alt text from the
    YAML file.

    Args:
        yaml_file_path: Path to the YAML file containing the image data.
    """
    modified_markdown = process_markdown_with_yaml(yaml_file_path)
    save_file(output_path="agent_out/md_output.yaml", content=modified_markdown)

    for file_path, new_content in modified_markdown.items():
        if new_content != "":  # Only update if processing was successful
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                    print(f"Successfully updated: {file_path}")
            except Exception as e:
                print(f"Error writing to {file_path}: {e}")


main()
