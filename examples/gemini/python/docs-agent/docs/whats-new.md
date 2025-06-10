# What's new in Docs Agent


## April 2025

* **Milestone: Introduced Tool Usage through MCP**
* Added the new `agent tools` CLI command, enabling interaction with the model
  using external tools.
* Leverages the Model Context Protocol (MCP) for tool discovery and execution.
  Define MCP servers in `config.yaml`.
* This allows the agent to use configured tools.
* Manages tools through the `ToolManager` and `MCPService`.

## April 2024

* **Focus: Feature enhancements and usability improvements**
* Expanded CLI functionality with options for managing online corpora and interacting with files.
* Addressed bug fixes and performed code refactoring for improved stability and maintainability.
* Added a new chat app template specifically designed for the **Gemini 1.5 model**.
* Updated GenAI SDK version to `0.5.0`.
* Introduced a splitter for handling of Fuchsia’s FIDL protocol files in the preprocessing stage.

## March 2024

* **Milestone: Introduction of the Docs Agent CLI**
* Added the `tellme` command for direct interaction with Gemini from a Linux terminal.
* Expanded CLI options for corpora management, including creation, deletion, and permission control.
* Enhanced the chat app UI with a "loading" animation and probability-based response pre-screening.
* Enabled displaying more URLs retrieved from the AQA model in the widget mode.
* Added support for including URLs as metadata when uploading chunks to online corpora.

## February 2024

* **Focus: Refining AQA model integration**
* Improved UI rendering of AQA model responses, especially for code segments.
* Addressed bug fixes to handle unexpected AQA model responses.
* Generated related questions by using retrieved context instead of a user question.
* Started logging `answerable_probability` for AQA model responses.

## January 2024

* **Milestone: Docs Agent uses AQA model and Semantric Retrieval API**
* Started Logs Agent experiments
* Benchmark score up ~2.5% with enhancements to embeddings

## December 2023

* **Milestone: Docs Agent uses Gemini model.**
* Prototyping benchmarking: documentation unit tests.
* Steady traffic since launch, 861 weekly views, December 14.

## November 2023

* Experimented with context reconstruction.
* Docs Agent now parsing code blocks.
* Added new condition using a mixture of best practices to improve answers.
* Added chunking by tokenization.

## October 2023

* **Milestone: Docs Agent supports Google docs, PDFs, and emails.**
* Drafted Docs Agent security strategy.
* Drafted Docs Agent + Talking Character design doc.
* Top of the charts for generative AI samples: 1216 weekly views.
* Build for AI series: 16000 watches.

## September 2023

* First open-source feature request: support Google docs.
* **Milestone: Docs Agent published!**
* Recorded Build for AI series.
* Implemented hashing to check existing entries and only generate embeddings for
  new or updated content.

## August 2023

* Docs Agent demo running with Flutter docs.
* Docs Agent gets necessary approvals for open-sourcing.
* Special mention: Docs Agent gets it's name.
* Added support to read frontmatter, starting with titles.

## July 2023

* Light month, as many of us took vacations :).
* Created `opensource` branch on internal repo for open-source pushes.
* Reviewed video script for Build for AI series.
* Security: meeting on using open-source content and security issues.

## June 2023

* Drafted Docs Agent Readme.
* Created internal repo to set up infrastructure for open-source pushes.
* First internal customer tried Docs Agent.
* Compiled list of Todos to open-source Docs Agent.

## May 2023

* Switched from chunking content based on 3000-char limit to chunking by
  headings.
* Cleaned up Markdown processing issues.
* Privacy: clarified in UI how we are using data.
* Attempted to create a chat bot for Google chat.
* Added database admin console.
* Partially implemented rewrite option.
* Added related questions.

## April 2023

* Created new UI for chat app: Flask app.
* Added 'fact-checking' section.
* **Milestone: started the Docs Agent open-source project.**
