/**
 * Copyright 2024 Jason
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

  function adjustTextareaHeight() {
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";
    sendMessageButton.disabled = !userInput.value;
  }
  userInput.addEventListener("input", adjustTextareaHeight);

  function showAIMessage(text, chatID) {
    const messageContainer = document.createElement("div");
    if (messageContainer) {
      messageContainer.id = chatID;
      messageContainer.classList.add("message-container");
      messageContainer.innerHTML =
        "<p><strong>Gemini:</strong> " + marked.parse(text) + "</p>";
      dialog.appendChild(messageContainer);
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
    }
  }

  function showUserMessage(text) {
    const messageContainer = document.createElement("div");
    if (messageContainer) {
      messageContainer.classList.add("message-container");
      messageContainer.innerHTML =
        "<p><strong>You:</strong> " + marked.parse(text) + "</p>";
      addBottons(messageContainer);
      dialog.appendChild(messageContainer);
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

  sendMessageButton.addEventListener("click", () => {
    this.chatID = Math.random().toString();
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
        updateAIMessage(message.text, this.chatID);
        break;
      case "Message":
        showUserMessage(message.text);
        showAIMessage("Thinking ...", this.chatID);
        break;
      case "clearChat":
        dialog.innerHTML = "<div></div>";
        break;
      default:
        console.log("Unknown command: " + message.command);
    }
    vscode.setState(dialog.innerHTML);
  });
});