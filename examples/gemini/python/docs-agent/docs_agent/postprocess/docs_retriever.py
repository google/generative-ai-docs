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
# from markdown import markdown
# from bs4 import BeautifulSoup
# import re, os
from docs_agent.models import tokenCount
from docs_agent.preprocess.splitters.markdown_splitter import Section as Section

"""Objects to handle retrieval of Sections and rebuild original pages"""


# Let's you retrieve sections based on an original match while
# also keeping distance
class SectionDistance:
    """Return Section including origin UUID, distance from result, and url"""

    def __init__(self, section: Section, distance: str):
        self.section = section
        self.distance = distance


# Let's you retrieve sections based on an original match while
# also keeping probability. This is for AQA
class SectionProbability:
    """Return Section including origin UUID, probability of result, and url"""

    def __init__(self, section: Section, probability: float):
        self.section = section
        self.probability = probability


# Let's you build a full page based on list of Sections and in the order provided
# Returns a string of final page and a token_count_estimate of the final page
class FullPage:
    def __init__(self, section_list: list[Section]):
        self.section_list = section_list

    def __str__(self):
        return f"This is a page with the following content:\n"

    def buildPage(self):
        final_page = ""
        total_token_count = 0
        for item in self.section_list:
            # It is possible to check attributes such as token_count of chunks here
            # (i.e)if item.token_count > 800:
            final_page += item.content
            total_token_count += item.token_count
        return final_page, total_token_count

    # Given a page, returns only the section that matches the provided id
    # Also adds a preamble (which can be customized)
    def returnSelfSection(self, section_id):
        # Adds initial section from match
        for item in self.section_list:
            try:
                if section_id == item.id:
                    # Updates the content of a section on the fly with a template
                    item.updateContentTemplate()
                    return item
            except:
                print(f"Could not find a section with the provided ID {section_id}")

    # Returns all of the children for a given section_id. Any section that
    # are under the given header. For example, if the provided section_id is
    # a ##, provide all ### directly under it
    # Specify a token_limit to limit amount of sections returned
    def returnChildrenSections(self, section_id, token_limit: float = float("inf")):
        # Finds the Section given a section_id
        match = False
        updated_list = []
        for item in self.section_list:
            if section_id == item.id:
                given_section = item
                match = True
                break
        # If Section doesn't match, just return a FullPage with a blank list
        if not match:
            print(f"Could not find a section with the provided ID {section_id}")
            return FullPage(section_list=updated_list)
        # Start token count at 0
        curr_token = 0
        # updated_list = []
        for item in self.section_list:
            direct_parent = item.returnDirectParentId()
            if int(direct_parent) == int(given_section.id):
                if (curr_token + item.token_count) < token_limit:
                    curr_token += item.token_count
                    # Updates the content of a section on the fly with a template
                    item.updateContentTemplate()
                    # Estimate token count for preamble and add it to curr_token
                    item.token_count = tokenCount.returnHighestTokens(item.content)
                    curr_token += item.token_count
                    # Append each Section to a new list to return
                    updated_list.append(item)
        updated_page = FullPage(section_list=updated_list)
        # You can view token count by doing sum of all Section.token_count
        return updated_page

    # Returns all of the siblings for a given section_id. Any section that
    # has the same parent_tree
    def returnSiblingSections(self, section_id, token_limit: float = float("inf")):
        # Finds the Section given a section_id
        match = False
        updated_list = []
        for item in self.section_list:
            if section_id == item.id:
                given_section = item
                match = True
                # Break out of loop once a match is found
                break
        # If Section doesn't match, just return a FullPage with a blank list
        if not match:
            print(f"Could not find a section with the provided ID {section_id}")
            return FullPage(section_list=updated_list)
        # Start token count at 0
        curr_token = 0
        # updated_list = []
        given_parent_tree = eval(given_section.parent_tree)
        for item in self.section_list:
            direct_parent = item.returnDirectParentId()
            # Matches parent_tree and skips the same section
            if (
                given_parent_tree == eval(item.parent_tree)
                and given_section.id != item.id
            ):
                if (curr_token + item.token_count) < token_limit:
                    curr_token += item.token_count
                    # Updates the content of a section on the fly with a template
                    item.updateContentTemplate()
                    # Estimate token count for preamble and add it to curr_token
                    item.token_count = tokenCount.returnHighestTokens(item.content)
                    curr_token += item.token_count
                    # Append each Section to a new list to return
                    updated_list.append(item)
        updated_page = FullPage(section_list=updated_list)
        # You can view token count by doing sum of all Section.token_count
        return updated_page

    # Returns the parent of a given section.
    # If updated_page contains no parents, return []
    def returnParentSection(self, section_id, token_limit: float = float("inf")):
        # Finds the Section given a section_id
        match = False
        updated_list = []
        for item in self.section_list:
            if section_id == item.id:
                given_section = item
                match = True
                # Break out of loop once a match is found
                given_parent = given_section.returnDirectParentId()
                break
        # If Section doesn't match, just return a FullPage with a blank list
        if not match:
            print(f"Could not find a section with the provided ID {section_id}")
            # return FullPage(section_list=updated_list)
            return None
        # Start token count at 0
        curr_token = 0
        # updated_list = []
        for item in self.section_list:
            direct_parent = item.returnDirectParentId()
            if int(given_parent) == int(item.id) and given_parent != 0:
                if (curr_token + item.token_count) < token_limit:
                    curr_token += item.token_count
                    # Updates the content of a section on the fly with a template
                    item.updateContentTemplate()
                    # Estimate token count for preamble and add it to curr_token
                    item.token_count = tokenCount.returnHighestTokens(item.content)
                    curr_token += item.token_count
                    # A section only can only have a single item
                    return item

    # Sorts Section by a clause, defaults to id (only supported at the moment)
    # Include a reverse flag to also do a reverse order
    def sortSections(self, reverse: bool = False):
        updated_list = []
        # In some cases an item may be None, so remove these
        for item in self.section_list:
            if item is not None:
                updated_list.append(item)
        updated_list.sort(key=lambda x: x.id, reverse=reverse)
        updated_page = FullPage(section_list=updated_list)
        return updated_page

    # Builds a page using the additional flags
    def buildSections(
        self,
        section_id,
        selfSection: bool = True,
        children: bool = False,
        parent: bool = False,
        siblings: bool = False,
        token_limit: float = float("inf"),
        reverse: bool = False,
    ):
        final_sections = []
        section_token_count = 0
        if selfSection:
            self_section = self.returnSelfSection(section_id=section_id)
            if self_section is not None:
                final_sections.append(self_section)
                section_token_count += self_section.token_count
        if children:
            children_sections = self.returnChildrenSections(
                section_id=section_id, token_limit=(token_limit - section_token_count)
            )
            final_sections = final_sections + children_sections.section_list
            # Adds the tokens for the sections
            for item in children_sections.section_list:
                if item is not None:
                    section_token_count += item.token_count
        if parent:
            parent_section = self.returnParentSection(
                section_id=section_id, token_limit=(token_limit - section_token_count)
            )
            final_sections.append(parent_section)
            if parent_section is not None:
                section_token_count += parent_section.token_count
        if siblings:
            sibling_sections = self.returnSiblingSections(
                section_id=section_id, token_limit=(token_limit - section_token_count)
            )
            final_sections = final_sections + sibling_sections.section_list
            for item in sibling_sections.section_list:
                if item is not None:
                    section_token_count += item.token_count
        final_page = FullPage(final_sections).sortSections(reverse=reverse)
        return final_page