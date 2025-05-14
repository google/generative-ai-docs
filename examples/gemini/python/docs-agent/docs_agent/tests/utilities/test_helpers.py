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

import unittest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import bs4
import urllib
from flask import Flask, url_for
from docs_agent.utilities import helpers


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SERVER_NAME"] = "testserver"

        # This is where we define the route so the url_for function will work
        @self.app.route('/question', methods=['GET'])
        def question():
            return "test question"

        self.app.add_url_rule('/chatui/question', endpoint='chatui.question')

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_expand_path_with_tilde(self):
        """Tests that a path starting with '~/' is expanded correctly."""
        # Patch controls the output of os.path.expanduser
        expected_home_dir = "/usr/local/home/testuser"
        with patch("os.path.expanduser", return_value=os.path.join(expected_home_dir, "Documents")):
            input_path = "~/Documents"
            expected_path = os.path.join(expected_home_dir, "Documents")
            self.assertEqual(helpers.expand_user_path(input_path), expected_path)

    def test_expand_path_without_tilde(self):
        """Tests that a path not starting with '~/' is returned unchanged."""
        input_path = "/absolute/path/to/file"
        self.assertEqual(helpers.expand_user_path(input_path), input_path)

    def test_expand_path_with_tilde_but_not_at_start(self):
        """Tests that a path containing '~' but not at the start is returned unchanged."""
        input_path = "/some/path/~/something"
        self.assertEqual(helpers.expand_user_path(input_path), input_path)

    def test_expand_path_with_empty_string_input(self):
        """Tests that an empty string is returned unchanged."""
        input_path = ""
        self.assertEqual(helpers.expand_user_path(input_path), input_path)

    def test_expand_path_none_input(self):
        """Tests that None input returns None."""
        input_path = None
        self.assertIsNone(helpers.expand_user_path(input_path))

    def test_expand_path_just_tilde_slash(self):
        """Tests that just '~/' expands to the home directory."""
        expected_home_dir = "/usr/local/home/testuser"
        with patch("os.path.expanduser", return_value=expected_home_dir):
            input_path = "~/"
            self.assertEqual(helpers.expand_user_path(input_path), expected_home_dir)

    def test_get_project_path(self):
        # Assumes this test file is in the project root's tests directory
        project_path = helpers.get_project_path()
        # Verify that the path is a directory
        self.assertTrue(os.path.isdir(project_path))
        # Verify that the project path is within one subdirectory above this test file
        self.assertEqual(Path(__file__).parent.parent.parent.parent, project_path)

    def test_resolve_path_absolute(self):
        # Test an absolute path
        abs_path = "/absolute/path"
        self.assertEqual(helpers.resolve_path(abs_path), abs_path)

    def test_resolve_path_relative(self):
        # Test a relative path
        rel_path = "relative/path"
        expected_path = os.path.join(helpers.get_project_path(), rel_path)
        self.assertEqual(helpers.resolve_path(rel_path), expected_path)

    def test_resolve_path_with_base_dir(self):
         # Test a relative path with a specified base directory
        base_dir = Path("/base")
        rel_path = "sub/path"
        expected_path = os.path.join(base_dir, rel_path)
        self.assertEqual(helpers.resolve_path(rel_path, base_dir), expected_path)

    def test_end_path_backslash(self):
        # Test adding a backslash to a path
        self.assertEqual(helpers.end_path_backslash("path"), "path/")
        self.assertEqual(helpers.end_path_backslash("path/"), "path/")

    def test_start_path_no_backslash(self):
        # Test removing a leading backslash
        self.assertEqual(helpers.start_path_no_backslash("/path"), "path")
        self.assertEqual(helpers.start_path_no_backslash("path"), "path")

    def test_parallel_backup_dir(self):
       # Test creating a parallel backup directory
        test_path = "/path/to/file.txt"
        backup_dir = helpers.parallel_backup_dir(test_path, "backup")
        expected_path = "/path/to/backup/file.txt"
        self.assertEqual(backup_dir, expected_path)

    def test_parallel_backup_dir_relative(self):
         # Test creating a parallel backup directory with a relative path
        test_path = "path/to/file.txt"
        backup_dir = helpers.parallel_backup_dir(test_path, "backup")
        expected_path = os.path.join(helpers.get_project_path(), 'path', 'to', 'backup', 'file.txt')
        self.assertEqual(backup_dir, expected_path)

    def test_parallel_backup_dir_custom_backup_name(self):
         # Test creating a parallel backup directory with a custom backup name
        test_path = "/path/to/file.txt"
        backup_dir = helpers.parallel_backup_dir(test_path, "custom")
        expected_path = "/path/to/custom/file.txt"
        self.assertEqual(backup_dir, expected_path)

    def test_return_pure_dir(self):
        # Test returning the parent directory name
        self.assertEqual(helpers.return_pure_dir("/path/to/file.txt"), "file.txt")
        self.assertEqual(helpers.return_pure_dir("path/to/file.txt"), "file.txt")

    def test_add_scheme_url(self):
        # Test adding a URL scheme
        self.assertEqual(helpers.add_scheme_url("google.com"), "https://google.com")
        self.assertEqual(helpers.add_scheme_url("http://google.com"), "http://google.com")
        self.assertEqual(helpers.add_scheme_url("https://google.com"), "https://google.com")
        self.assertEqual(helpers.add_scheme_url("google.com", "http"), "http://google.com")

    def test_parse_related_questions_response_to_html_list(self):
        # Test parsing related questions response and converting to HTML
        response = """
        <ul>
            <li>This is a <p>paragraph.</p></li>
            <li>This is a <code>code</code> example.</li>
            <li>This is a simple item.</li>
        </ul>
        """
        parsed_html = helpers.parse_related_questions_response_to_html_list(response)
        # Verify there are no p or code tags
        self.assertIsNone(parsed_html.find("p"))
        self.assertIsNone(parsed_html.find("code"))

        # Test there are now <a> tags instead of raw string
        a_tags = parsed_html.find_all("a")
        self.assertEqual(len(a_tags), 3)

        self.assertEqual(
            a_tags[0].get("href"),
            url_for("chatui.question", ask=urllib.parse.quote_plus("This is a paragraph."), _external=True),
        )
        self.assertEqual(
            a_tags[1].get("href"),
            url_for("chatui.question", ask=urllib.parse.quote_plus("This is a code example."), _external=True),
        )
        self.assertEqual(
            a_tags[2].get("href"),
            url_for("chatui.question", ask=urllib.parse.quote_plus("This is a simple item."), _external=True),
        )

        self.assertEqual(a_tags[0].string, "This is a paragraph.")
        self.assertEqual(a_tags[1].string, "This is a code example.")
        self.assertEqual(a_tags[2].string, "This is a simple item.")

    def test_build_list_html_links_no_content(self):
        # Test building a list of HTML links
        urls = ["https://example.com/section1", "https://example.com/section2"]
        section_titles = ["Section 1", "Section 2"]
        page_titles = ["Page 1", "Page 2"]
        distances = [0.1, 0.2]

        html_list = helpers.build_list_html_links(
            urls, section_titles, page_titles, distances
        )
        self.assertIn("<li>", html_list)
        self.assertIn("Section 1", html_list)
        self.assertIn("Section 2", html_list)
        self.assertIn("Page 1", html_list)
        self.assertIn("Page 2", html_list)
        self.assertIn("Distance: 0.1", html_list)
        self.assertIn("Distance: 0.2", html_list)

    def test_build_list_html_links_with_content(self):
        urls = ["https://example.com/section1", "https://example.com/section2"]
        section_titles = ["Section 1", "Section 2"]
        page_titles = ["Page 1", "Page 2"]
        distances = [0.1, 0.2]
        section_content = ["Content 1", "Content 2"]

        html_list = helpers.build_list_html_links(
            urls, section_titles, page_titles, distances, section_content=section_content
        )

        self.assertIn("<li>", html_list)
        self.assertIn("Section 1", html_list)
        self.assertIn("Section 2", html_list)
        self.assertIn("Page 1", html_list)
        self.assertIn("Page 2", html_list)
        self.assertIn("Content 1", html_list)
        self.assertIn("Content 2", html_list)
        self.assertIn("Distance: 0.1", html_list)
        self.assertIn("Distance: 0.2", html_list)

    def test_build_list_html_links_max_count(self):
        urls = ["https://example.com/section1", "https://example.com/section2", "https://example.com/section3"]
        section_titles = ["Section 1", "Section 2", "Section 3"]
        page_titles = ["Page 1", "Page 2", "Page 3"]
        distances = [0.1, 0.2, 0.3]

        html_list = helpers.build_list_html_links(
            urls, section_titles, page_titles, distances, max_count=2
        )
        self.assertIn("<li>", html_list)
        self.assertIn("Section 1", html_list)
        self.assertIn("Section 2", html_list)
        self.assertNotIn("Section 3", html_list)
        self.assertIn("Page 1", html_list)
        self.assertIn("Page 2", html_list)
        self.assertNotIn("Page 3", html_list)
        self.assertIn("Distance: 0.1", html_list)
        self.assertIn("Distance: 0.2", html_list)
        self.assertNotIn("Distance: 0.3", html_list)

    def test_named_link_html(self):
        # Test building an HTML link
        html_link = helpers.named_link_html("google.com", "Google")
        self.assertEqual(html_link, '<a href="https://google.com" target="_blank">Google</a>')

        # Test with a class attribute.  Sort the attributes for comparison.
        html_link = helpers.named_link_html("google.com", "Google", class_="test")
        self.assertEqual(self._sort_html_attributes(html_link), self._sort_html_attributes('<a class="test" href="https://google.com" target="_blank">Google</a>'))

        #Test with no label
        html_link = helpers.named_link_html("google.com")
        self.assertEqual(html_link, '<a href="https://google.com" target="_blank"></a>')

        #Test with other kwargs
        html_link = helpers.named_link_html("google.com", "Google", id="test-id", style="color: blue;")
        self.assertEqual(self._sort_html_attributes(html_link), self._sort_html_attributes('<a href="https://google.com" target="_blank" id="test-id" style="color: blue;">Google</a>'))

        # Test with http:// URL
        html_link = helpers.named_link_html("http://google.com", "Google")
        self.assertEqual(html_link, '<a href="http://google.com" target="_blank">Google</a>')

        # Test with quotes in attribute values (the KEY TEST CASE)
        html_link = helpers.named_link_html("example.com", "Example", title='This is a "test" with quotes.')
        self.assertEqual(html_link, '<a href="https://example.com" target="_blank" title="This is a &quot;test&quot; with quotes.">Example</a>')

        # Test another edge case with special characters
        html_link = helpers.named_link_html("example.com", "Example & More", title="Special <chars> & stuff.")
        self.assertEqual(html_link, '<a href="https://example.com" target="_blank" title="Special &lt;chars&gt; &amp; stuff.">Example & More</a>')


    def test_named_link_html_no_label(self):
        # Test building an HTML link with no label
        html_link = helpers.named_link_html("google.com")
        soup1 = bs4.BeautifulSoup(html_link, features="html.parser")
        soup2 = bs4.BeautifulSoup('<a href="https://google.com" target="_blank"></a>', features="html.parser")
        self.assertEqual(soup1.prettify(), soup2.prettify())

    def test_named_link_md(self):
        # Test building a Markdown link
        md_link = helpers.named_link_md("google.com", "Google")
        self.assertEqual(md_link, "[Google](https://google.com)")

    def test_trim_section_for_page_link(self):
        # Test trimming the section from a URL
        self.assertEqual(
            helpers.trim_section_for_page_link("https://example.com/page#section"),
            "https://example.com/page",
        )
        self.assertEqual(
            helpers.trim_section_for_page_link("https://example.com/page"),
            "https://example.com/page",
        )

    def test_md_to_html(self):
       # Test converting markdown to html
        md = "# Header\n\nThis is a paragraph."
        html = helpers.md_to_html(md)
        self.assertTrue("<h1>Header</h1>" in html)
        self.assertTrue("<p>This is a paragraph.</p>" in html)

    def _sort_html_attributes(self, html_string):
        """Helper function to sort HTML attributes within a tag."""
        soup = bs4.BeautifulSoup(html_string, 'html.parser')
        tag = soup.find('a')  # Find the <a> tag
        if tag:
            attrs = dict(sorted(tag.attrs.items()))  # Sort attributes
            tag.attrs = attrs  # Replace with sorted attributes
        return str(soup)


