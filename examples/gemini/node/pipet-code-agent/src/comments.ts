/**
 * Copyright 2023 Google LLC
 *
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

const SYSTEMINSTRUCTION =
  "Comment code use doxygen style. Don't repeat Prompt. Only return the comments Content.";

/**
 *@brief Generate comment for code selection.
 * Gets the API key from user config and sends selected text to Gemini for comment generation.
 * Inserts generated comment before the selected code.
 */
export async function generateComment() {
  vscode.window.showInformationMessage("Generating comment...");

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

  // Text selection
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    console.debug("Abandon: no open text editor.");
    return;
  }

  const selection = editor.selection;
  const selectedCode = editor.document.getText(selection);

  try {
    const result = await model.generateContent({
      systemInstruction: {
        role: "system",
        parts: [{ text: SYSTEMINSTRUCTION }],
      },
      contents: [
        {
          role: "user",
          parts: [
            {
              text:
                "```" +
                editor.document.languageId +
                "\n" +
                selectedCode +
                "\n```",
            },
          ],
        },
      ],
    });
    const response = result.response;
    const comment = response.text();
    // Insert before selection.
    editor.edit((editBuilder) => {
      editBuilder.insert(selection.start, comment);
    });
  } catch (error) {
    vscode.window.showErrorMessage(`${error}`);
    return;
  }
}
