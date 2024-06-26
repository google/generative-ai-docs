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

"""Semantic Retrievel module for using the Semantic Retrieval API with AQA"""

import google.ai.generativelanguage as glm
from absl import logging
import typing


class SemanticRetriever:
    def __init__(self):
        # Initialize variables for the Semantic Retrieval API
        self.generative_service_client = glm.GenerativeServiceClient()
        self.retriever_service_client = glm.RetrieverServiceClient()
        self.permission_service_client = glm.PermissionServiceClient()

    def get_corpus(self, corpus_name: str):
        get_corpus_request = glm.GetCorpusRequest(name=corpus_name)
        response = self.retriever_service_client.get_corpus(get_corpus_request)
        return response

    # def get_document(self, document_name: str, metadata):
    #     get_document_request = glm.GetDocumentRequest(name=corpus_name)
    #     try:
    #         response = self.retriever_service_client.get_document(get_document_request)
    #         return response
    #     except:
    #         logging.error(
    #             f"Document {document_name} does not exist or you do not have permissions"
    #         )

    # def get_chunk(self, chunk_name: str, metadata):
    #     get_chunk_request = glm.GetChunkRequest(name=corpus_name)
    #     try:
    #         response = self.retriever_service_client.get_chunk(get_chunk_request)
    #         return response
    #     except:
    #         logging.error(
    #             f"Chunk {chunk_name} does not exist or you do not have permissions"
    #         )

    def list_existing_corpora(self, page_token: str = ""):
        corpora_list = glm.ListCorporaRequest(page_size=20, page_token=page_token)
        response = self.retriever_service_client.list_corpora(corpora_list)
        return response

    def delete_a_corpus(self, corpus_name: str, force: bool = True):
        try:
            delete = glm.DeleteCorpusRequest(name=corpus_name, force=force)
            delete_corpus_response = self.retriever_service_client.delete_corpus(delete)
            logging.info(f"Successfully deleted corpus: {corpus_name}")
        except:
            logging.info(f"Failed to delete the corpus: {corpus_name}")

    def create_a_new_corpus(self, corpus_display: str, corpus_name: str):
        try:
            corpus = glm.Corpus(display_name=corpus_display, name=corpus_name)
            create_corpus_request = glm.CreateCorpusRequest(corpus=corpus)
            corpus_response = self.retriever_service_client.create_corpus(
                create_corpus_request
            )
            logging.info(f"Created a new corpus {corpus_name}.\n{corpus_response}")
        except:
            logging.error(f"Failed to create a new corpus: {corpus_name}")

    def does_this_corpus_exist(self, corpus_name: str):
        try:
            corpus_request = glm.GetCorpusRequest(name=corpus_name)
            corpus_response = self.retriever_service_client.get_corpus(corpus_request)
            logging.info(f"{corpus_name} exists.\n{corpus_response}")
            return True
        except:
            return False

    def create_a_doc(
        self,
        corpus_name: str,
        page_title: str,
        page_url: typing.Optional[str] = None,
        uuid: typing.Optional[str] = None,
        metadata: typing.Optional[dict] = None,
    ):
        document_resource_name = ""
        try:
            # Create a new document with a custom display name.
            example_document = glm.Document(display_name=page_title)
            # Add metadata.
            document_metadata = []
            if metadata is not None:
                for key_dict, value_dict in metadata.items():
                    if isinstance(value_dict, int) or isinstance(value_dict, float):
                        document_metadata.append(
                            glm.CustomMetadata(key=key_dict, numeric_value=value_dict)
                        )
                    elif isinstance(value_dict, str):
                        document_metadata.append(
                            glm.CustomMetadata(key=key_dict, string_value=value_dict)
                        )
                    else:
                        document_metadata.append(
                            glm.CustomMetadata(
                                key=key_dict, string_value=str(value_dict)
                            )
                        )
                example_document.custom_metadata.extend(document_metadata)
            else:
                if uuid is not None and uuid != "":
                    document_metadata = [
                        glm.CustomMetadata(key="uuid", string_value=str(uuid))
                    ]
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
            logging.error(f"Cannot create a new doucment: {page_title}")
            exit(1)
        return document_resource_name

    def retrieve_a_doc(self, document_resource_name: str):
        response = []
        try:
            get_document_request = glm.GetDocumentRequest(name=document_resource_name)
            # Make the request
            response = self.retriever_service_client.get_document(get_document_request)
        except:
            logging.error(f"Cannot retrieve a doucment: {document_resource_name}")
        return response

    def create_a_chunk(
        self, doc_name, text, metadata, page_url: typing.Optional[str] = None
    ):
        response = ""
        document_metadata = []
        if metadata is not None:
            for key_dict, value_dict in metadata.items():
                if isinstance(value_dict, int) or isinstance(value_dict, float):
                    document_metadata.append(
                        glm.CustomMetadata(key=key_dict, numeric_value=value_dict)
                    )
                elif isinstance(value_dict, str):
                    document_metadata.append(
                        glm.CustomMetadata(key=key_dict, string_value=value_dict)
                    )
                else:
                    document_metadata.append(
                        glm.CustomMetadata(key=key_dict, string_value=str(value_dict))
                    )
        else:
            if page_url is not None:
                document_metadata = [
                    glm.CustomMetadata(key="url", string_value=page_url)
                ]
        try:
            chunk = glm.Chunk(
                data={"string_value": text}, custom_metadata=document_metadata
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
            logging.info("Created a new text chunk in semantic retriever.\n")
            # print(response)
        except:
            logging.error(f"Failed to create a text chunk for:\n\n{text}")
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
            self.create_a_chunk(
                doc_name=doc_name, text=text_01, metadata=document_metadata
            )
            self.create_a_chunk(
                doc_name=doc_name, text=text_02, metadata=document_metadata
            )
        return response

    def delete_a_chunk(self, chunk_name: str):
        response = []
        try:
            request = glm.DeleteChunkRequest(name=chunk_name)
            response = self.retriever_service_client.delete_chunk(request)
        except:
            logging.error(f"Cannot delete a chunk: {chunk_name}")
        return response

    def create_a_doc_chunk(
        self,
        corpus_name: str,
        page_title: str,
        text,
        page_url: typing.Optional[str] = None,
        metadata: typing.Optional[dict] = None,
    ):
        try:
            doc_name = self.create_a_doc(
                corpus_name=corpus_name,
                page_title=page_title,
                page_url=page_url,
                metadata=metadata,
            )
            try:
                chunk = self.create_a_chunk(
                    doc_name=doc_name, text=text, metadata=metadata, page_url=page_url
                )
                return chunk
            except:
                logging.error("Error in creaing a doc chunk: " + page_title)
                return None
        except:
            logging.error("Error in creaing a doc chunk: " + page_title)
            return None

    def get_all_docs(self, corpus_name: str, print_output: bool = False):
        all_docs = []
        try:
            request = glm.ListDocumentsRequest(parent=corpus_name, page_size=20)
            response = self.retriever_service_client.list_documents(request)
            index = 0
            for docs in response.documents:
                if print_output:
                    index += 1
                    print(f"\nDocument # {index}")
                    print(f"Name: {docs.name}")
                    print(f"Display name: {docs.display_name}")
                    metadata = docs.custom_metadata
                    for item in metadata:
                        if item.key == "uuid":
                            print(f"uuid: {item.string_value}")
                        elif item.key == "md_hash":
                            print(f"md_hash: {item.string_value}")
                all_docs.append(docs)
            while (
                hasattr(response, "next_page_token") and response.next_page_token != ""
            ):
                request = glm.ListDocumentsRequest(
                    parent=corpus_name,
                    page_size=20,
                    page_token=response.next_page_token,
                )
                response = self.retriever_service_client.list_documents(request)
                for docs in response.documents:
                    if print_output:
                        index += 1
                        print(f"\nDocument # {index}")
                        print(f"Name: {docs.name}")
                        print(f"Display name: {docs.display_name}")
                        metadata = docs.custom_metadata
                        for item in metadata:
                            if item.key == "uuid":
                                print(f"uuid: {item.string_value}")
                            elif item.key == "md_hash":
                                print(f"md_hash: {item.string_value}")
                    all_docs.append(docs)
            return all_docs
        except:
            logging.error("Error in listing all docs: " + corpus_name)
            return all_docs

    def get_all_chunks(self, doc_name: str, print_output: bool = False):
        all_chunks = []
        try:
            request = glm.ListChunksRequest(parent=doc_name, page_size=20)
            response = self.retriever_service_client.list_chunks(request)
            index = 0
            for chunk in response.chunks:
                if print_output:
                    index += 1
                    print(f"\nChunk # {index}")
                    print(f"Name: {chunk.name}")
                    metadata = chunk.custom_metadata
                    for item in metadata:
                        if item.key == "uuid":
                            print(f"uuid: {item.string_value}")
                        elif item.key == "md_hash":
                            print(f"md_hash: {item.string_value}")
                        elif item.key == "text_chunk_filename":
                            print(f"text_chunk_filename: {item.string_value}")
                all_chunks.append(chunk)
            while (
                hasattr(response, "next_page_token") and response.next_page_token != ""
            ):
                request = glm.ListChunksRequest(
                    parent=doc_name,
                    page_size=20,
                    page_token=response.next_page_token,
                )
                response = self.retriever_service_client.list_chunks(request)
                for chunk in response.chunks:
                    if print_output:
                        index += 1
                        print(f"\nChunk # {index}")
                        print(f"Name: {chunk.name}")
                        metadata = chunk.custom_metadata
                        for item in metadata:
                            if item.key == "uuid":
                                print(f"uuid: {item.string_value}")
                            elif item.key == "md_hash":
                                print(f"md_hash: {item.string_value}")
                            elif item.key == "text_chunk_filename":
                                print(f"text_chunk_filename: {item.string_value}")
                    all_chunks.append(chunk)
            return all_chunks
        except:
            logging.error("Error in listing all chunks: " + doc_name)
            return all_chunks

    def share_a_corpus(self, corpus_name: str, email: str, role: str):
        shared_user_email = email
        user_type = "USER"
        user_role = role
        if user_role == "READER" or user_role == "WRITER":
            # Make the request
            request = glm.CreatePermissionRequest(
                parent=corpus_name,
                permission=glm.Permission(
                    grantee_type=user_type, email_address=shared_user_email, role=role
                ),
            )
            create_permission_response = (
                self.permission_service_client.create_permission(request)
            )
            print(create_permission_response)
            return create_permission_response
        else:
            return "Invalid input arguments."

    def open_a_corpus(self, corpus_name: str):
        user_type = "EVERYONE"
        role = "READER"

        # Make the request
        request = glm.CreatePermissionRequest(
            parent=corpus_name,
            permission=glm.Permission(grantee_type=user_type, role=role),
        )
        create_permission_response = self.permission_service_client.create_permission(
            request
        )
        print(create_permission_response)
        return create_permission_response

    def delete_permission(self, permission_name: str):
        delete_corpus_name = permission_name
        request = glm.DeletePermissionRequest(name=delete_corpus_name)
        delete_permission_response = self.permission_service_client.delete_permission(
            request
        )
        return delete_permission_response