# Helper function to create a dummy file for testing existence checks
def create_test_file(filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.touch()


# Helper function to remove a dummy file
def remove_test_file(filepath: Path):
    if filepath.exists():
        filepath.unlink()
    # Clean up parent directory
    try:
        filepath.parent.rmdir()
    except OSError:
        pass


class TestResolveAndEnsurePath(unittest.TestCase):
    """Tests for the resolve_and_ensure_path function."""
    def setUp(self):
        """Setup for test cases."""
        # Create a temporary directory for testing
        self.test_dir = Path("./temp_test_dir_resolve_ensure")
        self.test_dir.mkdir(exist_ok=True)
        self.existing_file = self.test_dir / "existing_file.txt"
        create_test_file(self.existing_file)
        self.existing_abs_path = str(self.existing_file.resolve())
        self.non_existing_file = self.test_dir / "non_existing_file.txt"
        self.non_existing_abs_path = str(self.non_existing_file.resolve())

        # Mock get_project_path to return our test directory
        self.project_path_patcher = patch("docs_agent.utilities.helpers.get_project_path", return_value=self.test_dir.resolve())
        self.mock_get_project_path = self.project_path_patcher.start()

        # Mock logging
        self.log_patcher = patch("docs_agent.utilities.helpers.logging")
        self.mock_logging = self.log_patcher.start()

        # Mock Path
        self.path_patcher = patch("docs_agent.utilities.helpers.Path")
        self.mock_path_class = self.path_patcher.start()

    def tearDown(self):
        """Teardown for test cases."""
        # Clean up temporary files and directory
        remove_test_file(self.existing_file)
        if self.test_dir.exists():
            for item in self.test_dir.iterdir():
                 if item.is_file():
                     item.unlink()
            self.test_dir.rmdir()
        self.project_path_patcher.stop()
        self.log_patcher.stop()
        self.path_patcher.stop()

    def test_resolve_and_ensure_path_none_input(self):
        """Test resolve_and_ensure_path with None input."""
        self.assertIsNone(helpers.resolve_and_ensure_path(None))
        self.mock_logging.error.assert_not_called()

    def test_resolve_and_ensure_path_empty_string_input(self):
        """Test resolve_and_ensure_path with an empty string input."""
        self.assertIsNone(helpers.resolve_and_ensure_path(""))
        self.mock_logging.error.assert_not_called()

    @patch("docs_agent.utilities.helpers.expand_user_path")
    @patch("docs_agent.utilities.helpers.resolve_path")
    def test_resolve_and_ensure_path_existing_file_check_exists_true(self, mock_resolve_path, mock_expand_user):
        """Test with an existing file and check_exists=True."""
        input_path = "some/path/existing_file.txt"
        mock_expand_user.return_value = input_path
        mock_resolve_path.return_value = self.existing_abs_path

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.__str__.return_value = self.existing_abs_path
        self.mock_path_class.return_value = mock_path_instance

        result = helpers.resolve_and_ensure_path(input_path, check_exists=True)

        self.assertEqual(result, self.existing_abs_path)
        mock_expand_user.assert_called_once_with(input_path)
        mock_resolve_path.assert_called_once_with(input_path)
        self.mock_path_class.assert_called_once_with(self.existing_abs_path)
        mock_path_instance.exists.assert_called_once()
        self.mock_logging.error.assert_not_called()

    @patch("docs_agent.utilities.helpers.expand_user_path")
    @patch("docs_agent.utilities.helpers.resolve_path")
    def test_resolve_and_ensure_path_non_existing_file_check_exists_true(self, mock_resolve_path, mock_expand_user):
        """Test with a non-existing file and check_exists=True."""
        input_path = "some/path/non_existing_file.txt"
        mock_expand_user.return_value = input_path
        mock_resolve_path.return_value = self.non_existing_abs_path

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.__str__.return_value = self.non_existing_abs_path
        self.mock_path_class.return_value = mock_path_instance

        result = helpers.resolve_and_ensure_path(input_path, check_exists=True)

        self.assertIsNone(result)
        mock_expand_user.assert_called_once_with(input_path)
        mock_resolve_path.assert_called_once_with(input_path)
        self.mock_path_class.assert_called_once_with(self.non_existing_abs_path)
        mock_path_instance.exists.assert_called_once()
        self.mock_logging.error.assert_called_once_with(
            f"[Error] Cannot access the input path: {self.non_existing_abs_path}"
        )

    @patch("docs_agent.utilities.helpers.expand_user_path")
    @patch("docs_agent.utilities.helpers.resolve_path")
    def test_resolve_and_ensure_path_non_existing_file_check_exists_false(self, mock_resolve_path, mock_expand_user):
        """Test with a non-existing file and check_exists=False."""
        input_path = "some/path/non_existing_file.txt"
        mock_expand_user.return_value = input_path
        mock_resolve_path.return_value = self.non_existing_abs_path

        mock_path_instance = MagicMock()
        mock_path_instance.__str__.return_value = self.non_existing_abs_path
        self.mock_path_class.return_value = mock_path_instance

        result = helpers.resolve_and_ensure_path(input_path, check_exists=False)

        self.assertEqual(result, self.non_existing_abs_path)
        mock_expand_user.assert_called_once_with(input_path)
        mock_resolve_path.assert_called_once_with(input_path)
        self.mock_path_class.assert_called_once_with(self.non_existing_abs_path)
        mock_path_instance.exists.assert_not_called()
        self.mock_logging.error.assert_not_called()

    @patch("docs_agent.utilities.helpers.expand_user_path", return_value="expanded/path")
    @patch("docs_agent.utilities.helpers.resolve_path", side_effect=FileNotFoundError("Mock file not found"))
    def test_resolve_and_ensure_path_resolve_path_file_not_found(self, mock_resolve_path, mock_expand_user):
        """Test when resolve_path raises FileNotFoundError."""
        input_path = "some/invalid/path"
        result = helpers.resolve_and_ensure_path(input_path)

        self.assertIsNone(result)
        mock_expand_user.assert_called_once_with(input_path)
        mock_resolve_path.assert_called_once_with("expanded/path")
        self.mock_path_class.assert_not_called()
        self.mock_logging.error.assert_called_once_with(
            "[Error] Failed to resolve path: Mock file not found"
        )

    @patch("docs_agent.utilities.helpers.expand_user_path", return_value="expanded/path")
    @patch("docs_agent.utilities.helpers.resolve_path", side_effect=PermissionError("Mock permission error"))
    def test_resolve_and_ensure_path_resolve_path_generic_exception(self, mock_resolve_path, mock_expand_user):
        """Test when resolve_path raises a generic Exception."""
        input_path = "some/problematic/path"
        result = helpers.resolve_and_ensure_path(input_path)

        self.assertIsNone(result)
        mock_expand_user.assert_called_once_with(input_path)
        mock_resolve_path.assert_called_once_with("expanded/path")
        self.mock_path_class.assert_not_called()
        # Use single quotes around input_path to match the actual log message
        self.mock_logging.error.assert_called_once_with(
             f"[Error] An unexpected error occurred resolving path '{input_path}': Mock permission error"
        )

    @patch("docs_agent.utilities.helpers.expand_user_path")
    @patch("docs_agent.utilities.helpers.resolve_path")
    def test_resolve_and_ensure_path_path_exists_exception(self, mock_resolve_path, mock_expand_user):
        """Test when Path(...).exists() raises an exception."""
        input_path = "some/weird/path"
        resolved_path_str = "/resolved/weird/path"
        mock_expand_user.return_value = input_path
        mock_resolve_path.return_value = resolved_path_str

        mock_path_instance = MagicMock()
        mock_path_instance.exists.side_effect = OSError("Mock OS error checking existence")
        mock_path_instance.__str__.return_value = resolved_path_str
        self.mock_path_class.return_value = mock_path_instance

        result = helpers.resolve_and_ensure_path(input_path, check_exists=True)

        self.assertIsNone(result)
        mock_expand_user.assert_called_once_with(input_path)
        mock_resolve_path.assert_called_once_with(input_path)
        self.mock_path_class.assert_called_once_with(resolved_path_str)
        mock_path_instance.exists.assert_called_once()
        # Use single quotes around input_path to match the actual log message
        self.mock_logging.error.assert_called_once_with(
             f"[Error] An unexpected error occurred resolving path '{input_path}': Mock OS error checking existence"
        )

if __name__ == "__main__":
    unittest.main()