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

document.addEventListener("DOMContentLoaded", function () {
  const vscode = acquireVsCodeApi();
  const oldState = vscode.getState() || {};
  let oldHtml = oldState || "<div></div>";

  const dialog = document.getElementById("dialog");
  const userInput = document.getElementById("userInput");
  const sendMessageButton = document.getElementById("sendMessage");
  let chatID;
  dialog.innerHTML = oldHtml;
  userInput.scrollIntoView({ behavior: "smooth", block: "end" });

  const allCodeButtons = Array.from(
    dialog.getElementsByClassName("code-buttons-container")
  );
  if (allCodeButtons) {
    allCodeButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const toCopy =
          button.parentElement.querySelectorAll("pre code")[0].textContent;
        navigator.clipboard.writeText(toCopy);
      });
    });
  }

  const allChats = Array.from(
    dialog.getElementsByClassName("message-container")
  );
  if (allChats) {
    allChats.forEach((chat) => {
      switch (chat.firstChild.textContent) {
        case "You: ":
          vscode.postMessage({
            command: "updateHistory",
            role: "user",
            text: chat.textContent.replace("You:", "").trim(),
          });
          break;
        case "Gemini: ":
          vscode.postMessage({
            command: "updateHistory",
            role: "model",
            text: chat.textContent.replace("model:", "").trim(),
          });
          break;
      }
    });
  }

  function adjustTextareaHeight() {
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";
    sendMessageButton.disabled = !userInput.value;
  }
  userInput.addEventListener("input", adjustTextareaHeight);
  userInput.addEventListener("keydown", handleKeyDown);

  function showAIMessage(text, chatID) {
    const messageContainer = document.createElement("div");
    if (messageContainer) {
      messageContainer.id = chatID;
      messageContainer.classList.add("message-container");
      messageContainer.innerHTML =
        "<p><strong>Gemini:</strong> " + marked.parse(text) + "</p>";
      dialog.appendChild(messageContainer);
      userInput.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }

  function updateAIMessage(newText, chatID) {
    const messageContainer = document.getElementById(chatID);
    if (messageContainer) {
      (messageContainer.innerHTML =
        "<p><strong>Gemini:</strong> " + marked.parse(newText)),
        +"</p>";
      addBottons(messageContainer);
      sendMessageButton.innerHTML = "Chat";
      userInput.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }

  function onSelection(text) {
    userInput.placeholder = text;
  }

  function showUserMessage(text) {
    const messageContainer = document.createElement("div");
    if (messageContainer) {
      messageContainer.classList.add("message-container");
      messageContainer.innerHTML =
        "<p><strong>You:</strong> " + marked.parse(text) + "</p>";
      addBottons(messageContainer);
      dialog.appendChild(messageContainer);
      userInput.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }
  /**
   * @param {HTMLDivElement}
   */
  function addBottons(container) {
    const codeElements = container.querySelectorAll("pre code");
    codeElements.forEach((codeElement) => {
      const copyButton = document.createElement("button");
      copyButton.classList.add("code-buttons-container");
      copyButton.addEventListener("click", () => {
        const textToCopy = codeElement.textContent;
        navigator.clipboard.writeText(textToCopy);
      });
      codeElement.parentElement.classList.add("pre");
      codeElement.parentElement.appendChild(copyButton);
      Prism.highlightElement(codeElement);
    });
  }

  function handleKeyDown(event) {
    if (event.keyCode === 13) {
      if (!event.shiftKey) {
        event.preventDefault();
        sendMessageButton.click();
      }
    }
  }

  sendMessageButton.addEventListener("click", () => {
    chatID = Math.random().toString().substring(2);
    const userMessage = userInput.value;
    vscode.postMessage({ command: "sendMessage", text: userMessage });
    userInput.value = "";
    userInput.style.height = "auto";
    sendMessageButton.disabled = true;
    sendMessageButton.innerHTML = "Thinking...";
  });

  window.addEventListener("message", (event) => {
    const message = event.data;
    switch (message.command) {
      case "receiveMessage":
        updateAIMessage(message.text, chatID);
        break;
      case "Message":
        showUserMessage(message.text);
        showAIMessage("Thinking ...", chatID);
        break;
      case "clearChat":
        dialog.innerHTML = "<div></div>";
        break;
      case "onSelection":
        onSelection(message.text);
        break;
      default:
        console.log("Unknown command: " + message.command);
    }
    vscode.setState(dialog.innerHTML);
  });
});
