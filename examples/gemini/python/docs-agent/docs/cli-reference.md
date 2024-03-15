# Docs Agent CLI reference

This page provides a list of the Docs Agent command lines and their usages
and examples.

**Important**: All `agent` commands in this page need to run in the
`poetry shell` environment.

## Processing of Markdown files

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

### Show the Docs Agent configuration

The command below prints all the fields and values in the current
[`config.yaml`][config-yaml] file:

```sh
agent show-config
```

## Docs Agent chatbot web app

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

## Docs Agent benchmark test

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

## Online corpus management

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

<!-- Reference links -->

[config-yaml]: ../config.yaml
[benchmarks-yaml]: ../docs_agent/benchmarks/benchmarks.yaml
[set-up-docs-agent-cli]: ../docs_agent/interfaces/README.md
[semantic-api]: https://ai.google.dev/docs/semantic_retriever
