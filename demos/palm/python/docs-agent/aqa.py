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

"""AQA module for using the Semantic Retrieval API"""

import google.ai.generativelanguage as glm


class AQA:
    def __init__(self):
        # Initialize variables for the Semantic Retrieval API
        self.generative_service_client = glm.GenerativeServiceClient()
        self.retriever_service_client = glm.RetrieverServiceClient()
        self.permission_service_client = glm.PermissionServiceClient()

    def list_existing_corpora(self):
        corpora_list = glm.ListCorporaRequest()
        response = self.retriever_service_client.list_corpora(corpora_list)
        print("List of existing corpora:\n")
        print(response)

    def delete_a_corpus(self, corpus_name):
        try:
            delete = glm.DeleteCorpusRequest(name=corpus_name)
            delete = glm.DeleteCorpusRequest(name=corpus_name, force=True)
            delete_corpus_response = self.retriever_service_client.delete_corpus(delete)
            print("Successfully deleted corpus: " + corpus_name)
        except:
            print("Failed to delete the corpus: " + corpus_name)

    def create_a_new_corpus(self, corpus_display, corpus_name):
        try:
            # Get an existing corpus
            get_corpus_request = glm.GetCorpusRequest(name=corpus_name)
            get_corpus_response = self.retriever_service_client.get_corpus(
                get_corpus_request
            )
            print()
            print(f"{corpus_name} exists.\n{get_corpus_response}")
        except:
            # Create a new corpus
            corpus = glm.Corpus(display_name=corpus_display, name=corpus_name)
            create_corpus_request = glm.CreateCorpusRequest(corpus=corpus)
            create_corpus_response = self.retriever_service_client.create_corpus(
                create_corpus_request
            )
            print()
            print(f"Created a new corpus {corpus_name}.\n{create_corpus_response}")

    def create_a_doc(self, corpus_name, page_title, page_url):
        document_resource_name = ""
        try:
            # Create a new document with a custom display name.
            example_document = glm.Document(display_name=page_title)
            # Add metadata.
            document_metadata = [glm.CustomMetadata(key="url", string_value=page_url)]
            example_document.custom_metadata.extend(document_metadata)
            # Make the request
            create_document_request = glm.CreateDocumentRequest(
                parent=corpus_name, document=example_document
            )
            create_document_response = self.retriever_service_client.create_document(
                create_document_request
            )
            # Set the `document_resource_name` for subsequent sections.
            document_resource_name = create_document_response.name
        except:
            get_document_request = glm.GetDocumentRequest(name=document_resource_name)
            # Make the request
            get_document_response = self.retriever_service_client.get_document(
                get_document_request
            )
            document_resource_name = get_document_response.name
        return document_resource_name

    def create_a_chunk(self, doc_name, text, url):
        response = ""
        try:
            # Create a chunk.
            chunk = glm.Chunk(data={"string_value": text})
            # Add metadata.
            chunk.custom_metadata.append(
                glm.CustomMetadata(key="url", string_value=url)
            )
            create_chunk_requests = []
            create_chunk_requests.append(
                glm.CreateChunkRequest(parent=doc_name, chunk=chunk)
            )
            # Make the request
            request = glm.BatchCreateChunksRequest(
                parent=doc_name, requests=create_chunk_requests
            )
            response = self.retriever_service_client.batch_create_chunks(request)
            # Print the response
            print("Created a new text chunk:\n")
            print(response)
        except:
            print("[ERROR] Failed to create a text chunk for:\n\n" + text)
            # Failed possibly because the size of the text is too large.
            # Quick fix: Split the text into 2 chunks
            lines = text.splitlines()
            text_01 = ""
            text_02 = ""
            text_size = len(lines)
            half_size = int(text_size / 2)
            i = 0
            for line in lines:
                if i < half_size:
                    text_01 += line + "\n"
                else:
                    text_02 += line + "\n"
                i += 1
            self.create_a_chunk(doc_name, text_01, url)
            self.create_a_chunk(doc_name, text_02, url)
        return response

    def create_a_doc_chunk(self, corpus_name, page_title, page_url, text):
        doc_name = self.create_a_doc(corpus_name, page_title, page_url)
        return self.create_a_chunk(doc_name, text, page_url)
