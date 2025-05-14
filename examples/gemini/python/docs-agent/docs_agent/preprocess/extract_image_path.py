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

import os

from absl import logging
from bs4 import BeautifulSoup as bs4
from docs_agent.utilities.helpers import open_file
from docs_agent.utilities.helpers import trim_path_to_subdir
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class ImgExtractor(Treeprocessor):
    """
    This class is a Markdown treeprocessor that extracts all images from a
    Markdown document and appends them to the markdown.images list.
    """

    def run(self, doc):
        """Find all images and append to markdown.images."""
        self.md.images = []
        self.md.alt_texts = []
        self.md.image_titles = []
        for image in doc.findall(".//img"):
            self.md.images.append(image.get("src"))
            self.md.alt_texts.append(image.get("alt"))
            if image.get("title") is not None:
                self.md.image_titles.append(image.get("title"))
            else:
                self.md.image_titles.append("")


class ImgExtExtension(Extension):
    """
    This class is a Markdown extension that registers the ImgExtractor
    treeprocessor.
    """

    def extendMarkdown(self, md):
        """Register the ImgExtractor treeprocessor with the Markdown instance."""
        img_ext = ImgExtractor(md)
        md.treeprocessors.register(img_ext, "img_ext", 15)


def extract_image_path_from_markdown(markdown_text: str) -> list[str]:
    """Extracts all image paths from a markdown text."""
    md = markdown.Markdown(extensions=[ImgExtExtension()])
    md.convert(markdown_text)
    return md.images


def extract_image_alt_text_from_markdown(markdown_text: str) -> list[str]:
    """Extracts all image paths from a markdown text."""
    md = markdown.Markdown(extensions=[ImgExtExtension()])
    md.convert(markdown_text)
    return md.alt_texts


def extract_image_title_from_markdown(markdown_text: str) -> list[str]:
    """Extracts all image paths from a markdown text."""
    md = markdown.Markdown(extensions=[ImgExtExtension()])
    md.convert(markdown_text)
    return md.image_titles


def extract_image_path_from_html(html_text: str) -> list[str]:
    """Extracts all image paths from a html page."""
    soup = bs4(html_text, "html.parser")
    images = []
    for img in soup.findAll("img"):
        images.append(img["src"])
    return images


def extract_image_alt_text_from_html(html_text: str) -> list[str]:
    """Extracts all image paths from a html page."""
    soup = bs4(html_text, "html.parser")
    alt_text = []
    for img in soup.findAll("img"):
        alt_text.append(img["alt"])
    return alt_text


def extract_image_title_from_html(html_text: str) -> list[str]:
    """Extracts all image paths from a html page."""
    soup = bs4(html_text, "html.parser")
    title = []
    for img in soup.findAll("img"):
        title.append(img["title"])
    return title


def parse_md_html_files_for_images(input_file: str) -> dict[list[str], list[str]]:
    """
    Parses a file (markdown or html) to extract image paths.

    Args:
        input_file: The path to the input file.

    Returns:
        A dictionary containing the image paths, full image paths, and current
        alt text.
    """
    image_titles = []
    alt_texts = []
    image_paths = []
    if input_file.endswith(".md"):
        file_content = open_file(input_file)
        image_paths = extract_image_path_from_markdown(file_content)
        alt_texts = extract_image_alt_text_from_markdown(file_content)
        image_titles = extract_image_title_from_markdown(file_content)
    elif input_file.endswith(".html") or input_file.endswith(".htm"):
        file_content = open_file(input_file)
        image_paths = extract_image_path_from_html(file_content)
        alt_texts = extract_image_alt_text_from_html(file_content)
        image_titles = extract_image_title_from_html(file_content)
    else:
        # This can get noisy so better to log as info.
        logging.info(
            "Skipping this file since it is not a markdown or html file: " + input_file
        )
    image_def = {}
    full_image_paths = []
    for image_path in image_paths:
        dir_path = os.path.dirname(input_file)
        if image_path.startswith("http://") or image_path.startswith("https://"):
            logging.warning(
                f"Skipping this image path since it is a URL: {image_path}\n"
            )
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
            logging.error(
                f"Skipping this image path because it cannot be parsed: {image_path}\n"
            )
    image_def["full_image_paths"] = full_image_paths
    image_def["image_paths"] = image_paths
    image_def["alt_texts"] = alt_texts
    image_def["image_titles"] = image_titles
    image_obj = {"images": image_def}
    return image_obj
