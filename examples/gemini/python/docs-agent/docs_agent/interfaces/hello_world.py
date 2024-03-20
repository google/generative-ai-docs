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

"""Hello World for Docs Agent"""

from docs_agent.storage.chroma import Format
from docs_agent.agents.docs_agent import DocsAgent

# This `hello_world` script contains the minimal set of function calls
# needed to use Docs Agent.
#
# Note: This script assumes that the vector database has already been populated.
#
# To run this script:
# $ python3 hello_world.py
#


def main():
    # Initialize Docs Agent.
    print("STATE: Initializing Docs Agent.")
    docs_agent = DocsAgent()

    # This question is used for testing.
    question = "What are some differences between apples and oranges?"

    # Print the question.
    print("\nQuestion: " + question)

    # Pass the question to the vector database and get a list of the most relevant content.
    result = docs_agent.query_vector_store(question)
    context = result.fetch_formatted(Format.CONTEXT)

    # Add instruction (see `condition.txt`) as a prefix to the context.
    context_with_prefix = docs_agent.add_instruction_to_context(context)

    print("\nSending prompts to Google's language models...")

    # Pass the context and question to the `gemini-pro` model.
    if "gemini" in docs_agent.get_language_model_name():
        response_gemini = docs_agent.ask_content_model_with_context(
            context_with_prefix, question
        )
        print("\n[Genmini answer]:")
        print(response_gemini)

    # Pass the context and question to the `aqa` model
    if docs_agent.check_if_aqa_is_used():
        response_aqa = docs_agent.ask_aqa_model(question)
        print("\n[AQA answer]:")
        print(response_aqa)

    # Pass the context and question to PaLM 2's `text-bison-001` model.
    response_text = docs_agent.ask_text_model_with_context(
        context_with_prefix, question
    )
    print("\n[Text answer]:")
    print(response_text)

    # Pass the context and question to PaLM 2's `chat-bison-001` model.
    response_chat = docs_agent.ask_chat_model_with_context(
        context_with_prefix, question
    )
    print("\n[Chat answer]:")
    print(response_chat)

    print("")


if __name__ == "__main__":
    main()
