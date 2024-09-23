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

import typing
import markdown
import bs4
import re, os
from absl import logging
from docs_agent.models import tokenCount
import frontmatter
from docs_agent.utilities.helpers import add_scheme_url


class Section:
    def __init__(
        self,
        id: int,
        name_id: str,
        page_title: str,
        section_title: str,
        level: int,
        previous_id: int,
        parent_tree: list[int],
        token_count: float,
        content: str,
        url: typing.Optional[str] = None,
        origin_uuid: typing.Optional[str] = None,
        md_hash: typing.Optional[str] = None,
        uuid: typing.Optional[str] = None,
    ):
        self.id = id
        self.name_id = name_id
        self.page_title = page_title
        self.section_title = section_title
        self.level = level
        self.previous_id = previous_id
        self.parent_tree = parent_tree
        self.token_count = token_count
        self.content = content
        self.url = url
        self.origin_uuid = origin_uuid
        self.md_hash = md_hash
        self.uuid = uuid

    def __str__(self):
        return f"UUID: {self.uuid}\n\
ID: {self.id}\n\
Name ID: {self.name_id}\n\
Origin UUID: {self.origin_uuid}\n\
Page title: {self.page_title}\n\
Section title: {self.section_title}\n\
URL: {self.url}\n\
Level: {self.level}\n\
Parent ID: {self.previous_id}\n\
Parent tree: {self.parent_tree}\n\
Tokens: {self.token_count}\n\
Content hash: {self.md_hash}\n"

    # Updates the content of a section using page and section title
    def updateContentTemplate(self):
        new_content = f"The section titled {self.section_title} is from the page titled {self.page_title} and has this content:\n{self.content}"
        self.content = new_content
        return self

    # Given a section, return the id of the parent. If no, parent returns 0
    # 0 is equivalent to the top of the page
    def returnDirectParentId(self):
        parent_tree = eval(self.parent_tree)
        # Prepare direct_parent variable
        if len(parent_tree) > 1:
            direct_parent = parent_tree[len(parent_tree) - 1]
        # If the curr_parent_tree has a len of 0, this means that no parents
        if len(parent_tree) == 0:
            no_parent = True
            direct_parent = 0
        else:
            no_parent = False
            direct_parent = parent_tree[len(parent_tree) - 1]
        return direct_parent

    def encodeToChromaDBNoContent(self):
        metadata = {}
        metadata.update({"section_id": int(self.id)})
        metadata.update({"section_name_id": str(self.name_id)})
        metadata.update({"section_title": str(self.section_title)})
        metadata.update({"page_title": str(self.page_title)})
        metadata.update({"section_level": int(self.level)})
        metadata.update({"previous_id": int(self.previous_id)})
        # Lists like parent_tree need to be converted to str
        metadata.update({"parent_tree": str(self.parent_tree)})
        metadata.update({"token_estimate": float(self.token_count)})
        metadata.update({"origin_uuid": str(self.origin_uuid)})
        metadata.update({"md_hash": str(self.md_hash)})
        metadata.update({"url": str(self.url)})
        return metadata

    def createChunkTitle(self):
        if self.page_title == self.section_title:
            doc_title = self.page_title
        else:
            doc_title = f"{self.page_title} - {self.section_title}"
        return doc_title

    def return_id(self):
        return self.id


def DictionarytoSection(metadata: dict) -> Section:
    if "section_id" in metadata and metadata["section_id"] != '':
        section_id = int(metadata["section_id"])
    else:
        section_id = ""
    if "section_name_id" in metadata:
        section_name_id = str(metadata["section_name_id"])
    else:
        section_name_id = ""
    if "section_title" in metadata:
        section_title = str(metadata["section_title"])
    else:
        section_title = ""
    if "page_title" in metadata:
        page_title = str(metadata["page_title"])
    else:
        page_title = ""
    if "section_level" in metadata and metadata["section_level"] != '':
        section_level = int(metadata["section_level"])
    else:
        section_level = ""
    if "previous_id" in metadata and metadata["previous_id"] != '':
        previous_id = int(metadata["previous_id"])
    else:
        previous_id = ""
    if "parent_tree" in metadata:
        parent_tree = metadata["parent_tree"]
    else:
        parent_tree = []
    if "token_estimate" in metadata and metadata["token_estimate"] != '':
        token_estimate = int(metadata["token_estimate"])
    else:
        token_estimate = ""
    if "content" in metadata:
        content = str(metadata["content"])
    else:
        content = ""
    if "URL" in metadata:
        url = str(metadata["URL"])
    elif "url" in metadata:
        url = str(metadata["url"])
    else:
        url = ""
    if "origin_uuid" in metadata:
        origin_uuid = str(metadata["origin_uuid"])
    else:
        origin_uuid = ""
    if "md_hash" in metadata:
        md_hash = str(metadata["md_hash"])
    else:
        md_hash = ""
    if "UUID" in metadata:
        UUID = str(metadata["UUID"])
    else:
        UUID = ""
    section = Section(
        id=section_id,
        name_id=section_name_id,
        page_title=page_title,
        section_title=section_title,
        level=section_level,
        previous_id=previous_id,
        parent_tree=parent_tree,
        token_count=token_estimate,
        content=content,
        url=url,
        origin_uuid=origin_uuid,
        md_hash=md_hash,
        uuid=UUID,
    )
    return section


