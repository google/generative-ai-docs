# Convert Google Docs, PDF, and Gmail to Markdown files

The collection of scripts in this `apps_script` directory allows you to convert
the contents of Google Drive folders and Gmail to Markdown files that are
compatible with Docs Agent.

The steps are:

1. [Prepare a Google Drive folder](#1_prepare-a-google-driver-folder).
2. [Mount Google Drive on your host machine](#2_mount-google-drive-on-your-host-machine).
3. [Create an Apps Script project](#3_create-an-apps-script-project).
4. [Edit and run main.gs on Apps Script](#4_edit-and-run-main_gs-on-apps-script).
5. [Update config.yaml to include the mounted directory](#5_update-config_yaml-to-include-the-mounted-directory).

## 1. Prepare a Google Drive folder

First, create a new folder in Google Drive and add your Google Docs (which will be
used as source documents to Docs Agent) to the folder.

Do the following:

1. Browser to https://drive.google.com/.
1. Click **+ New** on the top left corner.
1. Click **New folder**.
1. Name your new folder (for example, `my source Google Docs`).
1. To enter the newly created folder, double click the folder.
1. Add (or move) your source Google Docs to this new folder.

## 2. Mount Google Drive on your host machine

Mount your Google Drive to your host machine, so that it becomes easy to access the
folders in Google Drive from your host machine (later in step 5).

There are a variety of methods and tools available online that enable this setup
(for example, see [`google-drive-ocamlfuse`][google-drive-ocamlfuse] for Linux machines).

## 3. Create an Apps Script project

Create a new Apps Script project and copy all the `.gs` scripts in this
`apps_script` directory to your new Apps Script project.

Do the following:

1. Browse to https://script.google.com/.
1. Click **New Project**.
1. At the top of the page, click **Untitled Project** and enter a meaningful
   title (for example, `gDocs to Docs Agent`).
1. Click the **+** icon next to **Files**.
1. Click **Script**.
1. Name the new script to be one of the `.gs` files in this `apps_script` directory
   (for example, `drive_to_markdown`).
1. Copy the content of the `.gs` file to the new script on your Apps Script project.
1. To save, click the "Save project" icon in the toolbar.
1. Repeat the steps until all the `.gs` files are copied to your Apps Script project.
1. Click the **+** icon next to **Services**.
1. Scroll down and click **Drive API**.
1. Click **Add**.

You are now ready to edit the parameters on the `main.gs` file to select a folder
in Google Drive and export emails from Gmail.

![Apps Script project](../docs/images/apps-script-screenshot-01.png)

**Figure 1**. A screenshot of an example Apps Script project.

## 4. Edit and run main.gs on Apps Script

Edit the `main.gs` file on your Apps Script project to select which functions
(features) you want to run.

Do the following:

1. Browse to your project on https://script.google.com/.

1. Open the `main.gs` file.

1. In the `main` function, comment out any functions that you don't want to run
   (see Figure 1):

   * `convertDriveFolderToMDForDocsAgent(folderInput)`: This function converts
     the contents of a Google Drive folder to Markdown files (currently only Google
     Docs and PDF). Make sure to specify a valid Google Drive folder in the `folderInput`
     variable. Use the name of the folder created in **step 1** above, for example:

     ```
     var folderInput = "my source Google Docs"
     function main() {
       convertDriveFolderToMDForDocsAgent(folderInput);
       //exportEmailsToMarkdown(SEARCH_QUERY, folderOutput);
     }
     ```

   * `exportEmailsToMarkdown(SEARCH_QUERY, folderOutput)`: This function converts
     the emails returned from a Gmail search query into Markdown files. Make sure to
     specify a search query in the `SEARCH_QUERY` variable. You can test this search
     query directly in the Gmail search bar. Also, specify an output directory for the
     resulting emails.

1. To save, click the "Save project" icon in the toolbar.

1. Click the "Run" icon in the toolbar.

   When this script runs successfully, the Execution log panel prints output similar
   to the following:

   ```
   9:55:59 PM	Notice	Execution completed
   ```

   Also, the script creates a new folder in your Google Drive and stores the converted
   Markdown files in this folder. The name of this new folder has `-output` as a postfix.
   For example, with the folder name `my source Google Docs`, the name of the new folder
   is `my source Google Docs-output`.

   With Google Drive mounted on your host machine in step 2, you can now directly access
   this folder from the host machine, for example:

   ```
   user@hostname:~/DriveFileStream/My Drive/my source Google Docs-output$ ls
   Copy_of_My_Google_Docs_To_Be_Converted.md
   ```

## 5. Update config.yaml to include the mounted directory

Once you have your Google Drive mounted on the host machine, you can now
specify one of its folders as an input source directory for Docs Agent.

Do the following:

1. In the Docs Agent project, open the [`config.yaml`][config-yaml] file
   with a text editor.

1. Specify your mounted Google Drive folder as an `input` group, for example:

   ```
   input:
   - path: "/usr/local/home/user01/DriveFileStream/My Drive/my source Google Docs-output"
     url_prefix: "docs.google.com"
   ```

   You **must** specify a value to the `url_prefix` field, such as `docs.google.com`.
   Currently this value is used to generate hashes for the content.

1. (**Optional**) Add an additional Google Drive folder for your exported emails,
   for example:

   ```
   input:
   - path: "/usr/local/home/user01/DriveFileStream/My Drive/my source Google Docs-output"
     url_prefix: "docs.google.com"
   - path: "/usr/local/home/user01/DriveFileStream/My Drive/psa-output"
     url_prefix: "mail.google.com"
   ```

1. Save the changes in the `config.yaml` file.

You're all set with a new documentation source for Docs Agent. You can now follow the
instructions in the project's main [`README`][main-readme] file to launch the Docs Agent app.

<!-- Reference links -->

[config-yaml]: ../config.yaml
[main-readme]: ../README.md
[google-drive-ocamlfuse]: https://github.com/astrada/google-drive-ocamlfuse
