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

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(async (message) => {
      // 处理来自 Webview 的消息
      if (message.command === "sendMessage" && message.text) {
        // 在 Webview 中显示接收到的消息
        webviewView.webview.postMessage({
          command: "receiveMessage",
          text: message.text,
        });
        const comments = await generateReview();
        if (comments) {
          webviewView.webview.postMessage({
            command: "receiveMessage",
            text: comments,
          });
        } else {
          webviewView.webview.postMessage({
            command: "receiveMessage",
            text: "请求失败。",
          });
        }
      }
    });
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    return `<!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
              background-color: var(--vscode-tab-activeBackground); /* 使用 VS Code 的标签页激活状态的背景色 */
              border-top: 1px solid var(--vscode-tab-activeBackground); /* 使用 VS Code 的标签页激活状态的背景色作为顶部边框颜色 */
            }

                input[type="text"],
            button {
              background-color: var(--vscode-input-background); /* 使用 VS Code 的输入框背景色 */
              color: var(--vscode-input-foreground); /* 使用 VS Code 的输入框前景色 */
              border: 1px solid var(--vscode-input-foreground); /* 使用 VS Code 的输入框前景色作为边框颜色 */
            }
                .message-container {
              background-color: var(--vscode-editor-background); /* 使用 VS Code 的编辑器背景色 */
              color: var(--vscode-editor-foreground); /* 使用 VS Code 的编辑器前景色 */
              border: 1px solid var(--vscode-editor-foreground); /* 使用 VS Code 的编辑器前景色作为边框颜色 */
              border-radius: 5px;
              padding: 10px;
              margin-bottom: 10px;
            }
              </style>
            </head>
            <body>
              <main>
                <h1>Gemini Chat</h1>
                <div id="dialog"></div>
              </main>
              <footer>
                <input type="text" id="userInput" placeholder="请输入您的消息">
                <button id="sendMessage">发送</button>
              </footer>

              <script>
                const vscode = acquireVsCodeApi();

                // 获取 UI 元素
                const dialog = document.getElementById('dialog');
                const userInput = document.getElementById('userInput');
                const sendMessageButton = document.getElementById('sendMessage');

                // 显示接收到的消息
                function showMessage(text) {
                const messageContainer = document.createElement('div'); // 创建一个新的 div 元素作为消息容器
                messageContainer.classList.add('message-container'); // 添加 CSS 类以进行样式设置
                messageContainer.innerHTML = '<p><strong>User:</strong> ' + text + '</p>'; // 设置消息内容
                dialog.appendChild(messageContainer); // 将消息容器添加到对话框中
                }

                // 当发送按钮被点击时
                sendMessageButton.addEventListener('click', () => {
                const userMessage = userInput.value;
                // 将用户消息发送给插件
                vscode.postMessage({ command: 'sendMessage', text: userMessage });
                userInput.value = ''; // 清空输入框
                });

                // 接收来自插件的消息
                window.addEventListener('message', event => {
                  const message = event.data;
                  if (message.command === 'receiveMessage') {
                    // 将收到的消息显示在对话框中
                    showMessage(message.text);
                  }
                });
              </script>
            </body>
            </html>


  `;
  }
}
export function deactivate() {}
