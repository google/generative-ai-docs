/**
 * Copyright 2024 Google LLC
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
import {
  ChatSession,
  GenerateContentResult,
  GenerativeModel,
  GoogleGenerativeAI,
} from "@google/generative-ai";
import { devNull } from "os";
import { promises } from "dns";

// export async function generateChat(prompt: string): Promise<string> {
//   //vscode.window.showInformationMessage("Gemini thinking...");
//   const modelName = vscode.workspace
//     .getConfiguration()
//     .get<string>("google.gemini.textModel", "gemini-1.0-pro");

//   // Get API Key from local user configuration
//   const apiKey = vscode.workspace
//     .getConfiguration()
//     .get<string>("google.gemini.apiKey");
//   if (!apiKey) {
//     vscode.window.showErrorMessage(
//       "API key not configured. Check your settings."
//     );
//     return "API key not configured. Check your settings.";
//   }

//   const genai = new GoogleGenerativeAI(apiKey);
//   const model = genai.getGenerativeModel({ model: modelName });

//   const result = await model.generateContent(prompt);
//   const response = await result.response;
//   const messages = response.text();
//   return messages;
// }

export async function generateChat(
  prompt: string,
  model: GenerativeModel
): Promise<string> {
  //vscode.window.showInformationMessage("Gemini thinking...");

  const chat = model.startChat({
    history: [
      {
        role: "user",
        parts: [
          {
            text: "你是一个程序员，工作内容是使用 doxygen 风格生成注释。这是要注释代码：UCLASS(hidecategories = Object)class ULumaAssetFactory    : public UFactory{    GENERATED_UCLASS_BODY()public:    virtual UObject* FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled) override;};",
          },
        ],
      },
      {
        role: "model",
        parts: [
          {
            text: "```cpp\n/**\n * Factory for creating Luma assets.\n */\nUCLASS(hidecategories = Object)\nclass ULumaAssetFactory : public UFactory\n{\n    GENERATED_UCLASS_BODY()\n\npublic:\n    /**\n     * Creates a new Luma asset file.\n     *\n     * @param InClass    The class of the asset to create.\n     * @param InParent   The parent object for the new asset.\n     * @param InName     The name of the new asset.\n     * @param Flags      Object flags for the new asset.\n     * @param Filename   The filename of the new asset.\n     * @param Parms      Optional parameters for asset creation.\n     * @param Warn       Feedback context for warnings.\n     * @param bOutOperationCanceled  Output flag indicating whether the operation was canceled.\n     *\n     * @return The newly created Luma asset, or nullptr if creation failed.\n     */\n    virtual UObject* FactoryCreateFile(UClass* InClass, UObject* InParent, FName InName, EObjectFlags Flags, const FString& Filename, const TCHAR* Parms, FFeedbackContext* Warn, bool& bOutOperationCanceled) override;\n};\n```",
          },
        ],
      },
    ],
  });
  const result = await chat.sendMessage(prompt);
  const response = result.response;
  return response.text();
}

export function startchat(): GenerativeModel | void {
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
    return undefined;
  }

  const genai = new GoogleGenerativeAI(apiKey);
  const model = genai.getGenerativeModel({ model: modelName });

  return model;
}