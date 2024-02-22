#
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Chatbot web service for Docs Agent"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    json,
)
import markdown
import markdown.extensions.fenced_code
from bs4 import BeautifulSoup
import urllib
import os
from datetime import datetime
from pytz import timezone
import pytz
import uuid
from scripts import read_config

from modules.chroma import Format
from docs_agent import DocsAgent


# Read the configuration file
config = read_config.ReadConfig()
# Create the 'rewrites' directory if it does not exist.
rewrites_dir = "rewrites"
is_exist = os.path.exists(rewrites_dir)
if not is_exist:
    os.makedirs(rewrites_dir)

product = config.returnConfigValue("product_name")
bp = Blueprint("chatui", __name__)
docs_agent = DocsAgent()


@bp.route("/", methods=["GET", "POST"])
def index():
    server_url = request.url_root.replace("http", "https")
    return render_template("chatui/index.html", product=product, server_url=server_url)


@bp.route("/like", methods=["GET", "POST"])
def like():
    if request.method == "POST":
        json_data = json.loads(request.data)
        is_like = json_data.get("like")
        uuid_found = json_data.get("uuid")
        log_like(is_like, str(uuid_found).strip())
        return "OK"
    else:
        return redirect(url_for("chatui.index"))


@bp.route("/rewrite", methods=["GET", "POST"])
def rewrite():
    if request.method == "POST":
        json_data = json.loads(request.data)
        user_id = json_data.get("user_id")
        question_captured = json_data.get("question")
        original_response = json_data.get("original_response")
        rewrite_captured = json_data.get("rewrite")
        date_format = "%m%d%Y-%H%M%S"
        date = datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone("US/Pacific"))
        print("[" + date.strftime(date_format) + "] A user has submitted a rewrite.")
        print("Submitted by: " + user_id + "\n")
        print("# " + question_captured.strip() + "\n")
        print("## Original response\n")
        print(original_response.strip() + "\n")
        print("## Rewrite\n")
        print(rewrite_captured + "\n")
        filename = (
            rewrites_dir
            + "/"
            + question_captured.strip()
            .replace(" ", "-")
            .replace("?", "")
            .replace("'", "")
            .lower()
            + "-"
            + date.strftime(date_format)
            + ".md"
        )
        with open(filename, "w", encoding="utf-8") as file:
            file.write("Submitted by: " + user_id + "\n\n")
            file.write("# " + question_captured.strip() + "\n\n")
            file.write("## Original response\n\n")
            file.write(original_response.strip() + "\n\n")
            file.write("## Rewrite\n\n")
            file.write(rewrite_captured + "\n")
            file.close()
        return "OK"
    else:
        return redirect(url_for("chatui.index"))


# Render a response page when the user asks a question
# using input text box.
@bp.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        question = request.form["question"]
        return ask_model(question)
    else:
        return redirect(url_for("chatui.index"))


# Render a response page when the user clicks a question
# from the related questions list.
@bp.route("/question/<ask>", methods=["GET", "POST"])
def question(ask):
    if request.method == "GET":
        question = urllib.parse.unquote_plus(ask)
        return ask_model(question)
    else:
        return redirect(url_for("chatui.index"))


