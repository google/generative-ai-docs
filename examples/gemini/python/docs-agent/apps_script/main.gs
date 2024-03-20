/**
 * Copyright 2023 Google LLC
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

// Defines the gmail search query for saving emails to markdown
var SEARCH_QUERY = 'subject: psa to:my-mailing-list@example.com';
// Defines the directory to output the emails in markdown format
var folderOutput = "PSA-output"
// Defines the directory that has your docs content
var folderInput = "input-folder"

function main() {
  convertDriveFolderToMDForDocsAgent(folderInput);
  exportEmailsToMarkdown(SEARCH_QUERY, folderOutput);
}