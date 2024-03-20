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

import re, os
from docs_agent.preprocess.splitters import markdown_splitter


# This function replaces HTML's includes sections with content.
def process_html_includes(html_text, root):
    updated_html = ""
    for line in html_text.split("\n"):
        # Replaces HTML includes (Jinja) with content (html include can happen
        # with indents)
        try:
            include_match = re.search('{% include "(.*?)" %}', line)
            include_file = os.path.abspath(root + "/" + include_match[1])
            # Tries to open include and errors if it doesn't exist
            try:
                html_include = markdown_splitter.verify_file(include_file)
                if html_include is str:
                    updated_html += html_include + "\n"
                else:
                    updated_html += "\n"
            except FileNotFoundError:
                # If the file doesn't exist, remove the include statement to
                # avoid polluting content
                updated_html += "\n"
        except:
            updated_html += line + "\n"
    return updated_html
