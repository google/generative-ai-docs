/**
 * Copyright 2024 Jason
 */

import * as vscode from "vscode";
import { GoogleGenerativeAI } from "@google/generative-ai";

const SYSTEMINSTRUCTION =
  "Generate Git Commit by Git Diff, Don't return other message.";

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
    await generateCommit(diff);
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
