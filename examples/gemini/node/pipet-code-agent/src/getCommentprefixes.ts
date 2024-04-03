
/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

//Code comment: (generated)
//Given a file type, returns the comment prefix appropriate for that file type.
//@param {string} fileType The file type to get the comment prefix for.
//@returns {string} The comment prefix for the given file type.
export function getCommentprefixes(fileType: string): string {
  switch (fileType) {
    case "python":
      return "# ";
    case "javascript":
      return "// ";
    case "html":
      return "<!-- -->";
    case "css":
      return "/* */";
    case "cpp":
    case "c":
    case "h": // C/C++ header
    case "java":
    case "csharp":
      return "// ";
    default:
      return "//"; // No comment prefix for unknown file types
  }
}

// TODO(you!): Support doxygen comment styles.