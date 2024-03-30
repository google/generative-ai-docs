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

def split_file_to_protocols(this_file):
    protocols = []
    line_buffer = ""
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
            #print("MATCHED [Protocol]: " + match_protocol.group(1))
            protocol_name = match_protocol.group(1)
            line_buffer += line + "\n"
        elif match_library:
            #print("MATCHED [Library]: " + match_library.group(1))
            library_name = match_library.group(1)
        elif match_comment:
            #print("MATCHED [Comment]: " + match_comment.group(1))
            line_buffer += line + "\n"
        elif match_new_line:
            #print("MATCHED [New line]")
            line_buffer += line + "\n"
        elif match_end_bracket:
            #print("MATCHED [End bracket]")
            line_buffer += line + "\n"
            content_to_store = "Library name: " + library_name + "\n"
            content_to_store += "Protocol name: " + protocol_name + "\n\n"
            content_to_store += "In Fuchsia's " + library_name + " FIDL library, the " + protocol_name + " protocol interface is defined as the following:\n\n"
            content_to_store += "<code>\n"
            content_to_store += line_buffer.strip() + "\n"
            content_to_store += "</code>\n"
            if library_name != "" and protocol_name != "":
                protocols.append(content_to_store)
            # Clear the line butter when an end bracket is found.
            line_buffer = ""
            # Clear the protocol name when an end bracket is found.
            protocol_name = ""
        else:
            line_buffer += line + "\n"
        index += 0
    return protocols

