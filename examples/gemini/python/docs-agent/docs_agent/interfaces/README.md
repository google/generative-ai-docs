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
   sudo apt install git pipx python3-venv
   ```

3. Install `poetry`:

   ```posix-terminal
   pipx install poetry
   ```

4. To add `$HOME/.local/bin` to your `PATH` variable, run the following
   command:

   ```posix-terminal
   pipx ensurepath
   ```

5. To set the Google API key as a environment variable, add the following
   line to your `$HOME/.bashrc` file:

   ```
   export GOOGLE_API_KEY=<YOUR_API_KEY_HERE>
   ```

   Replace `<YOUR_API_KEY_HERE>` with the API key to the
   [Gemini API][genai-doc-site].

6. Update your environment:

   ```posix-termainl
   source ~/.bashrc
   ```

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

## 4. Clone the Docs Agent project

**Note**: This guide assumes that you're creating a new project directory
from your `$HOME` directory.

1. Clone the following repo:

   ```posix-terminal
   git clone https://github.com/google/generative-ai-docs.git
   ```

2. Go to the Docs Agent project directory:

   ```posix-terminal
   cd generative-ai-docs/examples/gemini/python/docs-agent
   ```

3. Install dependencies using `poetry`:

   ```posix-terminal
   poetry install
   ```

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

## Appendices

### Set up your terminal to run the helpme command

**Note**: This is an experimental setup.

This new feature allows you to freely navigate a codebase setup in your
terminal and asks Gemini to perform various tasks while automatically
referencing the output you see in your terminal.

Similar to the `agent tellme` command, the `agent helpme` command allows you to
ask a question to Gemini directly from your terminal. However, unlike
the `tellme` command, the `helpme` command uses the Gemini Pro model
and doesn't depend on an online corpus to retrieve relevant context.
Instead, this `helpme` setup can read directly from the output of your terminal
(that is, the last 150 lines at the moment) and automatically adds it as context
to your prompt.

These tasks include, but not limited to:

- Rewrite `README` file to be instructional and linear.
- Rewrite `README` file to be more concise and better structured.
- Format `README` to collect reference links at the bottom.
- Write comments for a C++ source file.

**Note**: Since this setup uses the Gemini Pro model, setting up OAuth on your
host machine is **not required**.

To set up this `helpme` command in your terminal, do the following:

1. (**Optional**) Open the `helpme.sh` file using a text editor, for example:

   ```sh
   nano helpme.sh
   ```

   If necessary, adjust the path (`$HOME/docs-agent`) to match your
   `docs-agent` project directory on the host machine:

   ```
   #!/bin/bash

   # Check if the POETRY_ACTIVE environment variable is set
   if [ -z "$POETRY_ACTIVE" ]; then
       cd $HOME/docs-agent && poetry run agent helpme $@
   else
       agent helpme $@
   fi
   ```

   Save the file and close text editor.

2. Add the following `alias` lines to your `$HOME/.bashrc` file:

   ```
   alias gemini-pro='$HOME/docs-agent/helpme.sh'
   alias start_agent='script -f -o 200MiB -O /tmp/docs_agent_console_input'
   alias stop_agent='exit'
   ```

   Similarly, if necessary, you need to adjust the path
  (`$HOME/docs-agent`) to match your the `docs-agent` project directory
   on the host machine.

3. Update your environment:

   ```sh
   source ~/.bashrc
   ```

4. When you are ready to let Docs Agent to read output from your terminal,
   run the following command:

   ```sh
   start_agent
   ```

   **Note**: To stop this process, run `stop_agent`.

5. Navigate to a directory in your terminal and use the `cat` command
   (or `head` or `tail`) to print the content of a file to your terminal.

   (In fact, you can run any command that prints output to the terminal.)

   For example:

   ```
   user@user01:~/my-example-project$ cat test.cc
   <prints the test.cc file here>
   ```

6. To use the latest output from your terminal, run the `gemini-pro` command
   immediately after the output:

   ```sh
   gemini-pro <REQUEST>
   ```

   For example:

   ```
   user@user01:~/my-example-project$ cat test.cc
   <prints the test.cc file here>
   user@user01:~/my-example-project$ gemini-pro could you help me write comments for this C++ file above?
   ```

<!-- Reference links -->

[gemini-aqa]: https://ai.google.dev/docs/semantic_retriever
[populate-corpus]: ../preprocess/README.md
[share-corpus]: https://ai.google.dev/docs/semantic_retriever#share_the_corpus
[google-cloud]: https://console.cloud.google.com/
[oauth-client]: https://ai.google.dev/docs/oauth_quickstart#set-cloud
[authorize-credentials]: https://ai.google.dev/docs/oauth_quickstart#authorize-credentials
[genai-doc-site]: https://ai.google.dev/docs/gemini_api_overview