class Page:
    def __init__(
        self,
        title: str,
        URL: str,
        section_count: int,
        metadata: typing.Optional[dict] = None,
    ):
        self.title = title
        self.URL = URL
        self.section_count = section_count
        self.metadata = metadata

    def __str__(self):
        return f"This is a page with the following properties:\n\
Title: {self.title}\n\
URL: {self.URL}\n\
Section Count: {self.section_count}\n\
Metadata: {self.metadata}\n"


# This function converts a Markdown string to plain text.
def markdown_to_text(markdown_string):
    # Remove <!-- --> lines in Markdown
    markdown_string = re.sub(r"<\!--(.*?)-->", "", markdown_string)
    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown.markdown(markdown_string)
    # Extract text
    soup = bs4.BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(string=True))
    # Remove [][] in Markdown
    text = re.sub(r"\[(.*?)\]\[(.*?)\]", "\\1", text)
    # Remove {: } in Markdown
    text = re.sub(r"\{:(.*?)\}", "", text)
    # Remove {. } in Markdown
    text = re.sub(r"\{.(.*?)\}", "", text)
    # Remove a single line `sh` in Markdown
    text = re.sub(r"(?m)^sh$", "", text)
    # Remove a single line ````sh` in Markdown
    # text = re.sub(r'(?m)^```sh$', '', text)
    # Remove code snippet tags
    # text = re.sub(r"<pre>(.*?)</pre>", "\\1", text)
    # text = re.sub(r"<code>(.*?)</code>", "\\1", text)
    # Remove variable tags
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


# This function makes a plain text chunk. It can transform markdown headers
# into plain text for files that can fit in a single chunk or multiple chunks
# Takes an input of a markdown_text and header_id_spaces on how to treat spaces
# from Header names to header ids. For example if header_id_spaces="-",
# ## My section header will get a header id of my-section-header
# This will try to give more granural context on urls by appending #my-section-header
# to URL links
def make_markdown_chunk(markdown_text, header_id_spaces):
    section_markdown = ""
    remaining_markdown = ""
    section_title = ""
    section_id = ""
    section_level = ""
    first_header = True
    section_done = False
    # Regular expression to read a header level, title, and an optional anchor id
    regex_headers = r"^(\#*)\s+(.[^\{]*)(.*?)$"
    # Regular expression to read an anchor id, format can be {#header-id} or
    # {:#header-id}
    regex_anchors = r"(?:\{\#|\{:\#)(.*)\}"
    # Regular expression to read a special RFC title case (with jinja variables)
    regex_rfc_title = r"^\{\{\s+(.*)\.(.*)\s+\}\}$"
    # Regular expression to find parantheses as those are not valid in headers
    regex_section_name = r"(.[^\(]*)"
    regex_headers_compiled = re.compile(regex_headers)
    regex_anchors_compiled = re.compile(regex_anchors)
    regex_section_name_compiled = re.compile(regex_section_name)
    regex_rfc_compiled = re.compile(regex_rfc_title)
    for line in markdown_text.split("\n"):
        if line.startswith("#") and first_header == True:
            # Looks for a header in the format of ## Header name {#header-id} or
            # Just a ## Header name
            # Level 1 doesn't require header ids as these are page anchors
            first_header = False
            match = regex_headers_compiled.search(line)
            if match:
                if match[1]:
                    section_level = len(match[1])
                if match[2]:
                    section_title = match[2]
                    section_id = re.sub(
                        " ", header_id_spaces, section_title.lower().strip()
                    )
                    section_id = clean_section_id(section_id)
                    if regex_section_name_compiled.search(section_id):
                        section_id = regex_section_name_compiled.search(section_id)[1]
                if match[3]:
                    match_id = regex_anchors_compiled.search(match[3])
                    if match_id:
                        section_id = clean_section_id(match_id[1])
                    # Checks for the special RFC case to assign a title of RFC
                    # These headers don't have ids as there is no full header title
                    match_rfc = regex_rfc_compiled.search(match[2] + match[3])
                    if match_rfc:
                        section_title = "RFC (request for comment)"
                # Removing this line as this can be added (if needed) once retrieved from the db
                # section_markdown += section_intro.format(section_title=section_title)
        elif len(section_markdown) > 100:
            # Temp solution: Do not create a chunk if the size is less than 100 chars.
            if line.startswith("#") and first_header == False:
                section_done = True
                remaining_markdown += line + "\n"
            elif not (line.startswith("#")) and section_done:
                remaining_markdown += line + "\n"
            else:
                section_markdown += line + "\n"
        else:
            section_markdown += line + "\n"
    section_level = level_to_int(section_level)
    return (
        section_id,
        section_level,
        section_title,
        section_markdown,
        remaining_markdown,
    )


