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
def ask_model(question: str, product_configs: ConfigFile):
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
        # Print results
        for item in final_search:
            count += 1
        count = 0
        ai_console.print()
        ai_console.print(Markdown("To verify this information, see:\n"))
        md_links = ""
        for item in final_links:
            if isinstance(item, str):
                if not item.startswith("UUID"):
                    md_links += f"\n* [{item}]({item})\n"
                    count += 1
        ai_console.print(Markdown(md_links))


# This function is used by the `helpme` command to ask the Gemini AQA model
# a question from an online corpus.
def ask_model_with_file(
    question: str,
    product_configs: ConfigFile,
    file: typing.Optional[str] = None,
    rag: bool = False,
):
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
                if rag and product.db_type == "chroma":
                    docs_agent = DocsAgent(config=product, init_chroma=True)
                else:
                    docs_agent = DocsAgent(config=product, init_chroma=False)
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
                if file is not None:
                    results_num = 15
                    if rag:
                        (
                            search_result,
                            final_context,
                        ) = docs_agent.query_vector_store_to_build(
                            question=question,
                            token_limit=500000,
                            results_num=results_num,
                            max_sources=results_num,
                        )
                        final_context = (
                            "This is the file: \n" + str(file) + "\n\n" + final_context
                        )
                    else:
                        search_result = []
                        link = ""
                        final_context = "This is the file: \n" + str(file) + "\n"
                else:
                    # Issue if max_sources > results_num, so leave the same for now
                    (
                        search_result,
                        final_context,
                    ) = docs_agent.query_vector_store_to_build(
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
                    link = ""
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
                    link = ""
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
        # Print results
        for item in final_search:
            count += 1
        count = 0
        ai_console.print()
        md_links = ""
        for item in final_links:
            if isinstance(item, str):
                if not item.startswith("UUID"):
                    md_links += f"\n* [{item}]({item})\n"
                    count += 1
        # Avoid printing links if first link is blank
        if final_links[0] != "":
            ai_console.print(Markdown("To verify this information, see:\n"))
            ai_console.print(Markdown(md_links))
