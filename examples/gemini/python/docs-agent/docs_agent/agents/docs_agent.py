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

"""Docs Agent"""

import typing
import os, pathlib

from absl import logging
import google.api_core
import google.ai.generativelanguage as glm
from chromadb.utils import embedding_functions

from docs_agent.storage.chroma import ChromaEnhanced

from docs_agent.models.google_genai import Gemini

from docs_agent.utilities.config import ProductConfig, Models
from docs_agent.preprocess.splitters import markdown_splitter

from docs_agent.preprocess.splitters.markdown_splitter import Section as Section
from docs_agent.postprocess.docs_retriever import SectionDistance as SectionDistance
from docs_agent.postprocess.docs_retriever import (
    SectionProbability as SectionProbability,
)


class DocsAgent:
    """DocsAgent class"""

    # Temporary parameter of init_chroma
    def __init__(
        self,
        config: ProductConfig,
        init_chroma: bool = True,
        init_semantic: bool = True,
    ):
        # Models settings
        self.config = config
        self.language_model = str(self.config.models.language_model)
        self.embedding_model = str(self.config.models.embedding_model)
        self.api_endpoint = str(self.config.models.api_endpoint)

        # Initialize the default Gemini model.
        if self.language_model.startswith("models/gemini"):
            self.gemini = Gemini(
                models_config=config.models, conditions=config.conditions
            )
            self.context_model = self.language_model

        # Use the new chroma db for all queries
        # Should make a function for this or clean this behavior
        if init_chroma:
            for item in self.config.db_configs:
                if "chroma" in item.db_type:
                    self.vector_db_dir = item.vector_db_dir
                    self.collection_name = item.collection_name
            self.chroma = ChromaEnhanced(self.vector_db_dir)
            logging.info(
                "Using the local vector database created at %s", self.vector_db_dir
            )
            self.collection = self.chroma.get_collection(
                self.collection_name,
                embedding_model=self.embedding_model,
                embedding_function=embedding_function_gemini_retrieval(
                    self.config.models.api_key, self.embedding_model
                ),
            )

        # AQA model settings
        if init_semantic:
            # Except in "full" and "pro" modes, the semantic retriever option requires
            # the AQA model. If not, exit the program.
            if (
                self.config.app_mode != "full"
                and self.config.app_mode != "widget-pro"
                and self.config.db_type == "google_semantic_retriever"
            ):
                if self.language_model != "models/aqa":
                    logging.error(
                        "The db_type `google_semnatic_retriever` option"
                        + " requires the AQA model (`models/aqa`)."
                    )
                    exit(1)
            # If the AQA model is selected or the web app is on "full" and "pro" modes.
            if (
                self.language_model == "models/aqa"
                or self.config.app_mode == "full"
                or self.config.app_mode == "widget-pro"
            ):
                # AQA model setup
                self.generative_service_client = glm.GenerativeServiceClient()
                self.retriever_service_client = glm.RetrieverServiceClient()
                self.permission_service_client = glm.PermissionServiceClient()
                # Start a Gemini model for other tasks
                self.context_model = "models/gemini-pro"
                gemini_model_config = Models(
                    language_model=self.context_model,
                    embedding_model=self.embedding_model,
                    api_endpoint=self.api_endpoint,
                )
                self.gemini = Gemini(
                    models_config=gemini_model_config, conditions=config.conditions
                )
            # If semantic retriever is selected as the main database.
            if self.config.db_type == "google_semantic_retriever":
                for item in self.config.db_configs:
                    if "google_semantic_retriever" in item.db_type:
                        self.corpus_name = item.corpus_name
                        if item.corpus_display:
                            self.corpus_display = item.corpus_display
                        else:
                            self.corpus_display = (
                                self.config.product_name + " documentation"
                            )
                self.aqa_response_buffer = ""

        # Always initialize the Gemini 1.0 pro model for other tasks.
        gemini_pro_model_config = Models(
            language_model="models/gemini-pro",
            embedding_model=self.embedding_model,
            api_endpoint=self.api_endpoint,
        )
        self.gemini_pro = Gemini(
            models_config=gemini_pro_model_config, conditions=config.conditions
        )

        if self.config.app_mode == "full" or self.config.app_mode == "widget-pro":
            # Initialize the Gemini 1.5 model for generating main responses.
            gemini_15_model_config = Models(
                language_model=self.language_model,
                embedding_model=self.embedding_model,
                api_endpoint=self.api_endpoint,
            )
            self.gemini_15 = Gemini(
                models_config=gemini_15_model_config, conditions=config.conditions
            )
        else:
            self.gemini_15 = self.gemini_pro

    # Use this method for talking to a Gemini content model
    def ask_content_model_with_context(self, context, question):
        new_prompt = context + "\n\nQuestion: " + question
        # Print the prompt for debugging if the log level is VERBOSE.
        if self.config.log_level == "VERBOSE":
            self.print_the_prompt(new_prompt)
        try:
            response = self.gemini.generate_content(new_prompt)
        except google.api_core.exceptions.InvalidArgument:
            return self.config.conditions.model_error_message
        # for chunk in response:
        #     if str(chunk.candidates[0].content) == "":
        #         return self.config.conditions.model_error_message
        return response

    # Use this method for talking to Gemini's AQA model using inline passages
    # answer_style can be VERBOSE, ABSTRACTIVE, or EXTRACTIVE
    def ask_aqa_model_using_local_vector_store(
        self,
        question,
        results_num: int = 5,
        answer_style: str = "VERBOSE",
    ):
        user_query_content = glm.Content(parts=[glm.Part(text=question)])
        verbose_prompt = "Question: " + question + "\n"
        # Retrieves from chroma, using up to 30k tokens - max gemini model tokens
        chroma_search_result, final_context = self.query_vector_store_to_build(
            question=question,
            token_limit=30000,
            results_num=results_num,
            max_sources=results_num,
        )
        # Create the grounding inline passages
        grounding_passages = glm.GroundingPassages()
        i = 0
        aqa_search_result = []
        for item in chroma_search_result:
            returned_context = item.section.content
            new_passage = glm.Content(parts=[glm.Part(text=returned_context)])
            index_id = str("{:03d}".format(i + 1))
            i += 1
            grounding_passages.passages.append(
                glm.GroundingPassage(content=new_passage, id=index_id)
            )
            verbose_prompt += "\nID: " + index_id + "\n" + returned_context + "\n"
        req = glm.GenerateAnswerRequest(
            model="models/aqa",
            contents=[user_query_content],
            inline_passages=grounding_passages,
            answer_style=answer_style,
        )
        aqa_response = self.generative_service_client.generate_answer(req)
        self.aqa_response_buffer = aqa_response
        for item in chroma_search_result:
            # Builds an object with sections + probability
            aqa_search_result.append(
                SectionProbability(
                    section=item.section,
                    probability=aqa_response.answerable_probability,
                )
            )
        if self.config.log_level == "VERBOSE":
            self.print_the_prompt(verbose_prompt)
        elif self.config.log_level == "DEBUG":
            self.print_the_prompt(verbose_prompt)
            print(aqa_response)
        try:
            return aqa_response.answer.content.parts[0].text, aqa_search_result
        except:
            self.aqa_response_buffer = ""
            return self.config.conditions.model_error_message, aqa_search_result

    # Get the save response of the AQA model
    def get_saved_aqa_response_json(self):
        return self.aqa_response_buffer

    # Retrieve the metadata dictionary from an AQA response grounding attribution entry
    def get_aqa_response_metadata(self, aqa_response_item):
        try:
            chunk_resource_name = (
                aqa_response_item.source_id.semantic_retriever_chunk.chunk
            )
            get_chunk_response = self.retriever_service_client.get_chunk(
                name=chunk_resource_name
            )
            metadata = get_chunk_response.custom_metadata
            final_metadata = {}
            for m in metadata:
                if m.string_value:
                    value = m.string_value
                elif m.numeric_value:
                    value = m.numeric_value
                else:
                    value = ""
                final_metadata[m.key] = value
        except:
            final_metadata = {}
        return final_metadata

    # Use this method for talking to Gemini's AQA model using a corpus
    # Answer style can be "VERBOSE" or ABSTRACTIVE, EXTRACTIVE
    def ask_aqa_model_using_corpora(
        self, question, corpus_name: str = "None", answer_style: str = "VERBOSE"
    ):
        search_result = []
        if corpus_name == "None":
            corpus_name = self.corpus_name
        # Prepare parameters for the AQA model
        user_question_content = glm.Content(
            parts=[glm.Part(text=question)], role="user"
        )
        # Settings to retrieve grounding content from semantic retriever
        retriever_config = glm.SemanticRetrieverConfig(
            source=corpus_name, query=user_question_content
        )

        # Ask the AQA model.
        req = glm.GenerateAnswerRequest(
            model="models/aqa",
            contents=[user_question_content],
            semantic_retriever=retriever_config,
            answer_style=answer_style,
        )

        try:
            aqa_response = self.generative_service_client.generate_answer(req)
            self.aqa_response_buffer = aqa_response
        except:
            self.aqa_response_buffer = ""
            return self.config.conditions.model_error_message, search_result

        if self.config.log_level == "VERBOSE":
            verbose_prompt = "[question]\n" + question + "\n"
            verbose_prompt += (
                "\n[answerable_probability]\n"
                + str(aqa_response.answerable_probability)
                + "\n"
            )
            for attribution in aqa_response.answer.grounding_attributions:
                verbose_prompt += "\n[grounding_attributions]\n" + str(
                    attribution.content.parts[0].text
                )
            self.print_the_prompt(verbose_prompt)
        elif self.config.log_level == "DEBUG":
            print(aqa_response)
        try:
            for item in aqa_response.answer.grounding_attributions:
                metadata = self.get_aqa_response_metadata(item)
                for part in item.content.parts:
                    metadata["content"] = part.text
                section = markdown_splitter.DictionarytoSection(metadata)
                search_result.append(
                    SectionProbability(
                        section=section, probability=aqa_response.answerable_probability
                    )
                )
            # Return the aqa_response object but also the actual text response
            return aqa_response.answer.content.parts[0].text, search_result
        except:
            return self.config.conditions.model_error_message, search_result

    def ask_aqa_model(self, question):
        response = ""
        if self.config.db_type == "google_semantic_retriever":
            response = self.ask_aqa_model_using_corpora(question)
        else:
            response = self.ask_aqa_model_using_local_vector_store(question)
        return response

    # Retrieve and return chunks that are most relevant to the input question.
    def retrieve_chunks_from_corpus(self, question, corpus_name: str = "None"):
        if corpus_name == "None":
            corpus_name = self.corpus_name
        user_query = question
        results_count = 5
        # Quick fix: This was needed to allow the method to be called
        # even when the model is not set to `models/aqa`.
        retriever_service_client = glm.RetrieverServiceClient()
        # Make the request
        request = glm.QueryCorpusRequest(
            name=corpus_name, query=user_query, results_count=results_count
        )
        query_corpus_response = retriever_service_client.query_corpus(request)
        return query_corpus_response

    # Use this method for asking a Gemini content model for fact-checking
    def ask_content_model_to_fact_check(self, context, prev_response):
        question = self.config.conditions.fact_check_question + "\n\nText: "
        question += prev_response
        return self.ask_content_model_with_context(context, question)

    # Query the local Chroma vector database using the user question
    def query_vector_store(self, question, num_returns: int = 5):
        return self.collection.query(question, num_returns)

    # Add specific instruction as a prefix to the context
    def add_instruction_to_context(self, context):
        new_context = ""
        new_context += self.config.conditions.condition_text + "\n\n" + context
        return new_context

    # Add custom instruction as a prefix to the context
    def add_custom_instruction_to_context(self, condition, context):
        new_context = ""
        new_context += condition + "\n\n" + context
        return new_context

    # Return true if the aqa model used in this Docs Agent setup
    def check_if_aqa_is_used(self):
        if (
            self.config.models.language_model == "models/aqa"
            or self.config.app_mode == "full"
            or self.config.app_mode == "widget-pro"
        ):
            return True
        else:
            return False

    # Return the chroma collection name
    def return_chroma_collection(self):
        try:
            return self.collection_name
        except:
            return None

    # Return the vector db name
    def return_vector_db_dir(self):
        try:
            return self.vector_db_dir
        except:
            return None

    # Print the prompt on the terminal for debugging
    def print_the_prompt(self, prompt):
        print("#########################################")
        print("#              PROMPT                   #")
        print("#########################################")
        print(prompt)
        print("#########################################")
        print("#           END OF PROMPT               #")
        print("#########################################")
        print("\n")

    # Query the local Chroma vector database. Starts with the number of results
    # from results
    # Results_num is the initial result set based on distance to the question
    # Max_sources is the number of those results_num to use to build a final
    # context page
    def query_vector_store_to_build(
        self,
        question: str,
        token_limit: float = 30000,
        results_num: int = 10,
        max_sources: int = 4,
    ):
        # Looks for contexts related to a question that is limited to an int
        # Returns a list
        contexts_query = self.collection.query(question, results_num)
        # This returns a list of results
        build_context = contexts_query.returnDBObjList()
        # Use the token limit and distances to assign a token limit for each
        # page. For time being split evenly into top max_sources
        token_limit_temp = token_limit / max_sources
        token_limit_per_source = []
        i = 0
        for i in range(max_sources):
            token_limit_per_source.append(token_limit_temp)
        same_document = ""
        same_metadata = ""
        # Each item is a chunk result along with all of it's metadata
        # We can use metadata to identify if one of these chunks comes from the
        # same page, potentially indicating a better match, so more token allocation
        # You can see these objects contents with .content, .document, .distance, .metadata
        plain_content = ""
        search_result = []
        same_pages = []
        # For each result make a SectionDistance object that includes the
        # Section along with it's distance from the question
        for item in build_context:
            # Check if this page was previously added as a source, to avoid
            # duplicate count. These signals should be used to give a page higher token limits
            # Make a page based on the section_id (this is where the search
            # found a match)
            section = SectionDistance(
                section=Section(
                    id=item.metadata.get("section_id", None),
                    name_id=item.metadata.get("name_id", None),
                    page_title=item.metadata.get("page_title", None),
                    section_title=item.metadata.get("section_title", None),
                    level=item.metadata.get("level", None),
                    previous_id=item.metadata.get("previous_id", None),
                    parent_tree=item.metadata.get("parent_tree", None),
                    token_count=item.metadata.get("token_estimate", None),
                    content=item.document,
                    md_hash=item.metadata.get("md_hash", None),
                    url=item.metadata.get("url", None),
                    origin_uuid=item.metadata.get("origin_uuid", None),
                ),
                distance=item.distance,
            )
            search_result.append(section)
            # From this you can run queries to find all chunks from the same page
            # since they all share the same origin_uuid which is a hash of the
            # original source file name
        # Limits the number of results to go through
        final_page_content = []
        final_page_token = []
        plain_token = 0
        sources = []
        final_pages = []
        # Quick fix: Ensure max_sources is not larger than the array size of search_result.
        this_range = len(search_result)
        if this_range > max_sources:
            this_range = max_sources
        for i in range(this_range):
            # The current section that is being built
            # eval turns str representation of array into an array
            curr_section_id = search_result[i].section.name_id
            curr_parent_tree = eval(search_result[i].section.parent_tree)
            # Assigned token limit for this position in the list
            page_token_limit = token_limit_per_source[i]
            # Returns a FullPage which is just a list of Section
            same_page = self.collection.getPageOriginUUIDList(
                origin_uuid=search_result[i].section.origin_uuid
            )
            same_pages.append(same_page)
            # Use all sections in experimental, only self when "normal"
            if self.config.docs_agent_config == "experimental":
                test_page = same_page.buildSections(
                    section_id=search_result[i].section.id,
                    selfSection=True,
                    children=True,
                    parent=True,
                    siblings=True,
                    token_limit=token_limit_per_source[i],
                )
            else:
                test_page = same_page.buildSections(
                    section_id=search_result[i].section.id,
                    selfSection=True,
                    children=False,
                    parent=False,
                    siblings=False,
                    token_limit=token_limit_per_source[i],
                )
            final_pages.append(test_page)
        # Each item here is a FullPage corresponding to the source
        final_context = ""
        for item in final_pages:
            for source in item.section_list:
                final_context += source.content + "\n\n"
        final_context = final_context.strip()
        # Result contains the search result of Section of the initial hits
        # final_pages could be returned to get the full Section for displaying
        # context with metadata
        return search_result, final_context

    # Use this method for talking to a Gemini content model
    # Optionally provide a prompt, if not use the one from config.yaml
    # If prompt is "fact_checker" it will use the fact_check_question from
    # config.yaml for the prompt
    def ask_content_model_with_context_prompt(
        self,
        context: str,
        question: str,
        prompt: typing.Optional[str] = None,
        model: typing.Optional[str] = None,
    ):
        if prompt == None:
            prompt = self.config.conditions.condition_text
        elif prompt == "fact_checker":
            prompt = self.config.conditions.fact_check_question
        new_prompt = f"{prompt}\n\nContext:\n{context}\nQuestion:\n{question}"
        # Print the prompt for debugging if the log level is VERBOSE.
        if self.config.log_level == "VERBOSE":
            self.print_the_prompt(new_prompt)
        try:
            response = ""
            if model == "gemini-pro":
                response = self.gemini_pro.generate_content(
                    contents=new_prompt, log_level=self.config.log_level
                )
            elif model == "gemini-1.5":
                response = self.gemini_15.generate_content(
                    contents=new_prompt, log_level=self.config.log_level
                )
            else:
                response = self.gemini.generate_content(
                    contents=new_prompt, log_level=self.config.log_level
                )
        except Exception as e:
            print("Error in generate_content()")
            print(e)
            return self.config.conditions.model_error_message, new_prompt
        return response, new_prompt

    # Use this method for talking to a Gemini content model
    # Provide a prompt, followed by the content of the file
    # This isn't in use yet, but can be used to give an LLM a full or partial file
    def ask_content_model_to_use_file(self, prompt: str, file: str):
        new_prompt = prompt + file
        # Print the prompt for debugging if the log level is VERBOSE.
        if self.config.log_level == "VERBOSE":
            self.print_the_prompt(new_prompt)
        try:
            response = self.gemini.generate_content(contents=new_prompt)
        except google.api_core.exceptions.InvalidArgument:
            return self.config.conditions.model_error_message
        return response

    # Use this method for asking a Gemini content model for fact-checking.
    # This uses ask_content_model_with_context_prompt w
    def ask_content_model_to_fact_check_prompt(self, context: str, prev_response: str):
        question = self.config.conditions.fact_check_question + "\n\nText: "
        question += prev_response
        return self.ask_content_model_with_context_prompt(
            context=context, question=question, prompt=""
        )

    # Generate an embedding given text input
    def generate_embedding(self, text, task_type: str = "SEMANTIC_SIMILARITY"):
        return self.gemini.embed(text, task_type)[0]

    # Generate a response to an image
    def ask_model_about_image(self, prompt: str, image):
        if not prompt:
            prompt = f"Describe this image:"
        if self.context_model.startswith("models/gemini-1.5"):
            try:
                # Adding prompt in the beginning allows long contextual
                # information to be added.
                response = self.gemini.generate_content([prompt, image])
            except google.api_core.exceptions.InvalidArgument:
                return self.config.conditions.model_error_message
        else:
            logging.error(f"The {self.context_model} can't read an image.")
            response = None
            exit(1)
        return response

    # Generate a response to audio
    def ask_model_about_audio(self, prompt: str, audio):
        if not prompt:
            prompt = f"Describe this audio clip:"
        audio_size = os.path.getsize(audio)
        # Limit is 20MB
        if audio_size > 20000000:
            logging.error(f"The audio clip {audio} is too large: {audio_size} bytes.")
            exit(1)
        # Get the mime type of the audio file and trim the . from the extension.
        mime_type = "audio/" + pathlib.Path(audio).suffix[:1]
        audio_clip = {
            "mime_type": mime_type,
            "data": pathlib.Path(audio).read_bytes()
        }
        if self.context_model.startswith("models/gemini-1.5"):
            try:
                response = self.gemini.generate_content([prompt, audio_clip])
            except google.api_core.exceptions.InvalidArgument:
                return self.config.conditions.model_error_message
        else:
            logging.error(f"The {self.context_model} can't read an audio clip.")
            exit(1)
        return response

    # Generate a response to video
    def ask_model_about_video(self, prompt: str, video):
        if not prompt:
            prompt = f"Describe this video clip:"
        video_size = os.path.getsize(video)
        # Limit is 2GB
        if video_size > 2147483648:
            logging.error(f"The video clip {video} is too large: {video_size} bytes.")
            exit(1)
        request_options = {
            "timeout": 600
        }
        mime_type = "video/" + pathlib.Path(video).suffix[:1]
        video_clip_uploaded =self.gemini.upload_file(video)
        video_clip = self.gemini.get_file(video_clip_uploaded)
        if self.context_model.startswith("models/gemini-1.5"):
            try:
                response = self.gemini.generate_content([prompt, video_clip],
                                                        request_options=request_options)
            except google.api_core.exceptions.InvalidArgument:
                return self.config.conditions.model_error_message
        else:
            logging.error(f"The {self.context_model} can't see video clips.")
            exit(1)
        return response

# Function to give an embedding function for gemini using an API key
def embedding_function_gemini_retrieval(api_key, embedding_model: str):
    return embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=api_key, model_name=embedding_model, task_type="RETRIEVAL_QUERY"
    )