# Construct a set of prompts using the user question, send the prompts to
# the lanaguage model, receive responses, and present them into a page.
def ask_model(question):
    ### PROMPT 1: AUGMENT THE USER QUESTION WITH CONTEXT.
    # 1. Use the question to retrieve a list of related contents from the database.
    # 2. Convert the list of related contents into plain Markdown text (context).
    # 3. Add the custom condition text to the context.
    # 4. Send the prompt (condition + context + question) to the language model.
    query_result = docs_agent.query_vector_store(question)
    context = query_result.fetch_formatted(Format.CONTEXT)
    context_with_instruction = docs_agent.add_instruction_to_context(context)
    if docs_agent.check_if_aqa_is_used():
        response = docs_agent.ask_aqa_model(question)
    elif "gemini" in docs_agent.get_language_model_name():
        response = docs_agent.ask_content_model_with_context(
            context_with_instruction, question
        )
    else:
        response = docs_agent.ask_text_model_with_context(
            context_with_instruction, question
        )

    ### PROMPT 2: FACT-CHECK THE PREVIOUS RESPONSE.
    if "gemini" in docs_agent.get_language_model_name():
        fact_checked_response = docs_agent.ask_content_model_to_fact_check(
            context_with_instruction, response
        )
    else:
        fact_checked_response = docs_agent.ask_text_model_to_fact_check(
            context_with_instruction, response
        )

    ### PROMPT 3: GET 5 RELATED QUESTIONS.
    # 1. Use the response from Prompt 1 as context and add a custom condition.
    # 2. Prepare a new question asking the model to come up with 5 related questions.
    # 3. Ask the language model with the new question.
    # 4. Parse the model's response into a list in HTML format.
    new_condition = "Read the context below and answer the user's question at the end."
    new_context_with_instruction = docs_agent.add_custom_instruction_to_context(
        new_condition, response
    )
    new_question = (
        "What are 5 questions developers might ask after reading the context?"
    )
    new_response = markdown.markdown(
        docs_agent.ask_text_model_with_context(
            new_context_with_instruction, new_question
        )
    )
    related_questions = parse_related_questions_response_to_html_list(new_response)

    ### RETRIEVE SOURCE URLS.
    # - Construct clickable URLs using the returned related contents above.
    # - Extract the URL of the top related content for the fact-check message.
    clickable_urls = markdown.markdown(
        query_result.fetch_formatted(Format.CLICKABLE_URL)
    )
    fact_check_url = ""
    if docs_agent.check_if_aqa_is_used() and docs_agent.get_db_type() == "ONLINE_STORAGE":
        aqa_response_url = docs_agent.get_aqa_response_url()
        fact_check_url = (
            '<a href="' + aqa_response_url + '">' + aqa_response_url + "</a>"
        )
    else:
        fact_check_url = markdown.markdown(
            query_result.fetch_nearest_formatted(Format.CLICKABLE_URL)
        )

    ### PREPARE OTHER ELEMENTS NEEDED BY UI.
    # - Create a uuid for this request.
    # - (Optional) Prepare the AQA model's JSON response into HTML for rendering.
    # - Convert the context returned from the database into HTML for rendering.
    # - Convert the first response from the model into HTML for rendering.
    # - Convert the fact-check response from the model into HTML for rendering.
    # - A workaround to get the server's URL to work with the rewrite and like features.
    new_uuid = uuid.uuid1()
    aqa_response_in_html = ""
    if docs_agent.check_if_aqa_is_used():
        aqa_response_json = docs_agent.get_saved_aqa_response_json()
        if aqa_response_json:
            aqa_response_in_html = "Grounding attributions:<br/><br/>"
            aqa_response_in_html += str(aqa_response_json.answer.grounding_attributions)
            aqa_response_in_html += "<br/><br/>Answerable probability: "
            aqa_response_in_html += str(aqa_response_json.answerable_probability)
    context_in_html = markdown.markdown(context, extensions=["fenced_code"])
    response_in_html = markdown.markdown(response, extensions=["fenced_code"])
    fact_checked_response_in_html = markdown.markdown(fact_checked_response)
    server_url = request.url_root.replace("http", "https")

    ### LOG THIS REQUEST.
    log_question(new_uuid, question, response)

    return render_template(
        "chatui/index.html",
        question=question,
        context_in_html=context_in_html,
        response=response,
        response_in_html=response_in_html,
        clickable_urls=clickable_urls,
        fact_checked_response_in_html=fact_checked_response_in_html,
        fact_check_url=fact_check_url,
        related_questions=related_questions,
        product=product,
        server_url=server_url,
        uuid=new_uuid,
        aqa_response_in_html=aqa_response_in_html,
    )


# Parse a response containing a list of related questions from the language model
# and convert it into an HTML-based list.
def parse_related_questions_response_to_html_list(response):
    soup = BeautifulSoup(response, "html.parser")
    for item in soup.find_all("li"):
        # In case there are code tags, remove the tag and just replace with
        # plain text
        if item.find("code"):
            text = item.find("code").text
            item.code.replace_with(text)
        # In case there are <p> tags within the <li> strip <p>
        if item.find("p"):
            text = item.find("p").text
            link = soup.new_tag(
                "a",
                href=url_for("chatui.question", ask=urllib.parse.quote_plus(text)),
            )
            link.string = text
            item.string = ""
            item.append(link)
        if item.string is not None:
            link = soup.new_tag(
                "a",
                href=url_for(
                    "chatui.question", ask=urllib.parse.quote_plus(item.string)
                ),
            )
            link.string = item.string
            item.string = ""
            item.append(link)
    return soup


# Log the question and response to the server's log file.
def log_question(uid, user_question, response):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone("US/Pacific"))
    print("UID: " + str(uid))
    print("Question: " + user_question.strip() + "\n")
    print("Response:")
    print(response.strip() + "\n")
    if docs_agent.check_if_aqa_is_used():
        aqa_response = docs_agent.get_saved_aqa_response_json()
        try:
            probability = aqa_response.answerable_probability
        except:
            probability = 0.0
        print("Answerable probability: " + str(probability) + "\n")
    with open("chatui_logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write("[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n")
        log_file.write("# " + user_question.strip() + "\n\n")
        log_file.write(response.strip() + "\n\n")
        if docs_agent.check_if_aqa_is_used():
            log_file.write("Answerable probability: " + str(probability) + "\n\n")
        log_file.close()


def log_like(is_like, uid):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone("US/Pacific"))
    print("UID: " + str(uid))
    print("Like: " + str(is_like))
    with open("chatui_logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write("[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n")
        log_file.write("Like: " + str(is_like) + "\n\n")
        log_file.close()
