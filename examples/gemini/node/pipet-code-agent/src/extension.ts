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
import { ChatSession } from "@google/generative-ai";
import { generateGitCommit } from "./gitCommit";

export function activate(context: vscode.ExtensionContext) {
  vscode.commands.registerCommand(
    "pipet-code-agent.commentCode",
    generateComment
  );
  vscode.commands.registerCommand(
    "pipet-code-agent.reviewCode",
    generateReview
  );

  vscode.commands.registerCommand(
    "pipet-code-agent.generateGitCommit",
    generateGitCommit
  );

  const provider = new ChatViewProvider(context.extensionUri);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      ChatViewProvider.viewType,
      provider
    )
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("pipet-code-agent.clearChat", () => {
      provider.clearChat();
    })
  );
}

let chat: void | ChatSession;
class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "pipet-code-agent.chatView";

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

    try {
      chat = startchat();
      webviewView.webview.onDidReceiveMessage(async (message) => {
        if (message.command === "sendMessage" && message.text) {
          webviewView.webview.postMessage({
            command: "Message",
            text: message.text,
          });
          if (chat) {
            try {
              const code = this.selectedCode();
              const prompt = `${code}${message.text}`;
              const result = await chat.sendMessageStream(prompt);
              let chunktext = "";
              for await (const chunk of result.stream) {
                chunktext += chunk.text();
                webviewView.webview.postMessage({
                  command: "receiveMessage",
                  text: chunktext,
                });
              }
            } catch (error) {
              webviewView.webview.postMessage({
                command: "receiveMessage",
                text: `${error}`,
              });
            }
          } else {
            webviewView.webview.postMessage({
              command: "receiveMessage",
              text: "Chat Start Failed.",
            });
          }
        }
      });
    } catch (error) {
      webviewView.webview.postMessage({
        command: "receiveMessage",
        text: `${error}`,
      });
    }
  }

  public selectedCode(): string {
    try {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        console.debug("Abandon: no open text editor.");
        return "";
      }
      const code = editor.document.getText(editor.selection);
      const prefix = "```";
      const codePrefix = `${prefix}${editor.document.languageId}`;
      const result = `${codePrefix}\n${code}\n${prefix}\n`;
      return result ?? "";
    } catch (error) {
      vscode.window.showErrorMessage(`${error}`);
      return "";
    }
  }

  public clearChat() {
    if (this._view) {
      this._view.webview.postMessage({
        command: "clearChat",
      });
      try {
        chat = startchat();
      } catch (error) {
        this._view.webview.postMessage({
          command: "receiveMessage",
          text: `${error}`,
        });
      }
    }
  }
  private _getHtmlForWebview(webview: vscode.Webview) {
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.js")
    );
    const styleMainUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.css")
    );
    const styleCodeUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "prism.css")
    );
    const mediaUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media")
    );
    // Use a nonce to only allow a specific script to be run.
    const nonce = getNonce();
    return `<!DOCTYPE html>
            <html lang="en">
              <head>
                <meta charset="UTF-8" />
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src ${webview.cspSource}; script-src 'nonce-${nonce}' https://cdn.jsdelivr.net/npm/prismjs/components/;">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="${styleMainUri}" rel="stylesheet">
                <link rel="stylesheet" href="${styleCodeUri}">
                <title>Gemini Chat</title>
              </head>
              <body>
                <main>
                  <div id="dialog"></div>
                </main>
                <footer>
                  <textarea id="userInput" placeholder="Ask anything here"></textarea>
                  <button id="sendMessage" disabled>Chat</button>
                </footer>
                <script nonce="${nonce}" src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
                <script nonce="${nonce}" src="https://cdn.jsdelivr.net/npm/prismjs/prism.min.js"></script>
                <script nonce="${nonce}" src="https://cdn.jsdelivr.net/npm/prismjs/plugins/autoloader/prism-autoloader.min.js">
                Prism.plugins.autoloader.languages_path = "${mediaUri}";
                </script>
                <script nonce="${nonce}" src="${scriptUri}"></script>
              </body>
            </html>`;
  }
}
function getNonce() {
  let text = "";
  const possible =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
export function deactivate() {}
