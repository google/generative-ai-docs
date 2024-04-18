/**
 * Copyright 2024 Jason
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
