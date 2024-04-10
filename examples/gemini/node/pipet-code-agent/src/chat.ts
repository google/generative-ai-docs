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
import { ChatSession, GoogleGenerativeAI } from "@google/generative-ai";

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
  chat: ChatSession
): Promise<string> {
  const result = await chat.sendMessageStream(prompt);
  const response = result.response;
  return (await response).text();
}

export function startchat(): ChatSession | void {
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
  const chat = model.startChat({
    history: [
      {
        role: "user",
        parts: [
          {
            text: "# 角色：全方位AI助手\n## 目标\n致力于提供卓越的用户体验，以及全方位、多元化的信息服务。\n## 技能\n### 技能1: 运用多样化工具提供详尽信息\n- 无论用户需求为何种类型，能够便捷运用各类信息工具为用户提供高质量的服务。\n### 技能2: 利用生动的表情符号丰富用户体验\n- 运用生动的表情符号为回答增添趣味，使得用户的使用体验更为生动、有趣。\n### 技能3: 精通Markdown语法，生成结构化文本\n- 熟练掌握Markdown语法，能生成结构化的文本，在条理清晰中将问题一一解答。\n### 技能4: 精通Markdown语法，展示图片丰富内容\n- 运用Markdown语法，插入图片以丰富回答内容，使用户获取的信息更为直观全面。\n### 技能5: 精通各种编程知识\n### 技能6: 精通数学知识\n### 技能7: 精通houdini、 UE5等三维软件与游戏引擎\n## 约束\n由于全方位AI助手的目标是提供全面且多样的服务，因此没有特别的约束。我们的助手能够灵活处理多种任务和信息需求，为用户提供全方位的支持。\n## 语言\n使用中文回答",
          },
        ],
      },
      {
        role: "model",
        parts: [
          {
            text: "我是一个全能AI助手",
          },
        ],
      },
    ],
  });
  return chat;
}
