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
import asyncio
import click
import logging
import traceback
import os

from docs_agent.agents.docs_agent import DocsAgent
from docs_agent.utilities.config import return_config_and_product

# Define history file path
history_file = "/tmp/docs_agent_responses"

# --- Structured History Constants ---
# This header will be at the top of the history file and part of the LLM prompt with history.
HISTORY_FILE_AND_PROMPT_HEADER = (
    "## Conversation History (for context) ##\n"
    "The following is a log of previous questions and responses.\n"
    "Use this information as context to understand the current request.\n"
    "------------------------------------------------------------\n"
)

# This footer will be at the bottom of the history file and part of the LLM prompt with history.
HISTORY_FILE_AND_PROMPT_FOOTER = (
    "------------------------------------------------------------\n"
    "## End of Conversation History ##\n"
)

# This prefix is added *only* to the LLM prompt (not saved in the file)
# when history is present, before the new user question.
LLM_PROMPT_NEW_REQUEST_PREFIX = (
    "\n## New User Request ##\n"
)
# --- End Structured History Constants ---

async def run_agent_processing(
    prompt: str,
    agent: DocsAgent,
    verbose: bool = False,
):
    """
    Main execution logic for the Agent using tools loop.

    Args:
        prompt (str): The prompt to send to the agent including context.
        agent (DocsAgent): The initialized DocsAgent instance.
        verbose (bool): Enable verbose logging.

    Returns:
        str: The final output text from the agent or an error message.
    """
    final_result_text = "[MCP Service Initialization Failed]"
    try:
        logging.info("Starting agent processing loop...")
        final_result_text = await agent.process_prompt_with_tools(
            prompt=prompt, verbose=verbose
        )
    except ConnectionRefusedError as e:
        logging.error("MCP Connection Error: Could not connect to the server.")
        logging.error(f"Details: {e}")
        final_result_text = "[Connect ERR: Server refused connection]"
    except FileNotFoundError as e:
        logging.error("MCP Stdio Error: Command or script not found.")
        logging.error(f"Details: {e}")
        final_result_text = "[Stdio ERR: Command not found]"
    except Exception as e:
        logging.critical(
            f"Unexpected runtime error during MCP session: {type(e).__name__}"
        )
        logging.critical(f"Details: {e}")
        if verbose:
            traceback.print_exc()
        final_result_text = f"[Runtime ERR: {type(e).__name__}: {e}]"

    return final_result_text


