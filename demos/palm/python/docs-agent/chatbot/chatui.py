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
from bs4 import BeautifulSoup
import urllib
import os
from datetime import datetime
from pytz import timezone
import pytz
import uuid
from scripts import read_config

from chroma import Format
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


@bp.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":
        uuid_value = uuid.uuid1()
        question_captured = request.form["question"]
        query_result = docs_agent.query_vector_store(question_captured)
        context = markdown.markdown(query_result.fetch_formatted(Format.CONTEXT))
        context_with_prefix = docs_agent.add_instruction_to_context(context)
        response_in_markdown = docs_agent.ask_text_model_with_context(
            context_with_prefix, question_captured
        )
        if response_in_markdown is None:
            response_in_markdown = (
                "The PaLM API is not able to answer this question at the moment. "
                "Try to rephrase the question and ask again."
            )
        response_in_html = markdown.markdown(response_in_markdown)
        metadatas = markdown.markdown(
            query_result.fetch_formatted(Format.CLICKABLE_URL)
        )
        fact_checked_answer_in_markdown = docs_agent.ask_text_model_to_fact_check(
            context_with_prefix, response_in_markdown
        )
        if fact_checked_answer_in_markdown is None:
            fact_checked_answer_in_markdown = (
                "The PaLM API is not able to answer this question at the moment. "
                "Try to rephrase the question and ask again."
            )
        fact_checked_answer_in_html = markdown.markdown(fact_checked_answer_in_markdown)
        new_question = (
            "What are 5 questions developers might ask after reading the context?"
        )
        related_questions = markdown.markdown(
            docs_agent.ask_text_model_with_context(response_in_markdown, new_question)
        )
        soup = BeautifulSoup(related_questions, "html.parser")
        for item in soup.find_all("li"):
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
        related_questions = soup
        fact_link = markdown.markdown(
            query_result.fetch_nearest_formatted(Format.CLICKABLE_URL)
        )
        server_url = request.url_root.replace("http", "https")
        # Log the question and response to the log file.
        log_question(uuid_value, question_captured, response_in_markdown)
        return render_template(
            "chatui/index.html",
            question=question_captured,
            context=context,
            context_with_prefix=context_with_prefix,
            response_in_markdown=response_in_markdown,
            response_in_html=response_in_html,
            product=product,
            metadatas=metadatas,
            fact_checked_answer=fact_checked_answer_in_html,
            fact_link=fact_link,
            related_questions=related_questions,
            server_url=server_url,
            uuid=uuid_value,
        )
    else:
        return redirect(url_for("chatui.index"))


@bp.route("/question/<ask>", methods=["GET", "POST"])
def question(ask):
    if request.method == "GET":
        uuid_value = uuid.uuid1()
        question_captured = urllib.parse.unquote_plus(ask)
        query_result = docs_agent.query_vector_store(question_captured)
        context = markdown.markdown(query_result.fetch_formatted(Format.CONTEXT))
        context_with_prefix = docs_agent.add_instruction_to_context(context)
        response_in_markdown = docs_agent.ask_text_model_with_context(
            context_with_prefix, question_captured
        )
        if response_in_markdown is None:
            response_in_markdown = (
                "The PaLM API is not able to answer this question at the moment. "
                "Try to rephrase the question and ask again."
            )
        response_in_html = markdown.markdown(response_in_markdown)
        metadatas = markdown.markdown(
            query_result.fetch_formatted(Format.CLICKABLE_URL)
        )
        fact_checked_answer_in_markdown = docs_agent.ask_text_model_to_fact_check(
            context_with_prefix, response_in_markdown
        )
        if fact_checked_answer_in_markdown is None:
            fact_checked_answer_in_markdown = (
                "The PaLM API is not able to answer this question at the moment. "
                "Try to rephrase the question and ask again."
            )
        fact_checked_answer_in_html = markdown.markdown(fact_checked_answer_in_markdown)
        new_question = (
            "What are 5 questions developers might ask after reading the context?"
        )
        related_questions = markdown.markdown(
            docs_agent.ask_text_model_with_context(response_in_markdown, new_question)
        )
        soup = BeautifulSoup(related_questions, "html.parser")
        for item in soup.find_all("li"):
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
        related_questions = soup
        fact_link = markdown.markdown(
            query_result.fetch_nearest_formatted(Format.CLICKABLE_URL)
        )
        server_url = request.url_root.replace("http", "https")
        # Log the question and response to the log file.
        log_question(uuid_value, question_captured, response_in_markdown)
        return render_template(
            "chatui/index.html",
            question=question_captured,
            context=context,
            context_with_prefix=context_with_prefix,
            response_in_markdown=response_in_markdown,
            response_in_html=response_in_html,
            product=product,
            metadatas=metadatas,
            fact_checked_answer=fact_checked_answer_in_html,
            fact_link=fact_link,
            related_questions=related_questions,
            server_url=server_url,
            uuid=uuid_value,
        )
    else:
        return redirect(url_for("chatui.index"))


# Log the question and response to the server's log file.
def log_question(uid, user_question, response):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone("US/Pacific"))
    print("UID: " + str(uid))
    print("Question: " + user_question.strip() + "\n")
    print("Response:")
    print(response.strip() + "\n")
    with open("chatui_logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write("[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n")
        log_file.write("# " + user_question.strip() + "\n\n")
        log_file.write(response.strip() + "\n\n")
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
