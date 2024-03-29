# Set up Docs Agent CLI

This guide provides instructions on setting up Docs Agent's command-line
interface (CLI) that allows you to ask questions from anywhere in a terminal.

Using Docs Agent, you can configure your host machine's environment to make
the `gemini` command run from anywhere in your terminal. The `gemini` command
(which is an `alias` to Docs Agent's `agent tellme` command) reads a question
from the arguments, asks the [Gemini AQA][gemini-aqa] model, and prints its
response in the terminal.

The example below shows that a user can run the `gemini` command directly
from a terminal:

```
user@user01:~$ gemini does Flutter support material design 3?

As of the Flutter 3.16 release, Material 3 is enabled by default.

To verify this information, see:

 • https://docs.flutter.dev/ui/design/material/index#more-information

user@user01:~$
```

In this setup guide, Docs Agent's AQA model is configured to use an example
online corpus. However, using the tools available in the Docs Agent project,
you can [create and populate a new corpus][populate-corpus] with your own
documents and adjust your Docs Agent configuration to use that corpus
instead – you can also [share the corpus][share-corpus] with other members
in your team.

## 1. Prerequisites

Setting up Docs Agent requires the following prerequisite items:

- A Linux host machine

- A [Google Cloud][google-cloud] project with the setup below:

  - An API key enabled with the Generative Language API (that is,
    the [Gemini API][genai-doc-site])

  - (**Optional**) [Authenticated OAuth client credentials][oauth-client]
    stored on the host machine

## 2 Update your host machine's environment

1. Update the Linux package repositories on the host machine:

   ```posix-terminal
   sudo apt update
   ```

2. Install the following dependencies:

   ```posix-terminal
   sudo apt install git pip python3-venv
   ```

3. Install `poetry`:

   ```posix-terminal
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   **Important**: Make sure that `$HOME/.local/bin` is in your `PATH` variable
   (for example, `export PATH=$PATH:~/.local/bin`).

4. Set the following environment variable:

   ```posix-terminal
   export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
   ```

   This is a [known issue][poetry-known-issue] in `poetry`.

5. Set the Google API key as a environment variable:

   ```
   export GOOGLE_API_KEY=<YOUR_API_KEY_HERE>
   ```

   Replace `<YOUR_API_KEY_HERE>` with the API key to the
   [Gemini API][genai-doc-site].

   **Tip**: To avoid repeating these `export` lines, add them to your
   `$HOME/.bashrc` file.

## 3. Authorize credentials for Docs Agent

**Note**: This step may not be necessary if you already have OAuth client
credentials (via `gcloud`) stored on your host machine.

1. Download the `client_secret.json` file from your
   [Google Cloud project][authorize-credentials].

2. Copy the `client_secret.json` file to your host machine.

3. To authenticate credentials, run the following command in the directory of
   the host machine where the `client_secret.json` file is located:

   ```
   gcloud auth application-default login --client-id-file=client_secret.json --scopes='https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language.retriever'
   ```

   This command opens a browser and asks to log in using your Google account.

   **Note**: If the `gcloud` command doesn’t exist, install the Google Cloud SDK
   on your host machine: `sudo apt install google-cloud-sdk`

4. Follow the instructions on the browser and click **Allow** to authenticate.

   This saves the authenticated credentials for Docs Agent
   (`application_default_credentials.json`) in the `$HOME/.config/gcloud/`
   directory of your host machine.

## 4. Clone the Docs Agent project repository

**Note**: This guide assumes that you're creating a new project directory
from your `$HOME` directory.

1. Clone the following internal repo:

   ```posix-terminal
   git clone sso://doc-llm-internal/docs-agent
   ```

2. Go to the project directory:

   ```posix-terminal
   cd docs-agent
   ```

3. Install dependencies using `poetry`:

   ```posix-terminal
   poetry install
   ```

   This may take some time to complete.

## 5. Set up an alias to the gemini command

**Note**: If your Docs Agent project is not cloned in the `$HOME` directory,
you need to edit the `tellme.sh` script in your `docs-agent` project directory.

Update your shell environment so that the `gemini` command can be run
from anywhere in the terminal:

1. (**Optional**) Open the `tellme.sh` file using a text editor, for example:

   ```sh
   nano tellme.sh
   ```

   If necessary, adjust the path (`$HOME/docs-agent`) to match your
   `docs-agent` project directory on the host machine:

   ```
   #!/bin/bash

   # Check if the POETRY_ACTIVE environment variable is set
   if [ -z "$POETRY_ACTIVE" ]; then
       cd $HOME/docs-agent && poetry run agent tellme $@
   else
       agent tellme $@
   fi
   ```

   Save the file and close text editor.

2. Add the following `alias` line to your `$HOME/.bashrc` file:

   ```
   alias gemini='$HOME/docs-agent/tellme.sh'
   ```

   Similarly, if necessary, you need to adjust the path
  (`$HOME/docs-agent`) to match your the `docs-agent` project directory
   on the host machine.

3. Update your environment:

   ```sh
   source ~/.bashrc
   ```

4. Now you can run the `gemini` command from anywhere in your terminal:

   ```sh
   gemini <QUESTION>
   ```

   For example:

   ```
   user@user01:~/temp$ gemini does flutter support material design 3?
   ```

<!-- Reference links -->

[gemini-aqa]: https://ai.google.dev/docs/semantic_retriever
[populate-corpus]: ../preprocess/README.md
[share-corpus]: https://ai.google.dev/docs/semantic_retriever#share_the_corpus
[google-cloud]: https://console.cloud.google.com/
[oauth-client]: https://ai.google.dev/docs/oauth_quickstart#set-cloud
[authorize-credentials]: https://ai.google.dev/docs/oauth_quickstart#authorize-credentials
[poetry-known-issue]: https://github.com/python-poetry/poetry/issues/1917
[genai-doc-site]: https://ai.google.dev/docs/gemini_api_overview
