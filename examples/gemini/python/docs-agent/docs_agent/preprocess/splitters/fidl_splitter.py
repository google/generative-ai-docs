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

import re
import os
from absl import logging


# Get the byte size of lines.
def get_byte_size(lines):
    buffer_size = 0
    for line in lines:
        buffer_size += len(line.encode("utf-8"))
    return buffer_size


# Prepare a FIDL protocol into a text chunk to be stored.
def construct_a_chunk(library_name: str, protocol_name: str, lines):
    content_to_store = ""
    content_to_store += "Library name: " + library_name + "\n"
    content_to_store += "Protocol name: " + protocol_name + "\n\n"
    content_to_store += (
        "In Fuchsia's "
        + library_name
        + " FIDL library, the "
        + protocol_name
        + " protocol interface is defined as the following:\n\n"
    )
    content_to_store += "<code>\n"
    for line in lines:
        content_to_store += line + "\n"
    content_to_store += "</code>\n"
    return content_to_store


# Divide a large protocol into two text chunks.
def divide_a_protocol(lines):
    half_point = len(lines) // 2
    first_half = lines[:half_point]
    second_half = lines[half_point:]
    return first_half, second_half


# Recursively process a FIDL protocol into text chunks.
def construct_chunks(library_name: str, protocol_name: str, lines):
    contents = []
    buffer_size = get_byte_size(lines)
    if int(buffer_size) > 5000:
        # If the protocol is larget than 5KB, divide it into two.
        logging.info(
            "Found a text chunk ("
            + str(protocol_name)
            + ") is greater than 6KB (size: "
            + str(buffer_size)
            + ")."
        )
        (first_half, second_half) = divide_a_protocol(lines)
        first_content = construct_chunks(library_name, protocol_name, first_half)
        second_content = construct_chunks(library_name, protocol_name, second_half)
        contents += first_content
        contents += second_content
    else:
        # Prepare a text chunk that describes a FIDL protocol.
        content = construct_a_chunk(library_name, protocol_name, lines)
        logging.info(
            "Created a text chunk for "
            + str(protocol_name)
            + " (size: "
            + str(buffer_size)
            + ")."
        )
        contents.append(content)
    return contents


# Split a FIDL file into protocols as text chunks.
def split_file_to_protocols(this_file):
    protocols = []
    line_buffer = []
    protocol_name = ""
    library_name = ""
    index = 0
    for line in this_file.split("\n"):
        match_protocol = re.search(r"^closed\s+protocol\s+(.*)\s+\{", line)
        match_library = re.search(r"^library\s+(.*);", line)
        match_comment = re.search(r"^\s*\/\/\/\s+(.*)", line)
        match_new_line = re.search(r"^\s*$", line)
        match_end_bracket = re.search(r"^};", line)
        if match_protocol:
            # print("MATCHED [Protocol]: " + match_protocol.group(1))
            protocol_name = match_protocol.group(1)
            line_buffer.append(line)
        elif match_library:
            # print("MATCHED [Library]: " + match_library.group(1))
            library_name = match_library.group(1)
        elif match_comment:
            # print("MATCHED [Comment]: " + match_comment.group(1))
            line_buffer.append(line)
        elif match_new_line:
            # print("MATCHED [New line]")
            line_buffer.append(line)
        elif match_end_bracket:
            # print("MATCHED [End bracket]")
            line_buffer.append(line)
            if library_name != "" and protocol_name != "":
                # Prepre a captured FIDL protocl into small text chunks.
                contents = construct_chunks(library_name, protocol_name, line_buffer)
                for content in contents:
                    protocols.append(content)
            # Clear the line butter and protocol name when an end bracket is found.
            line_buffer.clear()
            protocol_name = ""
        else:
            line_buffer.append(line)
        index += 0
    return protocols
