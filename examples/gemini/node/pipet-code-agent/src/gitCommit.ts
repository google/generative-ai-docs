/**
 * Copyright 2024 Google LLC
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import * as vscode from "vscode";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { promises } from "dns";

const SYSTEMINSTRUCTION =
  "Generate Git Commit by Git Diff and last commit, Only return commit message.";

export async function generateGitCommit() {
  try {
    const gitExtension = vscode.extensions.getExtension("vscode.git");
    const gitApi = gitExtension?.exports.getAPI(1);
    if (!gitApi.repositories.length) {
      vscode.window.showErrorMessage("no git repositories.");
      return;
    }

    vscode.window.showInformationMessage("Generate Git Diff...");
    const diff = await gitApi.repositories[0].diff();
    const logOptions = { maxEntries: 1 };
    const log = await gitApi.repositories[0].log(logOptions);
    const lastCommit = log[0];
    const lastCommitMessage = `Last commit:\n\n**Hash:** ${lastCommit.hash}\n**Author:** ${lastCommit.author_name} <${lastCommit.author_email}>\n**Date:** ${lastCommit.date}\n**Message:** ${lastCommit.message}`;
    await generateCommit(`${lastCommitMessage}\nDiff: ${diff}`);
  } catch (error) {
    vscode.window.showErrorMessage(`${error}`);
    return;
  }
}

async function generateCommit(diff: string) {
  const modelName = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.textModel", "default");

  // Get API Key from local user configuration
  const apiKey = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.apiKey", "default");
  if (!apiKey) {
    vscode.window.showErrorMessage(
      "API key not configured. Check your settings."
    );
    return;
  }
  const genai = new GoogleGenerativeAI(apiKey);
  const model = genai.getGenerativeModel(
    { model: modelName },
    { apiVersion: "v1beta" }
  );
  try {
    const result = await model.generateContent({
      systemInstruction: {
        role: "system",
        parts: [{ text: SYSTEMINSTRUCTION }],
      },
      contents: [
        {
          role: "user",
          parts: [{ text: "Git Diff:" + diff }],
        },
      ],
    });
    const response = result.response;
    const commit = response.text();
    await vscode.env.clipboard.writeText(commit);
    await vscode.commands.executeCommand("workbench.view.scm");
    vscode.window.showInformationMessage(
      "Commit message copied to clipboard and can Past in the commit box."
    );
  } catch (error) {
    vscode.window.showErrorMessage(`${error}`);
  }
}
