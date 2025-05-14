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

"""General utility functions"""

import os
import typing
import urllib

from absl import logging
import bs4
from flask import url_for
import bs4
import html
import typing
from pathlib import Path, PurePath
import markdown
import yaml
from PIL import Image


def expand_user_path(path_str: typing.Optional[str]) -> typing.Optional[str]:
    """
    Expands a path that starts with '~' to the user's home directory.

    Args:
        path_str: The path string to expand.

    Returns:
        The expanded path string, or the original path string if it doesn't
        start with '~'.
    """
    if path_str and path_str.startswith("~/"):
        return os.path.expanduser(path_str)
    return path_str


def resolve_and_ensure_path(
    path_str: typing.Optional[str], check_exists: bool = True
) -> typing.Optional[str]:
    """
    Resolves a path (handling '~') and optionally checks if it exists.

    Args:
        path_str: The path string to resolve.
        check_exists: If True, checks if the resolved path exists and logs an error if not.

    Returns:
        The resolved absolute path as a string, or None if input is None or check fails.
    """
    if not path_str:
        return None

    expanded_path = expand_user_path(path_str)
    try:
        resolved = resolve_path(expanded_path)
        resolved_path = Path(resolved)

        if check_exists and not resolved_path.exists():
            logging.error(f"[Error] Cannot access the input path: {resolved_path}")
            return None
        return str(resolved_path)
    except FileNotFoundError as e:
        logging.error(f"[Error] Failed to resolve path: {e}")
        return None
    except Exception as e:
        logging.error(
            f"[Error] An unexpected error occurred resolving path '{path_str}': {e}"
        )
        return None


def create_output_directory(output_path_str: str) -> typing.Optional[str]:
    """
    Determines the output directory path, creates it if necessary,
    and returns the full output file path.

    Args:
        output_path_str: The desired output file path (can be relative, absolute, or start with ~).

    Returns:
        The full absolute path to the output file, or None if directory creation fails.
    """
    if not output_path_str or output_path_str.lower() == "none":
        return None

    output_path_str = expand_user_path(output_path_str)
    output_path_obj = Path(output_path_str)

    if output_path_obj.is_absolute():
        base_out = output_path_obj.parent
        out_filename = output_path_obj.name
    else:
        # Default to project's agent_out directory
        try:
            base_out = Path(get_project_path()) / "agent_out"
        except FileNotFoundError:
            logging.warning(
                "Project root directory not found, using current directory for agent_out."
            )
            base_out = Path.cwd() / "agent_out"
        out_filename = output_path_obj.name

    # Create directory in the following order:
    # 1. The specified output directory
    # 2. The default agent_out directory in the project root
    # 3. A temporary directory in /tmp
    potential_dirs = [
        base_out,
        Path(os.path.expanduser("~/docs_agent/agent_out")),
        Path("/tmp/docs_agent/agent_out"),
    ]

    created_dir = None
    for potential_dir in potential_dirs:
        try:
            potential_dir.mkdir(parents=True, exist_ok=True)
            # Check write permissions
            test_file = potential_dir / ".writable_test"
            try:
                test_file.touch()
                test_file.unlink()
                created_dir = potential_dir
                break
            except OSError:
                logging.warning(
                    f"Cannot write to directory: {potential_dir}. Trying next fallback."
                )
                continue
        except OSError as e:
            logging.warning(
                f"Failed to create or access directory {potential_dir}: {e}. Trying next fallback."
            )

    if not created_dir:
        logging.error("Failed to create any suitable output directory.")
        return None

    full_output_path = created_dir / out_filename
    return str(full_output_path)


def get_project_path(marker: str = "config.yaml") -> Path:
    """
    Finds the project root directory by searching upwards for a specified marker file.

    Args:
        marker: The name of the file to search for (default is "config.yaml").

    Returns:
        The path to the project root directory.

    Raises:
        FileNotFoundError: If the marker file is not found.
    """
    start_dir = None
    try:
        # Start search from the directory containing this helpers.py file
        start_dir = Path(__file__).resolve().parent
    except NameError:
        logging.warning(
            "'__file__' not defined. Using current working directory as start path. This might be unreliable."
        )
        start_dir = Path.cwd()
    except Exception as e:
        logging.warning(
            f"Error determining start directory using '__file__': {e}. Falling back to CWD."
        )
        start_dir = Path.cwd()

    current_dir: Path = start_dir
    while True:
        # Checks if the current directory contains the config.yaml file
        # If so, return the current directory as the project root
        # If not, try the parent directory
        if (current_dir / marker).exists():
            _project_root_path_cache = current_dir
            return _project_root_path_cache

        parent_dir = current_dir.parent
        if parent_dir == current_dir:
            # Reached the filesystem root
            raise FileNotFoundError(
                f"Could not find project marker '{marker}' from {start_dir}. "
                f"Make sure that '{marker}' exists at the project root directory."
            )
        current_dir = parent_dir