# Define the main click group
@click.group(invoke_without_command=True)
@click.pass_context
def cli_tools(ctx):
    """Docs Agent tools using Tools."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli_tools.command(name="tools")
@click.argument("words", nargs=-1)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output, including full tool details and tracebacks.",
)
@click.option(
    "--new",
    is_flag=True,
    help="Start a new session.",
)
@click.option(
    "--cont",
    is_flag=True,
    help="Use the previous responses in the session as context.",
)
@click.pass_context
def run_agent_command(ctx, words: str, verbose: bool, new: bool, cont: bool):
    """Runs the Docs Agent with the given prompt using Tools.

    \b
    Args:
        words: The initial prompt to send to the agent.
        verbose: Enable verbose logging.
        new: Start a new session.
        cont: Continue the existing session.
    """
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.info("Verbose mode enabled.")
    else:
        logging.getLogger().setLevel(logging.WARNING)
    initial_prompt_str = " ".join(words)
    if not initial_prompt_str:
        click.echo("Error: Prompt cannot be empty.", err=True)
        ctx.exit(1)
    # Log raw prompt before context handling
    logging.info(f"Starting Docs Agent with Tools. Raw Prompt: {initial_prompt_str}")

    # --- History / Context Handling ---
    llm_history_context_block = ""  # HEADER + Parsed QAs + FOOTER for LLM
    parsed_qa_content_from_history_file = "" # Just the Q/A part from a structured file
    legacy_unstructured_content_to_migrate = "" # Full content of an old-format file

    if cont:
        if new:
            click.echo(
                "Warning: Both --new and --cont flags specified. --new takes precedence, history will be cleared for this session's start.",
                err=True,
            )
        else:
            try:
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8") as f:
                        full_file_content = f.read()

                    if not full_file_content.strip(): # File is empty or whitespace
                        logging.info(f"History file {history_file} is empty. No context to load.")
                    else:
                        header_start_idx = full_file_content.find(HISTORY_FILE_AND_PROMPT_HEADER)
                        footer_start_idx = -1
                        if header_start_idx != -1:
                            footer_start_idx = full_file_content.find(
                                HISTORY_FILE_AND_PROMPT_FOOTER,
                                header_start_idx + len(HISTORY_FILE_AND_PROMPT_HEADER)
                            )

                        if header_start_idx != -1 and footer_start_idx != -1:
                            # Successfully found structured history
                            qa_content_start_offset = header_start_idx + len(HISTORY_FILE_AND_PROMPT_HEADER)
                            parsed_qa_content_from_history_file = full_file_content[qa_content_start_offset:footer_start_idx]

                            llm_history_context_block = (
                                HISTORY_FILE_AND_PROMPT_HEADER +
                                parsed_qa_content_from_history_file +
                                HISTORY_FILE_AND_PROMPT_FOOTER
                            )
                            logging.info(
                                f"Successfully parsed {len(parsed_qa_content_from_history_file)} chars of Q/A content from structured history: {history_file}"
                            )
                        else:
                            # File exists but is not in the new structured format
                            click.echo(
                                f"Warning: History file {history_file} is not in the expected structured format. "
                                "No prior context will be used for this query. The file will be converted to the new format upon saving.",
                                err=True,
                            )
                            logging.warning(
                                f"History file {history_file} found but not in structured format. Storing its content for migration on save. Header found: {header_start_idx!=-1}, Footer found: {footer_start_idx!=-1} (after header)."
                            )
                            legacy_unstructured_content_to_migrate = full_file_content
            except IOError as e:
                click.echo(f"Warning: Could not read history file {history_file}: {e}", err=True)

    # Construct the prompt for the agent
    if llm_history_context_block: # If --cont successfully loaded and parsed structured history
        prompt_with_context = (
            llm_history_context_block +
            LLM_PROMPT_NEW_REQUEST_PREFIX +
            initial_prompt_str
        )
        logging.info("Using structured history as context for the prompt.")
    else:
        prompt_with_context = initial_prompt_str # No history or failed to parse structured

    logging.info(f"Final prompt for agent (with context if any):\n{prompt_with_context}")
    # --- End History / Context Handling ---

    logging.info("Starting Docs Agent with Tools...")
    # Log the original prompt, not the one with context for clarity here
    logging.info(f"Original Prompt: {initial_prompt_str}")

    # Define the async part to be run
    async def _main():
        # Load config and initialize Agent
        _loaded_config, product_config = return_config_and_product()
        if not product_config or not product_config.products:
            logging.critical("Failed to load product configuration.")
            click.echo(
                "\n[Config Load ERR: No products found]", err=True
            )
            ctx.exit(1)

        try:
            # Uses products[0] for now
            agent = DocsAgent(
                config=product_config.products[0],
                init_chroma=False,
                init_semantic=False,
            )
            if agent.tool_manager:
                loaded_tool_names = [
                    service.name
                    for service in agent.tool_manager.tool_services
                    if hasattr(service, "name")
                    ]
                click.echo(f"\nUsing tools: {loaded_tool_names}\n")
        except Exception as e:
            logging.critical(f"Failed to initialize DocsAgent: {e}")
            if verbose:
                traceback.print_exc()
            click.echo(f"\n[Agent Init ERR: {e}]", err=True)
            ctx.exit(1)
        final_output = "[Initialization Error]"
        try:
            # Call the async processing function
            final_output = await run_agent_processing(
                prompt=prompt_with_context,
                agent=agent,
                verbose=verbose,
            )
        except Exception as e:
            # Catch errors during the agent processing run
            logging.critical(
                f"Unexpected Error in agent processing: {type(e).__name__}: {e}"
            )
            final_output = f"[Processing ERR: {type(e).__name__}]"
            if verbose:
                traceback.print_exc()
            click.echo(f"Error during processing: {final_output}", err=True)

        return final_output

    # Run the async main function using asyncio.run()
    final_output_result = "[Async Execution Error]"
    try:
        final_output_result = asyncio.run(_main())
    except Exception as e:
        logging.critical(f"Error running asyncio main: {e}")
        final_output_result = f"[Asyncio Run ERR: {e}]"
        if verbose:
            traceback.print_exc()
        click.echo(f"Error during async execution: {final_output_result}", err=True)
        ctx.exit(1)

    # --- Write History ---
    if not (final_output_result.startswith("[") and final_output_result.endswith("]")):
        new_qa_interaction_entry = f"QUESTION:\n{initial_prompt_str}\n\nRESPONSE:\n{final_output_result}\n\n"

        current_qa_block_for_saving = ""
        if new:
            current_qa_block_for_saving = new_qa_interaction_entry
            logging.info(f"Starting new history Q/A block (due to --new flag).")
        else:
            if parsed_qa_content_from_history_file: # Successfully read structured history
                current_qa_block_for_saving = parsed_qa_content_from_history_file + new_qa_interaction_entry
                logging.info(f"Appending new interaction to existing structured Q/A block.")
            elif legacy_unstructured_content_to_migrate: # Migrating old format
                # Ensure there's a newline before appending the new Q/A if legacy content doesn't end with one
                separator = "\n" if legacy_unstructured_content_to_migrate.strip() and not legacy_unstructured_content_to_migrate.endswith("\n") else ""
                current_qa_block_for_saving = legacy_unstructured_content_to_migrate.strip() + separator + "\n" + new_qa_interaction_entry
                logging.info(f"Converting legacy history content and appending new interaction for saving.")
            else: # No prior history or file was empty
                current_qa_block_for_saving = new_qa_interaction_entry
                logging.info(f"Starting new Q/A block (no prior history or history file was empty).")

        history_content_to_write = (
            HISTORY_FILE_AND_PROMPT_HEADER +
            current_qa_block_for_saving +
            HISTORY_FILE_AND_PROMPT_FOOTER
        )

        try:
            with open(history_file, "w", encoding="utf-8") as f: # Always "w" to write full structured content
                f.write(history_content_to_write)
            logging.info(f"Successfully wrote/updated history file in structured format: {history_file}")
        except IOError as e:
            click.echo(f"Warning: Could not write to history file {history_file}: {e}", err=True)
    else:
        logging.info(f"Skipping history write due to agent output indicating an error: {final_output_result}")
    # --- End Write History ---

    # Print the final result
    click.echo(f"\n{final_output_result}")


cli = click.CommandCollection(
    sources=[cli_tools],
    help="Docs Agent LLM interactions using tools.",
)

if __name__ == "__main__":
    cli()