# Returns an int of a level to avoid blank string
def level_to_int(level) -> int:
    if level == "":
        level = 0
    else:
        level = int(level)
    return level


# In a regular child level the length of the parent_tree should be greater
# than the current level, so for example a header 2 (level 2) may have a
# parent_tree of [0, 1], in this case we want to append the previous previous_id
# Conditions to be aware of:
# If headers are out of order, you may end up with an array level with
# the same value, such as a header 4 that ends with a parent_tree of
# [0, 1, 25, 25] indicates that you jumped from a header 2, right into a 4
def build_parent_tree(
    parent_tree: list[int], level: int, previous_id: int
) -> list[int]:
    if len(parent_tree) != level:
        first = True
        while len(parent_tree) != level:
            if len(parent_tree) >= level:
                parent_tree.pop()
            elif len(parent_tree) <= level:
                parent_tree.append(previous_id)
    return parent_tree


# This function cleans section ids from special characters
def clean_section_id(section_id: str) -> str:
    section_id = re.sub("'", "", section_id)
    section_id = re.sub("`", "", section_id)
    section_id = re.sub("\.", "", section_id)
    section_id = re.sub("\,", "", section_id)
    section_id = re.sub("#", "", section_id)
    section_id = re.sub("\?", "", section_id)
    section_id = re.sub("\/", "", section_id)
    section_id = re.sub("\{", "", section_id)
    section_id = re.sub("\}", "", section_id)
    section_id = re.sub(":", "", section_id)
    return section_id


# This function replaces Markdown's includes sections with content.
def process_markdown_includes(markdown_text, root):
    updated_markdown = ""
    for line in markdown_text.split("\n"):
        # Replaces Markdown includes with content
        if line.startswith("<<"):
            try:
                include_match = re.search("^<<(.*?)>>", line)
                include_file = os.path.abspath(root + "/" + include_match[1])
                with open(include_file, "r", encoding="utf-8") as md_include:
                    for md_line in md_include:
                        updated_markdown += md_line + "\n"
            except:
                updated_markdown += line + "\n"
        else:
            updated_markdown += line + "\n"
    return updated_markdown


# Function to verify that include exists and exports its content if it exists
def verify_file(file):
    try:
        with open(file, "r", encoding="utf-8") as mdfile:
            output = mdfile.read()
            mdfile.close()
            return output
    except FileNotFoundError:
        logging.error(f"[FileNotFound] Missing the include file: {file}")


# Takes in current section, then returns an array of
# sections that it split by lines
def split_sections_by_lines(section: Section):
    buffer = []
    for line in section.content.split("\n"):
        # Special case if line is too long - tends to be comma seperated lists
        if get_byte_size(line) > 5000:
            for item in line.split(","):
                item = item + ","
                buffer.append(item)
        else:
            buffer.append(line)
    chunks = construct_chunks(buffer)
    page_sections = []
    chunk_count = 0
    for chunk in chunks:
        # Calculate tokens for new chunk
        token_count = tokenCount.returnHighestTokens(chunk)
        # Section id needs to get bumped up
        new_section = Section(
            (section.id + chunk_count),
            section.name_id,
            section.page_title,
            section.section_title,
            section.level,
            section.previous_id,
            section.parent_tree.copy(),
            token_count,
            markdown_to_text(chunk),
        )
        chunk_count += 1
        page_sections.append(new_section)
    return page_sections
    # return page_sections, remaining_content


