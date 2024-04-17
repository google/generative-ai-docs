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
    .get<string>("google.gemini.textModel", "models/gemini-1.5-pro-latest");

  // Get API Key from local user configuration
  const apiKey = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.apiKey");
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
  await vscode.commands.executeCommand("git.commitStaged", commit);
  await vscode.commands.executeCommand("editor.action.insertSnippet", {
    snippet: commit,
  });
  vscode.window.showInformationMessage(
    "Commit message copied to clipboard and Pasted in the commit box."
  );
}
