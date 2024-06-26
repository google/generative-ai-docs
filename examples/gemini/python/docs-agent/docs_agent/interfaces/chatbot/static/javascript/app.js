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

// Display the "loading" message when a question is entered and submitted.
let askButton = document.getElementById('ask-button');
let loadingDiv = document.getElementById('loading-div');

if (askButton != null){
  askButton.addEventListener('click',function (){
    if (loadingDiv.classList.contains("hidden")){
      loadingDiv.classList.remove("hidden");
    }
  });
}

// Display the "loading" message when a related question is clicked.
let relatedQuestions = document.getElementById('suggested-questions');

if (relatedQuestions != null){
  questions = relatedQuestions.getElementsByTagName('a');
  for(i=0; i<questions.length; i++){
    questions[i].addEventListener('click',function (){
      if (loadingDiv.classList.contains("hidden")){
        loadingDiv.classList.remove("hidden");
      }
    });
  }
}

// Display the "aqa-box" div only if the aqa json response is included.
let aqaContent = document.getElementById('aqa-content');
let aqaBox = document.getElementById('aqa-box');

if (aqaContent != null){
  if (aqaContent.innerText.trim() != ""){
    if (aqaBox.classList.contains("hidden")){
      aqaBox.classList.remove("hidden");
    }
  }
}

// Toggle the hidden class on the `rewrite-box` div.
let rewriteButton = document.getElementById('rewrite-button');

if (rewriteButton != null){
  rewriteButton.addEventListener('click',function (){
    let rewriteBox = document.getElementById('rewrite-box');
    if (rewriteBox.classList.contains("hidden")){
      rewriteBox.classList.remove("hidden");
      // Trigger a focus event on the textarea
      let element = document.getElementById('edit-text-area');
      element.dispatchEvent(new Event("focus"));
    }else{
      rewriteBox.classList.add("hidden");
    }
  });
}

// Toggle the hidden class on the `feedback-box` div.
let feedbackButton = document.getElementById('feedback-button');

if (feedbackButton != null){
  feedbackButton.addEventListener('click',function (){
    let feedbackBox = document.getElementById('feedback-box');
    if (feedbackBox.classList.contains("hidden")){
      feedbackBox.classList.remove("hidden");
      // Trigger a focus event on the textarea
      let element = document.getElementById('feedback-text-area');
      element.dispatchEvent(new Event("focus"));
    }else{
      feedbackBox.classList.add("hidden");
    }
  });
}

// Toggle the selected class on the `like this response` button.
let likeButton = document.getElementById('like-button');
let dislikeButton = document.getElementById('dislike-button');

if (likeButton != null){
  likeButton.addEventListener('click',function (){
    if (likeButton.classList.contains("notselected")) {
      this.classList.remove("notselected");
      this.classList.add("selected");
      this.value = "Liked"
      let uuidBox = document.getElementById('uuid-box');
      let uuid = "Unknown";
      if (uuidBox != null){
        uuid =  uuidBox.textContent;
      }
      if (dislikeButton != null){
        dislikeButton.classList.add("hidden");
        if (dislikeButton.classList.contains("selected")) {
          dislikeButton.classList.remove("selected");
          dislikeButton.classList.add("notselected");
	}
      }
      let xhr = new XMLHttpRequest();
      // The value of `urlLike` is specified in the html template,
      // which is set by the Flask server.
      // See chatbot/templates/chatui/base.html
      xhr.open("POST", urlLike, true);
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("Content-Type", "application/json");
      let data = JSON.stringify({"like": true, "uuid": uuid});
      xhr.send(data);
    }else{
      this.classList.remove("selected");
      this.classList.add("notselected");
      this.value = 'Like this response \uD83D\uDC4D';
      let uuidBox = document.getElementById('uuid-box');
      let uuid = "Unknown";
      if (uuidBox != null){
        uuid =  uuidBox.textContent;
      }
      if (dislikeButton != null){
        dislikeButton.classList.remove("hidden");
        if (dislikeButton.classList.contains("selected")) {
          dislikeButton.classList.remove("selected");
          dislikeButton.classList.add("notselected");
	}
      }
      let xhr = new XMLHttpRequest();
      // The value of `urlLike` is specified in the html template,
      // which is set by the Flask server.
      // See chatbot/templates/chatui/base.html
      xhr.open("POST", urlLike, true);
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("Content-Type", "application/json");
      let data = JSON.stringify({"like": false, "uuid": uuid});
      xhr.send(data);
    }
  });
}

// Toggle the selected class on the `dislike` button.
if (dislikeButton != null){
  dislikeButton.addEventListener('click',function (){
    if (dislikeButton.classList.contains("notselected")) {
      this.classList.remove("notselected");
      this.classList.add("selected");
      this.value = "Disliked"
      let uuidBox = document.getElementById('uuid-box');
      let uuid = "Unknown";
      if (uuidBox != null){
        uuid =  uuidBox.textContent;
      }
      if (likeButton != null){
        likeButton.classList.add("hidden");
        if (likeButton.classList.contains("selected")) {
          likeButton.classList.remove("selected");
          likeButton.classList.add("notselected");
	}
      }
      let xhr = new XMLHttpRequest();
      // The value of `urlLike` is specified in the html template,
      // which is set by the Flask server.
      // See chatbot/templates/chatui/base.html
      xhr.open("POST", urlLike, true);
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("Content-Type", "application/json");
      let data = JSON.stringify({"dislike": true, "uuid": uuid});
      xhr.send(data);
    }else{
      this.classList.remove("selected");
      this.classList.add("notselected");
      this.value = 'Dislike \uD83D\uDC4E';
      let uuidBox = document.getElementById('uuid-box');
      let uuid = "Unknown";
      if (uuidBox != null){
        uuid =  uuidBox.textContent;
      }
      if (likeButton != null){
        likeButton.classList.remove("hidden");
        if (likeButton.classList.contains("selected")) {
          likeButton.classList.remove("selected");
          likeButton.classList.add("notselected");
	}
      }
      let xhr = new XMLHttpRequest();
      // The value of `urlLike` is specified in the html template,
      // which is set by the Flask server.
      // See chatbot/templates/chatui/base.html
      xhr.open("POST", urlLike, true);
      xhr.setRequestHeader("Accept", "application/json");
      xhr.setRequestHeader("Content-Type", "application/json");
      let data = JSON.stringify({"dislike": false, "uuid": uuid});
      xhr.send(data);
    }
  });
}

