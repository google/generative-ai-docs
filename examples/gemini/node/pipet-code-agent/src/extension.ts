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
import { generateComment } from "./comments";
import { generateReview } from "./review";
import { startchat } from "./chat";

export function activate(context: vscode.ExtensionContext) {
  vscode.commands.registerCommand(
    "pipet-code-agent.commentCode",
    generateComment
  );
  vscode.commands.registerCommand(
    "pipet-code-agent.reviewCode",
    generateReview
  );

  const provider = new ChatViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      ChatViewProvider.viewType,
      provider
    )
  );
}
class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "pipet-code-agent.ChatView";

  private _view?: vscode.WebviewView;

  constructor(private readonly _extensionUri: vscode.Uri) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      // Allow scripts in the webview
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtmlForWebview();

    const chat = startchat();

    webviewView.webview.onDidReceiveMessage(async (message) => {
      // 处理来自 Webview 的消息
      if (message.command === "sendMessage" && message.text) {
        // 在 Webview 中显示接收到的消息
        webviewView.webview.postMessage({
          command: "Message",
          text: message.text,
        });
        if (chat) {
          const result = await chat.sendMessageStream(message.text);
          let chunktext = "";
          for await (const chunk of result.stream) {
            chunktext += chunk.text();
            webviewView.webview.postMessage({
              command: "receiveMessage",
              text: chunktext,
            });
          }
        } else {
          webviewView.webview.postMessage({
            command: "receiveMessage",
            text: "请求失败。",
          });
        }
      }
    });
  }

  private _getHtmlForWebview() {
    return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Gemini Chat</title>
    <style>
      body {
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        min-height: 100vh; /* 使内容占据整个视口高度 */
      }

      main {
        flex: 1; /* 使 main 元素占据剩余的垂直空间 */
        padding: 20px; /* 添加内边距 */
      }

      #dialog {
        overflow-y: auto; /* 当内容过多时，显示滚动条 */
        border-radius: 5px; /* 添加边框圆角 */
        padding: 10px; /* 添加内边距 */
        margin-bottom: 10px; /* 添加底部外边距 */
      }

      footer {
        display: flex;
        align-items: center;
        padding: 10px;
      }

      #userInput {
        height: auto;
        resize: none;
        background-color: var(
          --vscode-input-background
        ); /* 使用 VS Code 的输入框背景色 */
        color: var(--vscode-input-foreground); /* 使用 VS Code 的输入框前景色 */
        border: 1px solid var(--vscode-input-foreground); /* 使用 VS Code 的输入框前景色作为边框颜色 */
        flex: 1;
      }

      #sendMessage {
        background-color: var(
          --vscode-input-background
        ); /* 使用 VS Code 的输入框背景色 */
        color: var(--vscode-input-foreground); /* 使用 VS Code 的输入框前景色 */
        border: 1px solid var(--vscode-input-foreground); /* 使用 VS Code 的输入框前景色作为边框颜色 */
        margin-left: 5px;        
      }

      .ai-message-container {
        background-color: var(--vscode-input-background);
        color: var(--vscode-editor-foreground);
      }
      .user-message-container {
        background-color: var(--vscode-input-background);
        color: var(--vscode-editor-foreground);
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Gemini Chat</h1>
      <div id="dialog"></div>
    </main>
    <footer>
      <textarea id="userInput" placeholder="请输入您的消息"></textarea>
      <button id="sendMessage" disabled>发送</button>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script>
      const vscode = acquireVsCodeApi();

      // 获取 UI 元素
      const dialog = document.getElementById("dialog");
      const userInput = document.getElementById("userInput");
      const sendMessageButton = document.getElementById("sendMessage");
      const ID = "";

      function adjustTextareaHeight() {
        userInput.style.height = "auto";
        userInput.style.height = userInput.scrollHeight + "px";
        sendMessageButton.disabled = !userInput.value;
      }
      userInput.addEventListener("input", adjustTextareaHeight);

      // 显示接收到的Gemini消息
      function showAIMessage(text, ID) {
        const messageContainer = document.createElement("div");
        messageContainer.id = ID;
        messageContainer.classList.add("ai-message-container");
        messageContainer.innerHTML =
          "<p><strong>Gemini:</strong> " + marked.parse(text) + "</p>";
        dialog.appendChild(messageContainer);
      }

      function updateAIMessage(newText, ID) {
        const messageContainer = document.getElementById(ID);
        messageContainer.innerHTML = "<p><strong>Gemini:</strong> " + marked.parse(newText) + "</p>";
        sendMessageButton.innerHTML = "发送";
      }

      // 显示问题
      function showUserMessage(text) {
        const messageContainer = document.createElement("div");
        messageContainer.classList.add("user-message-container");
        messageContainer.innerHTML =
          "<p><strong>User:</strong> " + marked.parse(text) + "</p>";
        dialog.appendChild(messageContainer);
      }

      // 当发送按钮被点击时
      sendMessageButton.addEventListener("click", () => {
        this.ID = Math.random().toString();
        const userMessage = userInput.value;
        vscode.postMessage({ command: "sendMessage", text: userMessage });
        userInput.value = "";
        userInput.style.height = "auto";
        sendMessageButton.disabled = true;
        sendMessageButton.innerHTML = "Thinking...";
      });

      // 接收来自插件的消息
      window.addEventListener("message", (event) => {
        const message = event.data;
        switch (message.command) {
          case "receiveMessage":
            updateAIMessage(message.text, this.ID);
            break;
          case "Message":
            showUserMessage(message.text);
            showAIMessage("Thinking ...", this.ID);
            break;
          default:
            console.log("Unknown command: " + message.command);
        }
      });
    </script>
  </body>
</html>
`;
  }
}

export function deactivate() {}
