document.addEventListener("DOMContentLoaded", function () {
  const vscode = acquireVsCodeApi();
  const oldState = vscode.getState() || {};
  let oldHtml = oldState || "<div></div>";

  // 在这里执行获取元素的操作
  const dialog = document.getElementById("dialog");
  const userInput = document.getElementById("userInput");
  const sendMessageButton = document.getElementById("sendMessage");
  let chatID;
  dialog.innerHTML = oldHtml;

  function adjustTextareaHeight() {
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";
    sendMessageButton.disabled = !userInput.value;
  }
  userInput.addEventListener("input", adjustTextareaHeight);

  // 显示接收到的Gemini消息
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
      sendMessageButton.innerHTML = "发送";
    }
  }

  // 显示问题
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
   *
   * @param {HTMLDivElement}
   */
  function addBottons(container) {
    const svg =
      '<svg width="16" height="16" xmlns="http://www.w3.org/2000/svg"> <g id="Layer_1">  <title>Layer 1</title>  <path stroke="null" id="svg_1" d="m11.17086,13.7471l-7.75098,0l0,-10.05744l-1.40928,0l0,10.05744c0,0.79023 0.63418,1.43678 1.40928,1.43678l7.75098,0l0,-1.43678zm2.81854,-2.87355l0,-8.62066c0,-0.79023 -0.63418,-1.43678 -1.40928,-1.43678l-6.34171,0c-0.7751,0 -1.40928,0.64655 -1.40928,1.43678l0,8.62066c0,0.79023 0.63418,1.43678 1.40928,1.43678l6.34171,0c0.7751,0 1.40928,-0.64655 1.40928,-1.43678zm-1.40928,0l-6.34171,0c0,-2.87355 0,-5.74711 0,-8.62066l6.34171,0l0,8.62066z" fill="#bfbdb6"/> </g></svg>';
    const codeElements = container.querySelectorAll("pre code");
    codeElements.forEach((codeElement) => {
      const copyButton = document.createElement("button");
      copyButton.innerHTML = svg;
      copyButton.classList.add("code-buttons-container");
      copyButton.addEventListener("click", () => {
        const textToCopy = codeElement.textContent;
        navigator.clipboard
          .writeText(textToCopy)
          .then(() => {
            copyButton.innerHTML = svg;
          })
          .catch((error) => {
            copyButton.innerHTML = "Failed";
          });
      });
      codeElement.parentElement.classList.add("pre");
      codeElement.parentElement.appendChild(copyButton);
      Prism.highlightElement(codeElement);
    });
  }

  // 当发送按钮被点击时
  sendMessageButton.addEventListener("click", () => {
    this.chatID = Math.random().toString();
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
        break;
    }
    vscode.setState(dialog.innerHTML);
  });
});