# This function converts Markdown page (#), section (##), and subsection (###)
# headings into plain English.
def process_markdown_page(markdown_text, header_id_spaces: str = "_"):
    page_metadata = {}
    remaining_content = markdown_text
    page_title = ""
    page_sections = []
    page_url = ""
    # Processes the frontmatter in a markdown file
    data = frontmatter.loads(markdown_text)
    if "title" in data:
        page_title = data["title"]
        remaining_content = data.content
        page_metadata = data.metadata
    if "URL" in data:
        page_url = add_scheme_url(url=data["URL"], scheme="https")
    section_id = 0
    previous_id = 1
    parent_level = 0
    # For each header level the header ID is added, position 0 is header, pos 1 ##, pos 3 ###, etc...
    parent_tree = [0]
    while remaining_content != "":
        name_id, level, title, content, remaining_content = make_markdown_chunk(
            markdown_text=remaining_content, header_id_spaces=header_id_spaces
        )
        # Ensure parent_level is an int
        parent_level = int(parent_level)
        # Indicates the first encountered header since parent_level and parent_tree have base values
        if parent_level == 0 and parent_tree == [0] and "title" not in data:
            page_title = title
        # Builds the parent tree based on current section level and the previous_id
        parent_tree = build_parent_tree(parent_tree, level, previous_id)
        plain_text_content = markdown_to_text(content)
        token_count = tokenCount.returnHighestTokens(plain_text_content)
        # This goes up as sections start at 1
        section_id += 1
        # Initializes a Section, content may be replaced if too large
        # Copy ensures parent_tree doesn't get overwritten
        section = Section(
            section_id,
            name_id,
            page_title,
            title,
            level,
            previous_id,
            parent_tree.copy(),
            token_count,
            plain_text_content,
        )
        # If content is larger than 5KB - split by lines
        if len(plain_text_content.encode("utf-8")) > 5000:
            # Return an array of sections that were split and the remain content
            logging.info("Chunk is too big - splitting by lines")
            new_sections = split_sections_by_lines(section=section)
            # Merge the list of sections and bump up the section_id.
            # Length has to be reduced by 1 since original chunk was already
            # counted
            section_id = section_id + (len(new_sections)-1)
            page_sections += new_sections
        # Create a Section object for sections under 6k of the doc.
        else:
            # If less than 5kb - append to a list of section objects
            page_sections.append(section)
        # Prepare previous_id for next section
        previous_id = int(section_id)
        parent_level = int(level)
    sect_count = len(page_sections)
    page = Page(page_title, page_url, sect_count, page_metadata)
    # Return an array of Section objects with a single Page object
    return page_sections, page


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
        metadata["URL"] = add_scheme_url(url=data["URL"], scheme="https")
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
                    + '" page includes the following information:\n\n'
                )

            if section_title:
                new_line = (
                    '# The "'
                    + page_title
                    + '" page has the "'
                    + section_title
                    + '" section that includes the following information:\n'
                )

            if subsection_title:
                new_line = (
                    '# On the "'
                    + page_title
                    + '" page, the "'
                    + section_title
                    + '" section has the "'
                    + subsection_title
                    + '" subsection that includes the following information:\n'
                )

        if skip_this_line is False:
            if new_line:
                updated_markdown += new_line + "\n"
            else:
                updated_markdown += line + "\n"
    return updated_markdown, metadata


# This function divides Markdown content into sections and
# returns an array containing these sections.
# But this function requires pre-processed Markdown headings from
# the `process_page_and_section_titles()` function, which simplifies
# three levels of Markdown headings (#, ##, and ###) into just a single #.
def process_document_into_sections(markdown_text):
    sections = []
    buffer = []
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
                    contents = construct_chunks(buffer)
                    for content in contents:
                        sections.append(content)
                    buffer.clear()
        buffer.append(line)
    # Add the last section on the page.
    contents = construct_chunks(buffer)
    for content in contents:
        sections.append(content)
    return sections


# Process an array of Markdwon text into an array of string buffers
# whose size is smaller than 5KB.
def construct_chunks(lines):
    contents = []
    buffer_size = get_byte_size(lines)
    if int(buffer_size) > 5000:
        # If the protocol is larger than 5KB, divide it into two.
        logging.info(
            "Found a text chunk greater than 5KB (size: " + str(buffer_size) + ")."
        )
        (first_half, second_half) = divide_an_array(lines)
        first_content = construct_chunks(first_half)
        second_content = construct_chunks(second_half)
        contents += first_content
        contents += second_content
    else:
        chunk = convert_array_to_buffer(lines)
        contents.append(chunk)
    return contents


# Convert an array into a string buffer.
def convert_array_to_buffer(lines):
    content = ""
    for line in lines:
        content += line + "\n"
    return content


# Get the byte size of lines.
def get_byte_size(lines):
    buffer_size = 0
    for line in lines:
        buffer_size += len(line.encode("utf-8"))
    return buffer_size


# Divide a large array into two arrays.
def divide_an_array(lines):
    half_point = len(lines) // 2
    first_half = lines[:half_point]
    second_half = lines[half_point:]
    return first_half, second_half
