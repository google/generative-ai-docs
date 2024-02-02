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

from absl import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
import sys

from modules.chroma import Format
from docs_agent import DocsAgent

# Set logging level to WARNING or above to disable progress bar
logging.set_verbosity(logging.WARNING)

# Initialize Rich console
ai_console = Console(width=160)
ai_console.rule("Fold")

# Initialize Docs Agent
ai_console.print("STATE: Initializing Docs Agent.")
docs_agent = DocsAgent()
ai_console.print("\nHello! I'm PaLM 2.\n")

# First question (for quick testing)
question = "What are some differences between apples and oranges?"

# User input loop
while True:
    # Get context from the vector database
    result = docs_agent.query_vector_store(question)
    context = result.fetch_formatted(Format.CONTEXT)
    # Add instruction to the context
    context_with_prefix = docs_agent.add_instruction_to_context(context)
    # Print the context
    ai_console.print(Panel.fit(Markdown("\nContext: " + context_with_prefix)))
    # Get URLs of the context from the vector database
    metadatas = result.fetch_formatted(Format.URL)
    ai_console.print(Panel.fit(Markdown(metadatas)))
    # Print the question
    ai_console.print(Panel.fit("Question: " + question))
    ai_console.print("\nPaLM 2:")
    # Pass the context and question to PaLM 2 (Text)
    response_text = docs_agent.ask_text_model_with_context(context_with_prefix, question)
    ai_console.print("\n[Text answer]:")
    ai_console.print(Panel.fit(Markdown(response_text)))
    # Pass the context and question to PaLM 2 (Chat)
    response_chat = docs_agent.ask_chat_model_with_context(context_with_prefix, question)
    ai_console.print("\n[Chat answer]:")
    ai_console.print(Panel.fit(Markdown(response_chat)))
    # Keep asking questions to PaLM 2
    ai_console.print("\n######## Ask PaLM 2 ########")
    question = input("How can I help?\n> ")
    ai_console.print("")
    if question.startswith("exit"):
        ai_console.print("Goodbye!")
        sys.exit()
