# Docs Agent CLI reference

This page provides a list of the Docs Agent command lines and their usages
and examples.

The Docs Agent CLI helps developers to manage the Docs Agent project and
interact with language models. It can handle various tasks such as
processing documents, populating vector databases, launching the chatbot,
running benchmark test, sending prompts to language models, and more.

**Important**: All `agent` commands need to run in the `poetry shell`
environment.

## Processing documents

### Chunk Markdown files into small text chunks

The command below splits Markdown files (and other source files) into small
chunks of plain text files:

```sh
agent chunk
```

### Populate a vector database using text chunks

The command below populates a vector database using plain text files (created
by running the `agent chunk` command):

```sh
agent populate
```

### Populate a vector database and delete stale text chunks

The command below deletes stale entries in the existing vector database
before populating it with the new text chunks:

```sh
agent populate --enable_delete_chunks
```

### Show the Docs Agent configuration

The command below prints all the fields and values in the current
[`config.yaml`][config-yaml] file:

```sh
agent show-config
```

### Clean up the Docs Agent development environment

The command below deletes development databases specified in the
`config.yaml` file:

```sh
agent cleanup-dev
```

### Write logs to a CSV file

The command below writes the summaries of all captured debugging information
(in the `logs/debugs` directory) to  a `.csv` file:

```sh
agent write-logs-to-csv
```

## Launching the chatbot web app

### Launch the Docs Agent web app

The command below launches Docs Agent's Flask-based chatbot web application:

```sh
agent chatbot
```

### Launch the Docs Agent web app using a different port

The command below launches the Docs Agent web app to run on port 5005:

```sh
agent chatbot --port 5005
```

### Launch the Docs Agent web app as a widget

The command below launches the Docs Agent web app to use
a widget-friendly template:

```sh
agent chatbot --app_mode widget
```

### Launch the Docs Agent web app in full mode

The command below launches the Docs Agent web app to use
a special template that uses three Gemini models (AQA, Gemini 1.5,
and Gemini 1.0):

```sh
agent chatbot --app_mode full
```

### Launch the Docs Agent web app with a log view enabled

The command below launches the Docs Agent web app while enabling
a log view page (which is accessible at `<APP_URL>/logs`):

```sh
agent chatbot --enable_show_logs
```

## Running benchmark test

### Run the Docs Agent benchmark test

The command below runs benchmark test using the questions and answers listed
in the [`benchmarks.yaml`][benchmarks-yaml] file:

```sh
agent benchmark
```

## Interacting with language models

### Ask a question

The command below reads a question from the arguments, asks the Gemini model,
and prints its response:

```sh
agent tellme <QUESTION>
```

Replace `QUESTION` with a question written in plain English, for example:

```sh
agent tellme does flutter support material design 3?
```

**Note**: This `agent tellme` command is used to set up the `gemini` command
in the [Set up Docs Agent CLI][set-up-docs-agent-cli] guide.

### Ask a question to a specific product

The command below enables you to ask a question to a specific product in your
Docs Agent setup:

```sh
agent tellme <QUESTION> --product <PRODUCT>
```

The example below asks the question to the `Flutter` product in your
Docs Agent setup:

```sh
agent tellme which modules are available? --product=Flutter
```

You may also specify multiple products, for example:

```sh
agent tellme which modules are available? --product=Flutter --product=Angular --product=Android
```

### Ask for advice

The command below reads a request and a filename from the arguments,
asks the Gemini model, and prints its response:

```sh
agent helpme <REQUEST> --file <PATH_TO_FILE>
```

Replace `REQUEST` with a prompt and `PATH_TO_FILE` with a file's
absolute or relative path, for example:

```sh
agent helpme write comments for this C++ file? --file ../my-project/test.cc
```

You can also provide multiple files for the same request, for example:

```sh
agent helpme summarize the content of this file? --file ../my-project/example_01.md --file ../my-project/example_02.md --file ~/my-new-project/example.md
```

### Ask for advice using RAG

The command below uses a local or online vector database (specified in
the `config.yaml` file) to retrieve relevant context for the request:

```sh
agent helpme <REQUEST> --file <PATH_TO_FILE> --rag
```

### Ask for advice in a session

The command below starts a new session (`--new`), which tracks responses,
before running the `agent helpme` command:

```sh
agent helpme <REQUEST> --file <PATH_TO_FILE> --new
```

For example:

```sh
agent helpme write a draft of all features found in this README file? --file ./README.md --new
```

