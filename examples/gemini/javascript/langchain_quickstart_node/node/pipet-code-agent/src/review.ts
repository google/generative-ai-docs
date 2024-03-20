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

import * as vscode from 'vscode';
import { GoogleGenerativeAI } from '@google/generative-ai';
const CODE_LABEL = 'Here is the code:';
const REVIEW_LABEL = 'Here is the review:';
const PROMPT = `
Reviewing code involves finding bugs and increasing code quality. Examples of bugs are syntax 
errors or typos, out of memory errors, and boundary value errors. Increasing code quality 
entails reducing complexity of code, eliminating duplicate code, and ensuring other developers 
are able to understand the code. 
${CODE_LABEL}
for i in x:
    pint(f"Iteration {i} provides this {x**2}.")
${REVIEW_LABEL}
The command \`print\` is spelled incorrectly.
${CODE_LABEL}
height = [1, 2, 3, 4, 5]
w = [6, 7, 8, 9, 10]
${REVIEW_LABEL}
The variable name \`w\` seems vague. Did you mean \`width\` or \`weight\`?
${CODE_LABEL}
while i < 0:
  thrice = i * 3
  thrice = i * 3
  twice = i * 2
${REVIEW_LABEL}
There are duplicate lines of code in this control structure.
`;

export async function generateReview() {
  vscode.window.showInformationMessage('Generating code review...');
  const modelName = vscode.workspace.getConfiguration().get<string>('google.gemini.textModel', 'models/gemini-1.0-pro-latest');

  // Get API Key from local user configuration
  const apiKey = vscode.workspace.getConfiguration().get<string>('google.gemini.apiKey');
  if (!apiKey) {
    vscode.window.showErrorMessage('API key not configured. Check your settings.');
    return;
  }

  const genai = new GoogleGenerativeAI(apiKey);
  const model = genai.getGenerativeModel({model: modelName});

  // Text selection
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    console.debug('Abandon: no open text editor.');
    return;
  }

  const selection = editor.selection;
  const selectedCode = editor.document.getText(selection);

  // Build the full prompt using the template.
  const fullPrompt = `${PROMPT}
    ${CODE_LABEL}
    ${selectedCode}
    ${REVIEW_LABEL}
    `;

  const result = await model.generateContent(fullPrompt);
  const response = await result.response;
  const comment = response.text();  

  // Insert before selection
  editor.edit((editBuilder) => {
    // Copy the indent from the first line of the selection.
    const trimmed = selectedCode.trimStart();
    const padding = selectedCode.substring(0, selectedCode.length - trimmed.length);

    // TODO(you!): Support other comment styles.
    const commentPrefix = '# ';
    let pyComment = comment.split('\n').map((l: string) => `${padding}${commentPrefix}${l}`).join('\n');
    if (pyComment.search(/\n$/) === -1) {
      // Add a final newline if necessary.
      pyComment += "\n";
    }
    let reviewIntro = padding + commentPrefix + "Code review: (generated)\n";
    editBuilder.insert(selection.start, reviewIntro);
    editBuilder.insert(selection.start, pyComment);
  });
}