def resolve_path(rel_or_abs_path: str, base_dir: Path = get_project_path()) -> str:
    """
    Resolves a relative or absolute path to a canonical absolute path.

    Args:
        rel_or_abs_path: The path to resolve (can be relative or absolute).
        base_dir: The base directory to use for relative paths (defaults to the project root).

    Returns:
        The absolute path as a string.
    """
    path_str = rel_or_abs_path.strip()
    path_obj = Path(path_str)

    # If the path is absolute, return it as is.
    if path_obj.is_absolute():
        return str(path_obj.resolve())
    else:
        # Joins the path with / to ensure that the path is absolute.
        resolved = (base_dir / path_obj).resolve()
        return str(resolved)


def end_path_backslash(input_path: str):
    """
    Adds a trailing backslash to a path if it doesn't already have one.

    Args:
        input_path: The path to add the backslash to.

    Returns:
        The path with a trailing backslash.
    """
    if not input_path.endswith("/"):
        input_path = input_path + "/"
    return input_path


def start_path_no_backslash(input_path: str):
    """
    Removes a leading backslash from a path if it has one.

    Args:
        input_path: The path to remove the backslash from.

    Returns:
        The path without a leading backslash.
    """
    if input_path.startswith("/"):
        # Drop first character
        input_path = input_path[1:]
    return input_path


def parallel_backup_dir(rel_or_abs_path: str, backup_dir_name: str = "backup"):
    path = Path(resolve_path(rel_or_abs_path))
    pure_path = PurePath(resolve_path(rel_or_abs_path))
    backup_dir = (
        end_path_backslash(str(path.parent.absolute()))
        + end_path_backslash(start_path_no_backslash(backup_dir_name))
        + str(pure_path.name)
    )
    return backup_dir


def return_pure_dir(rel_or_abs_path: str) -> str:
    """
    Returns the parent directory of a given path.

    Args:
        rel_or_abs_path: The path to get the parent directory of.

    Returns:
        The parent directory as a string.
    """
    pure_path = PurePath(resolve_path(rel_or_abs_path))
    return str(pure_path.name)


def add_scheme_url(url: str, scheme: str = "https") -> str:
    """
    Adds a scheme (e.g., "https://") to a URL if it doesn't already have one.

    Args:
        url: The URL to add the scheme to.
        scheme: The scheme to add (default is "https").

    Returns:
        The URL with the scheme added, or the original URL if it already has a scheme.
    """
    return url if "://" in url else f"{scheme}://{url}"


def parse_related_questions_response_to_html_list(response):
    """
    Parses a related questions response and converts it to an HTML list.

    Args:
        response: The response containing related questions (HTML).

    Returns:
        A BeautifulSoup object representing the HTML list.
    """
    soup = bs4.BeautifulSoup(response, "html.parser")
    for item in soup.find_all("li"):
        if item.find("code"):
            # If there are <code> tags, strip the tags.
            text = item.text
        elif item.find("p"):
            # If there are <p> tags, strip the tags.
            text = item.text  # Corrected: Get the full text of the <li>
        elif item.string is not None:
            text = item.string
        else:
            continue  # Skip if no text content

        link = soup.new_tag(
            "a",
            href=url_for("chatui.question", ask=urllib.parse.quote_plus(text)),
        )
        link.string = text
        item.clear()  # Remove all existing children of the <li>
        item.append(link)
    return soup


def build_list_html_links(
    urls: list,
    section_titles: list,
    page_titles: list,
    distances: list,
    section_content: typing.Optional[list] = None,
    max_count: typing.Optional[int] = None,
):
    """
    Builds an HTML list of links from given URLs, titles, and distances.

    Args:
        urls: A list of URLs.
        section_titles: A list of section titles corresponding to the URLs.
        page_titles: A list of page titles corresponding to the URLs.
        distances: A list of distances corresponding to the URLs.
        section_content: Optional list of section content corresponding to the URLs.
        max_count: Optional maximum number of links to include in the list.

    Returns:
        An HTML string representing the list of links.
    """
    if max_count == None:
        max_count = len(urls)
    md_list = ""
    for count in range(max_count):
        section_url = named_link_md(urls[count], section_titles[count])
        page_url = named_link_md(
            trim_section_for_page_link(urls[count]), page_titles[count]
        )
        if max_count == 1:
            md_list += f"{section_url} from the {page_url} page"
            if distances != None:
                md_list += f"\n\nDistance: {distances[count]}\n"
            if section_content != None:
                md_list += f"\n\n{section_content[count]}\n"
        else:
            md_list += f"- {section_url} from the {page_url} page\n"
            md_list += f"\n\n  Distance: {distances[count]}\n"
            if section_content != None:
                md_list += f"\n\n  {markdown.markdown(section_content[count])}\n"
    html_list = markdown.markdown(md_list)
    return html_list


