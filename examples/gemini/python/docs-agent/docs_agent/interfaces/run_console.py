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

"""Run the Docs Agent console in the terminal"""

import typing
from absl import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress
from PIL import Image

from docs_agent.agents.docs_agent import DocsAgent
from docs_agent.utilities.config import ConfigFile


# This function is used by the `helpme` command to ask the Gemini Pro model
# to perform a task based on the console ouput.
def ask_model_for_help(question: str, context: str, product_configs: ConfigFile):
    # Initialize Rich console
    ai_console = Console(width=160)
    # Filter the input context into text.
    context_text = Text(context)
    # Print the console output to be provided as context.
    ai_console.print("[Context from console output]")
    ai_console.print(Panel(context_text), markup=False)
    # Initialize Docs Agent
    docs_agent = DocsAgent(config=product_configs.products[0], init_chroma=False)
    (
        good_response,
        new_prompt,
    ) = docs_agent.ask_content_model_with_context_prompt(
        context=context,
        question=question,
        prompt="Examine the console output below and respond to the user's request specified at the end of this prompt:",
    )
    # Print the Gemini response
    ai_console.print()
    ai_console.print("[Gemini response]")
    ai_console.print()
    ai_console.print(good_response)


# This function is used by the `tellme` command to ask the Gemini AQA model
# a question from an online corpus.
def ask_model(question: str, product_configs: ConfigFile, return_output: bool = False):
    # Initialize Rich console
    ai_console = Console(width=160)
    full_prompt = ""
    final_context = ""
    results_num = 5
    # Initialize Docs Agent
    with Progress(transient=True) as progress:
        search_results = []
        responses = []
        links = []
        task_docs_agent = progress.add_task(
            "[turquoise4 bold]Starting Docs Agent ", total=None, refresh=True
        )
        for product in product_configs.products:
            if "gemini" in product.models.language_model:
                docs_agent = DocsAgent(config=product)
                progress.update(
                    task_docs_agent,
                    description=f"[turquoise4 bold]Asking Gemini (model: {product.models.language_model}, source: {docs_agent.return_chroma_collection()}) ",
                    total=None,
                )
                if docs_agent.config.docs_agent_config == "experimental":
                    results_num = 10
                    new_question_count = 5
                else:
                    results_num = 5
                    new_question_count = 5
                # Issue if max_sources > results_num, so leave the same for now
                search_result, final_context = docs_agent.query_vector_store_to_build(
                    question=question,
                    token_limit=30000,
                    results_num=results_num,
                    max_sources=results_num,
                )
                (
                    response,
                    full_prompt,
                ) = docs_agent.ask_content_model_with_context_prompt(
                    context=final_context, question=question
                )
                if len(search_result) >= 1:
                    if search_result[0].section.url == "":
                        link = str(search_result[0].section)
                    else:
                        link = search_result[0].section.url
                search_results.append(search_result)
                responses.append(response)
                links.append(link)
            elif "aqa" in product.models.language_model:
                if product.db_type == "google_semantic_retriever":
                    docs_agent = DocsAgent(config=product, init_chroma=False)
                    label = f"[turquoise4 bold]Asking Gemini (model: {product.models.language_model}, "
                    corpus_name = ""
                    for db_config in product.db_configs:
                        if db_config.db_type == "google_semantic_retriever":
                            corpus_name = db_config.corpus_name
                    if corpus_name != "":
                        label += "source: " + corpus_name + ") "
                    progress.update(
                        task_docs_agent, description=label, total=None, refresh=True
                    )
                    (response, search_result) = docs_agent.ask_aqa_model_using_corpora(
                        question=question
                    )
                    if len(search_result) >= 1:
                        if search_result[0].section.url == "":
                            link = str(search_result[0].section)
                        else:
                            link = search_result[0].section.url
                    search_results.append(search_result)
                    responses.append(response)
                    links.append(link)
                elif product.db_type == "chroma":
                    docs_agent = DocsAgent(config=product, init_chroma=True)
                    progress.update(
                        task_docs_agent,
                        description=f"[turquoise4 bold]Asking Gemini (model: {product.models.language_model}, source: {docs_agent.return_chroma_collection()}) ",
                        total=None,
                    )
                    (
                        response,
                        search_result,
                    ) = docs_agent.ask_aqa_model_using_local_vector_store(
                        question=question, results_num=results_num
                    )
                    if len(search_result) >= 1:
                        if search_result[0].section.url == "":
                            link = str(search_result[0].section)
                        else:
                            link = search_result[0].section.url
                    search_results.append(search_result)
                    responses.append(response)
                    links.append(link)
                else:
                    logging.error(f"Unknown db_type: {product.db_type}")
        final_search = []
        final_responses = []
        final_response_md = ""
        final_links = []
        count = 0
        # Prune the generated answers as needed
        for item in search_results:
            # Gemini-pro + chroma will give distance instead of probability
            # if (item[0].probability != 0):
            final_search.append(search_results[count])
            final_responses.append(responses[count])
            final_response_md += responses[count] + "\n"
            final_links.append(links[count])
            count += 1

        # Print the response.
        count = 0
        synthesize = False
        synthesize_product = None
        # Currently only triggers from a gemini entry into the provided products
        for product in product_configs.products:
            if "gemini" in product.models.language_model:
                synthesize_product = product

        if synthesize and not (synthesize_product == None):
            docs_agent = DocsAgent(config=synthesize_product, init_chroma=False)
            progress.update(
                task_docs_agent,
                description=f"[turquoise4 bold]Asking {docs_agent.context_model} to synthesize a response",
                total=None,
            )
            new_question = f"Help me synthesize the context above into a cohesive response to help me answer my original question. Only use content from the provided context. My original question: {question}"
            (
                good_response,
                new_prompt,
            ) = docs_agent.ask_content_model_with_context_prompt(
                context=final_response_md, question=new_question, prompt=""
            )
            progress.update(task_docs_agent, visible=False, refresh=True)
            # Final printing to console
            ai_console.print()
            ai_console.print(Markdown(good_response))
        else:
            # This returns the responses as is for each agent interaction
            progress.update(task_docs_agent, visible=False, refresh=True)
            ai_console.print()
            ai_console.print(Markdown(final_response_md))

        # Get the link to the source.
        md_links = ""
        for item in final_links:
            if isinstance(item, str):
                if not item.startswith("UUID"):
                    md_links += f"\n* [{item}]({item})\n"

        # Print the link to the source.
        ai_console.print()
        ai_console.print(Markdown("To verify this information, see:\n"))
        ai_console.print(Markdown(md_links))

        # Retrun the output if the `return_output` flag is set.
        if return_output:
            return_string = (
                str(final_response_md.strip())
                + "\n\nTo verify this information, see:\n"
                + md_links
            )
            return return_string


