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
import { getCommentprefixes } from "./getCommentprefixes";

// Provide instructions for the AI language model
// This approach uses a few-shot technique, providing a few examples.
const CODE_LABEL = "Here is the code:";
const COMMENT_LABEL = "Here is a good comment:";
const PROMPT = `
A good code review comment describes the intent behind the code without
repeating information that's obvious from the code itself. Good comments
describe "why", explain any "magic" values and non-obvious behaviour.
Below are some examples of good code comments.

${CODE_LABEL}
print(f" \\033[33m {msg}\\033[00m", file=sys.stderr)
${COMMENT_LABEL}
Use terminal codes to print color output to console.

${CODE_LABEL}
to_delete = set(data.keys()) - frozenset(keep)
for key in to_delete:
  del data[key]
${COMMENT_LABEL}
Modifies \`data\` to remove any entry not specified in the \`keep\` list.

${CODE_LABEL}
lines[text_range.start_line - 1:text_range.end_line - 1] = [repl.new_content]
${COMMENT_LABEL}
Replace text from \`lines\` with \`new_content\`, noting that array indices 
are offset 1 from line numbers.

${CODE_LABEL}
api_key = os.getenv("GOOGLE_API_KEY")
${COMMENT_LABEL}
Attempt to load the API key from the environment.

${CODE_LABEL}
UFUNCTION(BlueprintCallable, Category = "TransparentWindows")
static void MakeTransparentWindow(ETWMode Usage);
${COMMENT_LABEL}
@brief Make Transparent Window.
@param Usage    Window Transparent mode.

${CODE_LABEL}
virtual void Tick(float DeltaTime) override;
${COMMENT_LABEL}
@brief Calls super::Tick(DeltaTime), then updates world bounds.
@param DeltaTime    The change in time between two points or events.


${CODE_LABEL}
sendMessage(request: string | Array<string | Part>): Promise<GenerateContentResult>;
${COMMENT_LABEL}
Sends a chat message and receives a non-streaming
{@link GenerateContentResult}

${CODE_LABEL}
export declare class ChatSession {
    model: string;
    params?: StartChatParams;
    requestOptions?: RequestOptions;
    private _apiKey;
    private _history;
    private _sendPromise;
    constructor(apiKey: string, model: string, params?: StartChatParams, requestOptions?: RequestOptions);
    getHistory(): Promise<Content[]>;
    sendMessage(request: string | Array<string | Part>): Promise<GenerateContentResult>;
    sendMessageStream(request: string | Array<string | Part>): Promise<GenerateContentStreamResult>;
}
${COMMENT_LABEL}
@brief ChatSession class that enables sending chat messages and stores history of sent and received messages so far.

${CODE_LABEL}
virtual void CreateClassVariablesFromBlueprint(IAnimBlueprintVariableCreationContext& InCreationContext) = 0;
${COMMENT_LABEL}
@brief Implement this in a graph node and the anim BP compiler will call this expecting to generate class variables.
@param	InVariableCreator   The variable creation context for the current BP compilation
`;


/**
 *@brief Generate comment for code selection.
 * Gets the API key from user config and sends selected text to Gemini for comment generation.
 * Inserts generated comment before the selected code.
*/
export async function generateComment() {
  vscode.window.showInformationMessage("Generating comment...");

  const modelName = vscode.workspace
    .getConfiguration()
    .get<string>("google.gemini.textModel", "gemini-1.0-pro");

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
  const model = genai.getGenerativeModel({ model: modelName });

  // Text selection
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    console.debug("Abandon: no open text editor.");
    return;
  }

  const selection = editor.selection;
  const selectedCode = editor.document.getText(selection);

  // Build the full prompt using the template.
  const fullPrompt = `${PROMPT}${CODE_LABEL}${selectedCode}${COMMENT_LABEL}`;

  const result = await model.generateContent(fullPrompt);
  const response = await result.response;
  const comment = response.text();

  // Insert before selection.
  editor.edit((editBuilder) => {
    // Copy the indent from the first line of the selection.
    const trimmed = selectedCode.trimStart();
    const padding = selectedCode.substring(
      0,
      selectedCode.length - trimmed.length
    );

    // const commentPrefix = getCommentprefixes(editor.document.languageId);
    const commentPrefix = `${padding} *`;

    /**
     *Split the comment into lines using `'\n'` as separator.
     *Add an indentation, comment prefix and join the lines back with a `'\n'` separator.
     */
    let inlineComment = comment
      .split("\n")
      .map((l: string) => `${padding}${commentPrefix}${l}`)
      .join("\n");
    if (inlineComment.search(/\n$/) === -1) {
      // Add a final newline if necessary.
      inlineComment += "\n";
    }
    let commentIntro = padding + "/**\n";
    let commentEnd = padding + "*/\n";
    editBuilder.insert(selection.start, commentIntro);
    editBuilder.insert(selection.start, inlineComment);
    editBuilder.insert(selection.start, commentEnd);
  });
}
