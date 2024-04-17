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

import urllib, os
from flask import url_for
import bs4
import typing
from pathlib import Path, PurePath
import markdown


# This retrieves the project root, regardless of module path
def get_project_path() -> Path:
    return Path(__file__).parent.parent.parent


# Function to resolve path. If no base_dir is specified, use the project root
def resolve_path(rel_or_abs_path: str, base_dir: Path = get_project_path()):
    path = rel_or_abs_path.strip()
    if path.startswith("/"):
        return path
    else:
        return os.path.join(base_dir, path)


# Function to add / to a path.
def end_path_backslash(input_path: str):
    if not input_path.endswith("/"):
        input_path = input_path + "/"
    return input_path


# Function to remove / from a path to combine with url
def start_path_no_backslash(input_path: str):
    if input_path.startswith("/"):
        # Drop first character
        input_path = input_path[1:]
    return input_path


# Function to create a path to a copy directory in the parent directory.
# Backup dir is relevant to the input path root
def parallel_backup_dir(rel_or_abs_path: str, backup_dir_name: str = "backup"):
    path = Path(resolve_path(rel_or_abs_path))
    pure_path = PurePath(resolve_path(rel_or_abs_path))
    backup_dir = (
        end_path_backslash(str(path.parent.absolute()))
        + end_path_backslash(start_path_no_backslash(backup_dir_name))
        + str(pure_path.name)
    )
    return backup_dir


# Function to return the parent directory
def return_pure_dir(rel_or_abs_path: str):
    pure_path = PurePath(resolve_path(rel_or_abs_path))
    return str(pure_path.name)


# This function adds a scheme URL
def add_scheme_url(url: str, scheme: str = "https"):
    return url if "://" in url else f"{scheme}://{url}"


# Parse a response containing a list of related questions from the language model
# and convert it into an HTML-based list.
def parse_related_questions_response_to_html_list(response):
    soup = bs4.BeautifulSoup(response, "html.parser")
    for item in soup.find_all("li"):
        if item.find("code"):
            # If there are <code> tags, strip the tags.
            text = item.text
            link = soup.new_tag(
                "a",
                href=url_for("chatui.question", ask=urllib.parse.quote_plus(text)),
            )
            link.string = text
            item.string = ""
            item.code = ""
            item.append(link)
        elif item.find("p"):
            # If there are <p> tags, strip the tags.
            text = item.find("p").text
            link = soup.new_tag(
                "a",
                href=url_for("chatui.question", ask=urllib.parse.quote_plus(text)),
            )
            link.string = text
            item.string = ""
            item.append(link)
        elif item.string is not None:
            link = soup.new_tag(
                "a",
                href=url_for(
                    "chatui.question", ask=urllib.parse.quote_plus(item.string)
                ),
            )
            link.string = item.string
            item.string = ""
            item.append(link)
    return soup


# Allows us to build a list of html, for example for fact checker and limit to
# a max_count. Optional section_content to display content chunks along with URLs
# This is not in use, but a good example to better manipulate data
def build_list_html_links(
    urls: list,
    section_titles: list,
    page_titles: list,
    distances: list,
    section_content: typing.Optional[list] = None,
    max_count: typing.Optional[int] = None,
):
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


# Build an html URL link
def named_link_html(url: str, label: str = "", **kwargs):
    soup = bs4.BeautifulSoup("")
    final_url = add_scheme_url(url)
    attrs = dict(href=f"{final_url}", target=f"_blank", **kwargs)
    tag = soup.new_tag(name="a", attrs=attrs)
    # leading and trailing blank space doesn't get removed?
    tag.string = label.strip()
    return tag.prettify()


def named_link_md(url: str, label: str = ""):
    final_url = add_scheme_url(url)
    link = f"[{label}]({final_url})"
    return link


# Create a top level link for a page
def trim_section_for_page_link(url: str):
    anchor_marker_url = "#"
    page_url = url.split(anchor_marker_url, 1)[0]
    return page_url


# Function to convert md to html for flask template
def md_to_html(md: str):
    html = markdown.markdown(md)
    return html
