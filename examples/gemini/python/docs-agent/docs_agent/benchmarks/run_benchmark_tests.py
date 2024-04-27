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

"""Run benchmark tests to measure the quality of embeddings, context chunks, and AI responses"""

import os
import sys
import yaml

import numpy as np

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from docs_agent.storage.chroma import Format
from docs_agent.agents.docs_agent import DocsAgent
from docs_agent.utilities import config
from docs_agent.utilities.config import ProductConfig


# A function that asks the questin to the AI model using the RAG technique.
def ask_model(question: str, docs_agent: DocsAgent):
    results_num = 5
    if "gemini" in docs_agent.config.models.language_model:
        # print("Asking a Gemini model")
        (search_result, final_context) = docs_agent.query_vector_store_to_build(
            question=question,
            token_limit=30000,
            results_num=results_num,
            max_sources=results_num,
        )
        response, full_prompt = docs_agent.ask_content_model_with_context_prompt(
            context=final_context, question=question
        )
    elif "aqa" in docs_agent.config.models.language_model:
        # print("Asking the AQA model")
        if docs_agent.config.db_type == "google_semantic_retriever":
            (response, search_result) = docs_agent.ask_aqa_model_using_corpora(
                question=question
            )
        elif docs_agent.config.db_type == "chroma":
            (
                response,
                search_result,
            ) = docs_agent.ask_aqa_model_using_local_vector_store(
                question=question, results_num=results_num
            )
        else:
            (response, search_result) = docs_agent.ask_aqa_model_using_corpora(
                question=question
            )
    return response


# A customized print function
def vprint(text: str, VERBOSE: bool = False):
    if VERBOSE:
        print(text)


# A function that computes cosine similarity between two vectors
def compute_cosine_similarity(v1, v2):
    a = np.asarray(v1)
    b = np.asarray(v2)
    dot = np.dot(a, b)
    a_norm = np.linalg.norm(a, 2)
    b_norm = np.linalg.norm(b, 2)
    cosine = dot / (a_norm * b_norm)
    return cosine


# Read the `benchmarks.yaml` file in the `benchmarks` directory of the project.
def read_benchmarks_yaml():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BENCHMARKS_YAML = os.path.join(BASE_DIR, "benchmarks/benchmarks.yaml")
    try:
        with open(BENCHMARKS_YAML, "r", encoding="utf-8") as b_yaml:
            read_values = yaml.safe_load(b_yaml)
    except FileNotFoundError:
        print("The " + BENCHMARKS_YAML + " file is missing.")
        sys.exit(1)
    return read_values


def run_benchmarks():
    # VERBOSE = False
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Initialize Rich console
    my_console = Console(width=160)

    # Read the configuration file (`config.yaml`)
    config_file = config.ReadConfig().returnProducts()
    # TODO: This benchmark test only selects the first product
    #       in the product list in the config file at the moment.
    product = config_file.products[0]
    print(f"===========================================")
    print(f"Benchmark test target product: {product.product_name}")
    print(f"===========================================")

    # Initialize Docs Agent
    if product.db_type == "google_semantic_retriever":
        docs_agent = DocsAgent(config=product, init_chroma=False)
    else:
        docs_agent = DocsAgent(config=product)

    # Read the `benchmarks.yaml` file.
    benchmark_values = read_benchmarks_yaml()

    questions = []
    results = []
    index = 0
    print()
    for benchmark in benchmark_values["benchmarks"]:
        embedding_01 = ""
        embedding_02 = ""
        response = ""
        similarity = ""

        # Step 1. Read a `question` and `target_answer` pair.
        question = benchmark["question"]
        target_answer = benchmark["target_answer"]
        questions.append(question)
        print("================")
        print("Benchmark " + str(index))
        print("================")
        print("Question: " + question)
        print("Target answer: " + target_answer)
        print()

        # Step 2. Generate an embedding using `target_answer` - Embedding 1.
        vprint("################")
        vprint("# Embedding 1  #")
        vprint("################")
        vprint("Input text:")
        vprint(target_answer)
        embedding_01 = docs_agent.generate_embedding(target_answer)
        vprint("")
        vprint("Embedding:")
        vprint(str(embedding_01))

        # Step 3. Ask `question` to the AI model.
        response = ask_model(question, docs_agent)
        vprint("################")
        vprint("# Response     #")
        vprint("################")
        vprint(response)

        # Step 4. Generate an embedding using the response - Embedding 2.
        vprint("################")
        vprint("# Embedding 2  #")
        vprint("################")
        vprint("Input text:")
        vprint(response)
        embedding_02 = docs_agent.generate_embedding(response)
        vprint("")
        vprint("Embedding:")
        vprint(str(embedding_02))

        # Step 5. Compute the similarity between Embedding 1 and Embedding 2.
        vprint("################")
        vprint("# Similarity   #")
        vprint("################")
        similarity = compute_cosine_similarity(embedding_01, embedding_02)
        vprint(similarity)
        vprint("")
        results.append(similarity)

        # Step 6. Print the summary of this run.
        print("################")
        print("# Result       #")
        print("################")
        print("Question:")
        my_console.print(Panel.fit(Markdown(question)))
        print()
        print("Target answer:")
        my_console.print(Panel.fit(Markdown(target_answer)))
        print()
        print("AI Response:")
        my_console.print(Panel.fit(Markdown(response)))
        print()
        print("Similarity:")
        print(similarity)
        print()

        index += 1

    # Print the benchmark test results.
    print("################################")
    print("# Benchmark tests summary      #")
    print("################################")
    print()
    print("Similarity (-1, 1)" + "    " + "Question")
    print("==================" + "    " + "========")
    for i, q in enumerate(questions):
        print(str("{:.16f}".format(results[i])) + "    " + q)
    print()

    # Store the benchmark test results into benchmarks/results.out.
    BENCHMARKS_OUT = os.path.join(BASE_DIR, "benchmarks/results.out")
    with open(BENCHMARKS_OUT, "w", encoding="utf-8") as outfile:
        outfile.write("Similarity (-1, 1)" + "    " + "Question\n")
        outfile.write("==================" + "    " + "========\n")
        for i, q in enumerate(questions):
            outfile.write(str("{:.16f}".format(results[i])) + "    " + q + "\n")
    print("Created " + BENCHMARKS_OUT + " to store the results of the benchmark tests.")


if __name__ == "__main__":
    run_benchmarks()