After starting a session, use the `--cont` flag to include the previous
responses as context to the request:

```sh
agent helpme <REQUEST> --cont
```

For example:

```sh
agent helpme write a concept doc that delves into more details of these features? --cont
```

### Print the context in the current session

The command below prints the questions, files, and responses that
are being used as context in the current session:

```sh
agent show-session
```

### Ask the model to perform the request to each file in a directory

The command below applies the request to each file found in the
specified directory:

```sh
agent helpme <REQUEST> --perfile <PATH_TO_DIRECTORY>
```

For example:

```sh
agent helpme explain what this file does? --perfile ~/my-project --new
```

### Ask the model to include all files in a directory as context

The command below includes all files found in the specified directory
as context to the request:

```sh
agent helpme <REQUEST> --allfiles <PATH_TO_DIRECTORY>
```

For example:

```sh
agent helpme write a concept doc covering all features in this project? --allfiles ~/my-project --new
```

### Ask the model to read a list of file names from an input file

Similar to the `--perfile` flag, the command below reads the input
file that contains a list of filenames and applies the request to
each file in the list:

```sh
agent helpme <REQUEST> --list_file <PATH_TO_FILE>
```

For example:

```sh
agent helpme write an alt text string for this image? --list_file ./mylist.txt
```

where the `mylist.txt` file contains a list of file names in plain text
as shown below:

```none
$ cat mylist.txt
docs/images/apps-script-screenshot-01.png
docs/images/docs-agent-ui-screenshot-01.png
docs/images/docs-agent-embeddings-01.png
```

### Ask the model to print the output in JSON

The command below prints the output from the model in JSON format:

```sh
agent helpme <REQUEST> --response_type json
```

For example:

```sh
agent helpme how do I cook pasta? --response_type json
```

### Ask the model to run a pre-defined chain of prompts

The command below runs a task (a sequence of prompts) defined in
a `.yaml` file stored in the [`tasks`][tasks-dir] directory:

```sh
agent runtask --task <TASK>
```

For example:

```sh
agent runtask --task DraftReleaseNotes
```

### View the list of available Docs Agent tasks

To see the list of all tasks available in your project, run
`agent runtask` without any arguments:

```sh
agent runtask
```

### Ask the model to run a task using custom input

If a task script has a `<INPUT>` placeholder, you can provide
a custom input string to the task:

```sh
agent runtask --task <TASK> --custom_input <INPUT_STRING>
```

For example:

```sh
agent runtask --task IndexPageGenerator --custom_input ~/my_example/docs/development/
```

### Ask the model to print the output in plain text

By default, the `agent runtask` command uses Python's Rich console
to format its output. You can disable it by using the `--plaintext`
flag:

```sh
agent runtask --task <TASK> --plaintext
```

For example:

```sh
agent runtask --task DraftReleaseNotes --plaintext
```

## Managing online corpora

### List all existing online corpora

The command below prints the list of all existing online corpora created
using the [Semantic Retrieval API][semantic-api]:

```sh
agent list-corpora
```

### Share an online corpora with a user

The command below enables `user01@gmail.com` to read text chunks stored in
`corpora/example01`:

```sh
agent share-corpus --name corpora/example01 --user user01@gmail.com --role READER
```

The command below enables `user01@gmail.com` to read and write to
`corpora/example01`:

```sh
agent share-corpus --name corpora/example01 --user user01@gmail.com --role WRITER
```

### Share an online corpora with everyone

The command below enables `EVERYONE` to read text chunks stored in
`corpora/example01`:

```sh
agent open-corpus --name corpora/example01
```

### Remove a user permission from an online corpora

The command below remove an existing user permission set in `corpora/example01`:

```sh
agent remove-corpus-permission --name corpora/example01/permissions/123456789123456789
```

### Delete an online corpora

The command below deletes an online corpus:

```sh
agent delete-corpus --name corpora/example01
```

### Interact with the model using external tools

The command below sends your prompt to the Gemini model and allows the model to
use configured external tools (through MCP servers defined in `config.yaml`) to
fulfill the request.

Note: You can use a `-v` flag to enable verbose mode to see the tool execution.

```sh
agent tools <PROMPT>
```

<!-- Reference links -->

[config-yaml]: ../config.yaml
[benchmarks-yaml]: ../docs_agent/benchmarks/benchmarks.yaml
[set-up-docs-agent-cli]: ../docs_agent/interfaces/README.md
[semantic-api]: https://ai.google.dev/docs/semantic_retriever
[tasks-dir]: ../tasks