# These functions are made to be used in a Jinja template when rendering a page


def named_link_html(url: str, label: str = "", **kwargs):
    """Builds an HTML URL link with optional attributes.

    Args:
        url: The URL for the link.
        label: The text label for the link.
        **kwargs: Additional HTML attributes (e.g., class, id, title).

    Returns:
        A string containing the HTML link.
    """
    soup = bs4.BeautifulSoup("", "html.parser")
    final_url = add_scheme_url(url)
    attrs = {"href": final_url, "target": "_blank"}
    for k, v in kwargs.items():
        # Remove trailing underscore from attribute names
        key = k.rstrip("_")
        attrs[key] = v
    tag = soup.new_tag(name="a", attrs=attrs)
    tag.append(label)

    attr_string = " ".join(f'{k}="{html.escape(str(v))}"' for k, v in attrs.items())
    return f"<a {attr_string}>{label}</a>"  # Directly use label


def named_link_md(url: str, label: str = ""):
    """Builds a Markdown URL link.

    Args:
        url: The URL for the link.
        label: The text label for the link.

    Returns:
        A string containing the Markdown link.
    """
    final_url = add_scheme_url(url)
    link = f"[{label}]({final_url})"
    return link


def trim_section_for_page_link(url: str):
    """
    Trims a URL to remove the section part, keeping only the page URL.

    Args:
        url: The URL to trim.

    Returns:
        The page URL without the section part.
    """
    anchor_marker_url = "#"
    page_url = url.split(anchor_marker_url, 1)[0]
    return page_url


def md_to_html(md: str):
    """
    Converts a Markdown string to HTML.

    Args:
        md: The Markdown string to convert.

    Returns:
        The HTML representation of the Markdown string.
    """
    html = markdown.markdown(md)
    return html


def open_file(file_path) -> str:
    """
    Opens a text file and returns its content.

    Args:
        file_path: The path to the file.

    Returns:
        The content of the file as a string, or an empty string if the file
        cannot be opened.
    """
    file_content = ""
    file_type = identify_file_type(file_path)
    if file_type == "text":
        try:
            with open(file_path, "r", encoding="utf-8") as auto:
                file_content = auto.read()
                auto.close()
        except:
            logging.error(f"Cannot open the text {file_path}\n")
    return file_content


def open_image(file_path) -> typing.Optional[Image.Image]:
    """
    Opens an image file and returns its content.
    """
    loaded_image = None
    file_type = identify_file_type(file_path)
    if file_type == "image":
        try:
            with open(file_path, "rb") as image:
                loaded_image = Image.open(image)
                loaded_image.load()
        except:
            logging.error(f"Cannot open the image {file_path}\n")
    return loaded_image


def save_file(output_path, content):
    """
    Saves content to a file.

    Args:
        output_path: The path to the output file.
        content: The content to be written to the file.
    """
    if output_path.endswith(".yaml"):
        try:
            with open(output_path, "w", encoding="utf-8") as auto:
                auto.write(yaml.dump(content))
                auto.close()
        except:
            logging.error(f"Cannot save the file to: {output_path}\n")
    else:
        try:
            with open(output_path, "w", encoding="utf-8") as auto:
                auto.write(content)
                auto.close()
        except:
            logging.error(f"Cannot save the file to: {output_path}\n")


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


def identify_file_type(file_path: str) -> str:
    """
    Identifies the type of a file based on its extension.

    Args:
        file_path: The path to the file.

    Returns:
        The file type (e.g., "text", "image", "audio", "video").
    """
    file_type = "text"
    file_path = Path(file_path)
    file_ext = file_path.suffix
    image_extensions = [".png", ".jpeg", ".jpg", ".gif"]
    audio_extensions = [".wav", ".mp3", ".flac", ".aiff", ".aac", ".ogg"]
    video_extensions = [
        ".mp4",
        ".mov",
        ".avi",
        ".x-flv",
        ".mpg",
        ".webm",
        ".wmv",
        ".3gpp",
    ]

    if file_ext in image_extensions:
        file_type = "image"
    elif file_ext in audio_extensions:
        file_type = "audio"
    elif file_ext in video_extensions:
        file_type = "video"
    return file_type