// Adjust the size of the `edit-text-area` textarea.
let rewriteTextArea = document.getElementById('edit-text-area');

if (rewriteTextArea != null){
  rewriteTextArea.addEventListener('focus', resize_textarea);
  rewriteTextArea.addEventListener('input', resize_textarea);
}

function resize_textarea(){
  this.style.height = "5px";
  this.style.width = "650px";
  this.style.height = (this.scrollHeight)+"px";
  let rewriteSubmitButton = document.getElementById('submit-button');
  if (rewriteSubmitButton != null){
    if (rewriteSubmitButton.classList.contains("disable")){
      rewriteSubmitButton.classList.remove("disable");
      let submitResult = document.getElementById('submit-result');
      submitResult.textContent = "Click to re-submit updated rewrite.";
    }
  }
}

// Adjust the size of the `feedback-text-area` textarea.
let feedbackTextArea = document.getElementById('feedback-text-area');

if (feedbackTextArea != null){
  feedbackTextArea.addEventListener('focus', resize_feedback_textarea);
  feedbackTextArea.addEventListener('input', resize_feedback_textarea);
}

function resize_feedback_textarea(){
  this.style.height = "5px";
  this.style.width = "650px";
  this.style.height = (this.scrollHeight)+"px";
  let feedbackSubmitButton = document.getElementById('feedback-submit-button');
  if (feedbackSubmitButton != null){
    if (feedbackSubmitButton.classList.contains("disable")){
      feedbackSubmitButton.classList.remove("disable");
      let feedbackResult = document.getElementById('feedback-submit-result');
      feedbackResult.textContent = "Click to re-submit updated feedback.";
    }
  }
}

// Make a rewrite POST call.
let rewriteSubmitButton = document.getElementById('submit-button');

if (rewriteSubmitButton != null){
  rewriteSubmitButton.addEventListener('click',function (){
    let xhr = new XMLHttpRequest();
    // The value of `urlRewrite` below is specified in the html template,
    // which is set by the Flask server.
    // See chatbot/templates/chatui/base.html
    xhr.open("POST", urlRewrite, true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    let rewriteQuestion = document.getElementById('rewrite-question-span');
    let rewriteOriginalResponse = document.getElementById('rewrite-original-response-span');
    let rewriteTextArea = document.getElementById('edit-text-area');
    let userIDInput = document.getElementById('user-id');
    let userID = userIDInput.value;
    if (userID == "") {
      userID = "anonymous";
    }
    let data = JSON.stringify({
      "user_id": userID,
      "question": rewriteQuestion.textContent,
      "original_response": rewriteOriginalResponse.textContent,
      "rewrite": rewriteTextArea.value});
    xhr.send(data);

    let submitResult = document.getElementById('submit-result');
    submitResult.textContent = "Rewrite has been submitted. Thank you!";
    rewriteSubmitButton.classList.add("disable");
  }, false);
}

// Make a feedback POST call.
let feedbackSubmitButton = document.getElementById('feedback-submit-button');

if (feedbackSubmitButton != null){
  feedbackSubmitButton.addEventListener('click',function (){
    let xhr = new XMLHttpRequest();
    // The value of `urlRewrite` below is specified in the html template,
    // which is set by the Flask server.
    // See chatbot/templates/chatui/base.html
    xhr.open("POST", urlFeedback, true);
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");
    let feedbackQuestion = document.getElementById('feedback-question-span');
    let feedbackResponse = document.getElementById('feedback-response-span');
    let feedbackTextArea = document.getElementById('feedback-text-area');
    let userIDInput = document.getElementById('user-id');
    let userID = userIDInput.value;
    if (userID == "") {
      userID = "anonymous";
    }
    let data = JSON.stringify({
      "user_id": userID,
      "question": feedbackQuestion.textContent,
      "response": feedbackResponse.textContent,
      "feedback": feedbackTextArea.value});
    xhr.send(data);

    let feedbackResult = document.getElementById('feedback-submit-result');
    feedbackResult.textContent = "Feedback has been submitted. Thank you!";
    feedbackSubmitButton.classList.add("disable");
  }, false);
}

// Monitor the width of the Docs Agent widget.
let answerableSpan = document.getElementById('answerable-span');
//let rewriteButton = document.getElementById('rewrite-button');
const element = document.querySelector('#chat-border');

const resizeObserver = new ResizeObserver(entries => {
  for (const entry of entries) {
    const width = entry.contentRect.width;
    console.log('Element width changed to:', width);
    if (width < 520) {
      answerableSpan.classList.add("hidden");
    }else{
      if (answerableSpan.classList.contains("hidden")) {
        answerableSpan.classList.remove("hidden");
      }
    }
    if (width < 300) {
      rewriteButton.classList.add("hidden");
    }else{
      if (rewriteButton.classList.contains("hidden")) {
        rewriteButton.classList.remove("hidden");
      }
    }
  }
});

resizeObserver.observe(element);
