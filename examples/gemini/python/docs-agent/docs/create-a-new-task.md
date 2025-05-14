# Create a new Docs Agent task

This guide provides instructions on how to create a new Docs Agent
task file (`.yaml`) for automating a workflow.

## Create a new task

To create a new task in your Docs Agent setup, follow these steps:

1. Go to your Docs Agent directory, for example:

   ```
   cd ~/docs_agent
   ```

2. Go to the `tasks` directory:

   ```
   cd tasks
   ```

3. Open a text editor and create a new `yaml` file, for example:

   ```
   nano my-new-task.yaml
   ```

4. Copy and paste the following task template:

   ```
    tasks:
      - name: "<TASKNAME>"
        model: "models/gemini-1.5-flash"
        description: "<DESCRIPTION>"
        preamble: <”PREAMBLE>”
        steps:
          - prompt: "<PROMPT_1>"
          - prompt: "<PROMPT_2>"
          - prompt: "<PROMPT_3>"
   ```

5. Update the task name (`<TASKNAME>`).
6. (**Optional**) Update the model (see this
   [Gemini model code][model-code]).
7. Update the task description (`<DESCRIPTION>`).
8. (**Optional**) Update the preamble (`<PREAMBLE>`).

   **Note**: The `preamble` field is not required. If it's not used,
   remove the `preamble` field.

9. Update the prompts (`<PROMPT_#>`).
10. (**Optional**) Add more prompts under the `steps` section.
11. Save the file and exit the text editor.
12. To verify that your new task is available, run the following command:

    ```
    agent runtask
    ```

13. Run the new task using the task name:

    ```
    agent runtask --task <TASKNAME>
    ```

    For example:

    ```
    agent runtask --task MyNewExampleTask
    ```

    If your task accepts custom input, you can run it with the
    `--custom_input` field, for example:

    ```
    agent runtask --task MyNewExampleTask --custom_input ~/my_project/my_example_doc.md
    ```

## A minimum task file

The example task below is created using only the **required fields**:

```
tasks:
  - name: "MyExampleTask"
    model: "models/gemini-1.5-flash"
    description: "An agent example that is created using only the required fields for a task."
    steps:
      - prompt: "This is my first prompt."
      - prompt: "This is my second prompt."
      - prompt: "This is my third prompt."
```

A task can have one `prompt` step at a minimum.

For more examples, see the [`tasks`][tasks-dir] directory.

## More examples for steps

This section contains more `prompt` examples and optional fields.

### A standard prompt step

A step that runs the `helpme` command:

```
   steps:
     - prompt: "Revise the PSA email draft above to be more concise and better structured."
```

### A POSIX command step

A step that runs a POSIX command:

```
   steps:
     - prompt: "git --no-pager log --since=2024-10-15"
       function: "posix"
```

**Important**: To run a POSIX command, the `function` field
must be set to `posix`.

### A script step

A step that runs a custom script:

```
   steps:
     - prompt: "extract_image_files.py"
       function: "script"
```

**Important**: To run a custom script, the script must be stored in
the [`scripts`][scripts-dir] directory of the Docs Agent setup.

You can provide a `script` step with a custom input string as
arguments to the script using the `script_input` field, for example:

```
   steps:
      - prompt: "extract_image_files.py"
        function: "script"
        flags:
          script_input: "<INPUT>"
          default_input: "./README.md"
```

This step runs the following commandline:

```sh
$ python3 scripts/extract_image_files.py <INPUT>
```

### A step that reads a file

The `file` flag reads the specified file and added its content
to the prompt's context.

A step that runs the `helpme` command with the `file` flag:

```
   steps:
     - prompt: "Analyze this file to understand the overall structure and key concepts."
       flags:
         file: "/home/user/docs_agent/README.md"
```

A step that runs the `helpme` command with the `file` flag and accepts custom input:

```
   steps:
     - prompt: "Analyze this file to understand the overall structure and key concepts."
       flags:
         file: "<INPUT>"
         default_input: "/home/user/docs_agent/README.md"
```

When this step is run, the `<INPUT>` string will be replaced with
the value provided in the `--custom_input` field at runtime.

You can also provide multiple files using a list as shown below:

```
    steps:
      - prompt: "Provide a concise, descriptive alt text for this PNG image."
        flags:
          file:
            - "docs/images/apps-script-screenshot-01.png"
            - "docs/images/docs-agent-ui-screenshot-01.png"
            - "docs/images/docs-agent-embeddings-01.png"
```

### A step that reads all files in a directory

The `allfiles` flag reads all the files in the specified directory
and added their content to the prompt's context.

A step that runs the `helpme` command with the `allfiles` flag:

```
   steps:
     - prompt: "Analyze the files in this directory to understand the overall structure and key concepts."
       flags:
         allfiles: "/home/user/docs_agent/docs"
```

A step that runs the `helpme` command with the `allfiles` flag
and accepts custom input:

```
   steps:
     - prompt: "Analyze the files in this directory to understand the overall structure and key concepts."
       flags:
         allfiles: "<INPUT>"
         default_input: "/home/user/docs_agent/docs"
```

When this step is run, the `<INPUT>` string will be replaced with
the value provided in the `--custom_input` field at runtime.

### A step that reads each file in a directory

Similar to a `foreach` loop, the `perfile` flag reads each file in
the specified directory and added the file's content to the prompt's
context. For instance, if there are 5 files in the input directory,
the same prompt will run 5 times using each file's content as context.

A step that runs the `helpme` command with the `perfile` flag:

```
   steps:
     - prompt: "Analyze this file to understand the overall structure and key concepts."
       flags:
         perfile: "/home/user/docs_agent/docs"
```

A step that runs the `helpme` command with the `perfile` flag
and accepts custom input:

```
   steps:
     - prompt: "Analyze this file to understand the overall structure and key concepts."
       flags:
         perfile: "<INPUT>"
         default_input: "/home/user/docs_agent/docs"
```

When this step is run, the `<INPUT>` string will be replaced with
the value provided in the `--custom_input` field at runtime.

### A step that reads a list of file names from an input file

Similar to the `perfile` flag, the `list_file` flag reads an input
file that contains a list of filenames and applies the prompt to
each file in the list:

```
   steps:
     - prompt: "Write an alt text string for this image."
       flags:
         list_file: "out/mylist.txt"
```

where the `out/mylist.txt` file contains a list of file names in
plain text as shown below:

```none
$ cat out/mylist.txt
docs/images/apps-script-screenshot-01.png
docs/images/docs-agent-ui-screenshot-01.png
docs/images/docs-agent-embeddings-01.png
```

### A step with the name field

A step that runs the `helpme` command and the `name` field
(which is for display only) is provided:

```
   steps:
     - name: "Revise the PSA email"
       prompt: "Revise the PSA email draft above to be more concise and better structured."
```

### A step with the function field

A step that runs the `helpme` command that explicitly mentions
which `function` to use:

```
   steps:
     - prompt: "Revise the PSA email draft above to be more concise and better structured."
       function: "helpme"
```

Without the `function` field, the prompt is set to use the `helpme` command by default.

### A question step

A step that runs the `tellme` command:

```
   steps:
     - prompt: "Does Flutter support Material Design 3?"
       function: "tellme"
```

Using the `tellme` command requires **a vector database setup**.

<!-- Referene links -->

[model-code]: https://ai.google.dev/gemini-api/docs/models/gemini
[tasks-dir]: ../tasks
[scripts-dir]: ../scripts
