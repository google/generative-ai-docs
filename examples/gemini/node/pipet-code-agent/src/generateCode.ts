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

const SYSTEMINSTRUCTION = `Code Enhancement:\n目的: 将用户提供的注释替换为实际可用的代码，并在不重写整个函数/类/等的情况下，仅修改指定范围内的代码。\n输入:\nfileTextWithLineNumbers:包含行号的项目文件文本。\nlineNumber:用户想要修改的代码行号。\ncurrentLineText:当前行包含的注释文本。\nlanguage:项目使用的编程语言。\n输出:\n将 currentLineText 替换为实际代码的修改后的代码片段，不包含任何额外的行，也不要包裹在代码块中.\n示例:\n用户输入:\nlineNumber: 2\ncurrentLineText: TODO: Implement add_numbers function \nlanguage: python\n系统输出:\nreturn x + y\n注意: 输出仅包含替换后的代码，不包含任何额外的行,也不要包裹在代码块中(i.e., \`\`\`).`;

function addLineNumbers(text: string): string {
  const lines = text.split("\n");
  const numberedLines = lines.map((line, index) => `${index + 1}: ${line}`);
  return numberedLines.join("\n");
}

export function performAction() {
  // Get the active text editor
  const editor = vscode.window.activeTextEditor;
  if (editor) {
    // Show loading notification
    vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Generating AI code...",
        cancellable: false,
      },
      async (progress) => {
        try {
          progress.report({ increment: 0 });

          const language = editor.document.languageId;
          const fileTextWithLineNumbers = addLineNumbers(
            editor.document.getText()
          );
          const currentLineText = editor.document
            .lineAt(editor.selection.active.line)
            .text.trim();
          const lineNumber = editor.selection.active.line + 1;

          // Generate the code
          const generatedCode = await generateCode(
            fileTextWithLineNumbers,
            lineNumber,
            currentLineText,
            language
          );

          // Insert the generated code at the current cursor position
          editor.insertSnippet(
            new vscode.SnippetString("\n" + generatedCode),
            editor.selection.active
          );
          vscode.window.showInformationMessage("AI Code Generated!");
        } catch (error: any) {
          vscode.window.showErrorMessage(
            "Error generating code: " + error?.message
          );
        }
      }
    );
  }
}

async function generateCode(
  fileTextWithLineNumbers: string,
  lineNumber: number,
  currentLineText: string,
  language: string
): Promise<string> {
  const apiKey = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.apiKey", "default");

  if (!apiKey) {
    vscode.window.showErrorMessage(
      "API key not configured. Check your settings."
    );
    return "";
  }

  const modelName = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.textModel", "default");
  const genai = new GoogleGenerativeAI(apiKey);
  const model = genai.getGenerativeModel(
    { model: modelName },
    { apiVersion: "v1beta" }
  );

  const prompt = `fileTextWithLineNumbers:${fileTextWithLineNumbers}
  lineNumber:${lineNumber}
  currentLineText:${currentLineText}
  language:${language}`;

  const result = await model.generateContent({
    systemInstruction: { role: "system", parts: [{ text: SYSTEMINSTRUCTION }] },
    contents: [
      {
        role: "user",
        parts: [
          { text: prompt },
          { text: "请不要将生成的代码包裹在代码块中。" },
        ],
      },
    ],
  });
  const response = result.response;
  const text = response.text();
  return text;
}