# This function is used by the `helpme` command to ask a Gemini model
# a question without additional context.
def ask_model_without_context(
    question: str,
    product_configs: ConfigFile,
    return_output: bool = False,
):
    # Initialize Rich console
    ai_console = Console(width=160)
    full_prompt = ""
    final_context = ""
    response = ""

    # Use the first product by default.
    product = product_configs.products[0]
    language_model = product.models.language_model
    with Progress(transient=True) as progress:
        task_docs_agent = progress.add_task(
            "[turquoise4 bold]Starting Docs Agent ", total=None, refresh=True
        )
        # Initialize Docs Agent.
        docs_agent = DocsAgent(config=product, init_chroma=False, init_semantic=False)
        # Set the progress bar.
        label = f"[turquoise4 bold]Asking Gemini (model: {language_model}) "
        progress.update(task_docs_agent, description=label, total=None, refresh=True)
        final_context = "No additional context is necessary for this question."
        # Ask Gemini with the question without additional context.
        response = docs_agent.ask_content_model_with_context(
            context=final_context, question=question
        )
    if return_output:
        return str(response.strip())
    ai_console.print()
    ai_console.print(Markdown(response.strip()))


# This function is used by the `helpme` command to ask a Gemini model
# a question with various context sources.
def ask_model_with_file(
    question: str,
    product_configs: ConfigFile,
    file: typing.Optional[str] = None,
    context_file: typing.Optional[str] = None,
    rag: bool = False,
    return_output: bool = False,
):
    # Initialize Rich console
    ai_console = Console(width=160)
    full_prompt = ""
    final_context = ""
    response = ""

    # Set the file extension.
    file_ext = None
    is_image = False
    is_audio = False
    is_video = False
    loaded_image = None
    if file != None:
        if file.endswith(".png"):
            file_ext = "png"
            is_image = True
        elif file.endswith(".jpg"):
            file_ext = "jpg"
            is_image = True
        elif file.endswith(".gif"):
            file_ext = "gif"
            is_image = True
        elif file.endswith(".wav"):
            file_ext = "wav"
            is_audio = True
        elif file.endswith(".mp3"):
            file_ext = "wav"
            is_audio = True
        elif file.endswith(".flac"):
            file_ext = "flac"
            is_audio = True
        elif file.endswith(".aiff"):
            file_ext = "aiff"
            is_audio = True
        elif file.endswith(".aac"):
            file_ext = "aac"
            is_audio = True
        elif file.endswith(".ogg"):
            file_ext = "aac"
            is_audio = True
        elif file.endswith(".mp4"):
            file_ext = "mp4"
            is_video = True
        elif file.endswith(".mp4"):
            file_ext = "mp4"
            is_video = True
        elif file.endswith(".mov"):
            file_ext = "mov"
            is_video = True
        elif file.endswith(".avi"):
            file_ext = "avi"
            is_video = True
        elif file.endswith(".x-flv"):
            file_ext = "x-flv"
            is_video = True
        elif file.endswith(".mpg"):
            file_ext = "mpg"
            is_video = True
        elif file.endswith(".webm"):
            file_ext = "webm"
            is_video = True
        elif file.endswith(".wmv"):
            file_ext = "wmv"
            is_video = True
        elif file.endswith(".3gpp"):
            file_ext = "3gpp"
            is_video = True

    # Get the content of the target file.
    file_content = ""
    if file != None and not is_image and not is_audio and not is_video:
        try:
            with open(file, "r", encoding="utf-8") as auto:
                content = auto.read()
                auto.close()
            file_content = f"\nTHE CONTENT BELOW IS FROM THE FILE {file}:\n\n" + content
        except:
            print(f"Cannot open the file {file}")
            exit(1)
    elif is_image:
        try:
            with open(file, "rb") as image:
                loaded_image = Image.open(image)
                loaded_image.load()
        except:
            print(f"Cannot open the image {file}")
            exit(1)

    # Get the content of the context file.
    context_file_content = ""
    if context_file != None:
        try:
            with open(context_file, "r", encoding="utf-8") as auto:
                content = auto.read()
                auto.close()
            context_file_content = (
                f"\nTHE CONTENT BELOW IS FROM THE PREVIOUS EXCHANGES WITH GEMINI:\n\n"
                + content
            )
            file_content = context_file_content + "\n\n" + file_content
        except:
            print(f"Cannot open the context file {file}")
            exit(1)

    # Use the first product by default.
    product = product_configs.products[0]
    language_model = product.models.language_model
    with Progress(transient=True) as progress:
        task_docs_agent = progress.add_task(
            "[turquoise4 bold]Starting Docs Agent ", total=None, refresh=True
        )
        if rag:
            # RAG specified. Retrieve additional context from a database.
            if product.db_type == "chroma":
                # Use a local Chroma database.
                # Initialize Docs Agent.
                docs_agent = DocsAgent(
                    config=product, init_chroma=True, init_semantic=False
                )
                # Get the Chroma collection name.
                collection = docs_agent.return_chroma_collection()
                # Set the progress bar.
                label = f"[turquoise4 bold]Asking Gemini (model: {language_model}, source: {collection}) "
                progress.update(
                    task_docs_agent, description=label, total=None, refresh=True
                )
                # Retrieve context from the local Chroma database.
                (
                    search_result,
                    returned_context,
                ) = docs_agent.query_vector_store_to_build(
                    question=question,
                    token_limit=500000,
                    results_num=5,
                    max_sources=5,
                )
                context_from_database = ""
                chunk_count = 0
                for item in search_result:
                    context_from_database += item.section.content
                    context_from_database += f"\nReference [{chunk_count}]\n\n"
                    chunk_count += 1
                # Construct the final context for the question.
                final_context = (
                    "\nTHE CONTENT BELOW IS RETRIEVED FROM THE LOCAL DATABASE:\n\n"
                    + context_from_database.strip()
                    + "\n\n"
                    + str(file_content)
                )
            elif product.db_type == "google_semantic_retriever":
                # Use an online corpus from the Semantic Retrieval API.
                # Initialize Docs Agent.
                docs_agent = DocsAgent(
                    config=product, init_chroma=False, init_semantic=True
                )
                # Get the corpus name.
                corpus_name = ""
                for db_config in product.db_configs:
                    if db_config.db_type == "google_semantic_retriever":
                        corpus_name = db_config.corpus_name
                # Set the progress bar.
                label = f"[turquoise4 bold]Asking Gemini (model: {language_model}, source: {corpus_name}) "
                progress.update(
                    task_docs_agent, description=label, total=None, refresh=True
                )
                # Retrieve context from the online corpus.
                context_chunks = docs_agent.retrieve_chunks_from_corpus(
                    question, corpus_name=str(corpus_name)
                )
                context_from_corpus = ""
                chunk_count = 0
                for chunk in context_chunks.relevant_chunks:
                    context_from_corpus += chunk.chunk.data.string_value
                    context_from_corpus += f"\nReference [{chunk_count}]\n\n"
                    chunk_count += 1
                # Construct the final context for the question.
                final_context = (
                    "\nTHE CONTENT BELOW IS RETRIEVED FROM THE ONLINE DATABASE:\n\n"
                    + context_from_corpus.strip()
                    + "\n\n"
                    + str(file_content)
                )
            else:
                logging.error(f"Unknown db_type: {product.db_type}")
                exit(1)
        else:
            # No RAG specified. No additional context to be retrieved from a database.
            docs_agent = DocsAgent(
                config=product, init_chroma=False, init_semantic=False
            )
            progress.update(
                task_docs_agent,
                description=f"[turquoise4 bold]Asking Gemini (model: {language_model}) ",
                total=None,
            )
            final_context = file_content
        if is_image:
            this_prompt = final_context + "\nQUESTION (REQUEST): " + question
            response = docs_agent.ask_model_about_image(
                prompt=this_prompt, image=loaded_image
            )
        elif is_audio:
            this_prompt = final_context + "\nQUESTION (REQUEST): " + question
            response = docs_agent.ask_model_about_audio(
                prompt=this_prompt, audio=file
            )
        elif is_video:
            this_prompt = final_context + "\nQUESTION (REQUEST): " + question
            response = docs_agent.ask_model_about_video(
                prompt=this_prompt, video=file
            )
        else:
            # Ask Gemini with the question and final context.
            (
                response,
                full_prompt,
            ) = docs_agent.ask_content_model_with_context_prompt(
                context=final_context, question=question
            )
        if return_output:
            return str(response.strip())
        ai_console.print()
        ai_console.print(Markdown(response.strip()))
