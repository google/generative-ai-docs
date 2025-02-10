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

from datetime import datetime
import pytz
import os
import re
from uuid import UUID

"""Module to log interactions with the chatbot"""


# Save this question and response pair as a file.
def log_question_to_file(user_question: str, response: str, probability: str = "None"):
    filename = (
        str(user_question)
        .lower()
        .replace(" ", "-")
        .replace("?", "")
        .replace("'", "")
        .replace("`", "")
    )
    filename = re.sub("[^a-zA-Z0-9\-]", "", filename)
    if len(filename) > 64:
        filename = filename[:64]
    log_dir = "./logs/responses"
    log_filename = f"{log_dir}/{filename}.md"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write("# " + user_question.strip() + "\n\n")
        log_file.write(response.strip() + "\n\n")
        if probability != "None":
            log_file.write("(Answerable probability: " + str(probability) + ")\n")
        log_file.close()


# Log the answerable_probability score and question.
def log_answerable_probability(user_question: str, probability: str):
    log_dir = "./logs"
    answerable_list_filename = log_dir + "/answerable_logs.txt"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(answerable_list_filename, "a", encoding="utf-8") as log_file:
        log_file.write(
            str("{:.16f}".format(probability)) + "    " + user_question.strip() + "\n"
        )
        log_file.close()


# Save a detailed record of a question and response pair as a file for debugging.
def log_debug_info_to_file(
    uid: UUID,
    user_question: str,
    response: str,
    context: str,
    top_source_url: str,
    source_urls: str,
    probability: str = "None",
    server_url: str = "None",
):
    # Compose a filename
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))
    date_formatted = str(date.strftime("%Y-%m-%d-%H-%M-%S"))
    question_formatted = (
        str(user_question)
        .lower()
        .replace(" ", "-")
        .replace("?", "")
        .replace("'", "")
        .replace("`", "")
    )
    question_formatted = re.sub("[^a-zA-Z0-9\-]", "", question_formatted)
    if len(question_formatted) > 32:
        question_formatted = question_formatted[:32]
    filename = date_formatted + "-" + question_formatted + "-" + str(uid) + ".txt"
    # Set the directory location.
    debug_dir = "./logs/debugs"
    debug_filename = f"{debug_dir}/{filename}"
    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)
    with open(debug_filename, "w", encoding="utf-8") as debug_file:
        debug_file.write("UID: " + str(uid) + "\n")
        debug_file.write("DATE: " + str(date) + "\n")
        debug_file.write("SERVER URL: " + server_url.strip() + "\n")
        debug_file.write("\n")
        debug_file.write("TOP SOURCE URL: " + top_source_url.strip() + "\n")
        debug_file.write("ANSWERABLE PROBABILITY: " + str(probability) + "\n")
        debug_file.write("\n")
        debug_file.write("QUESTION: " + user_question.strip() + "\n\n")
        debug_file.write("RESPONSE:\n\n")
        debug_file.write(response.strip() + "\n\n")
        debug_file.write("CONTEXT:\n\n")
        debug_file.write(context.strip() + "\n\n")
        debug_file.write("SOURCE URLS:\n\n")
        debug_file.write(source_urls.strip() + "\n\n")
        debug_file.close()


# Save the like and dislike interactions to the file for debugging.
def log_feedback_to_file(uid: str, is_like, is_dislike):
    # Search the debugs directory.
    debug_dir = "./logs/debugs"
    target_string = str(uid) + ".txt"
    debug_filename = ""
    for root, dirs, files in os.walk(debug_dir):
        for file in files:
            if file.endswith(target_string):
                debug_filename = f"{debug_dir}/{file}"
    if debug_filename != "":
        with open(debug_filename, "a", encoding="utf-8") as debug_file:
            if is_like != None:
                debug_file.write("LIKE: " + str(is_like) + "\n")
            if is_dislike != None:
                debug_file.write("DISLIKE: " + str(is_dislike) + "\n")
            debug_file.close()


# Write captured debug logs into a CSV file.
def write_logs_to_csv_file(log_date: str = "None"):
    # Compose the output CSV filename.
    output_filename = "debug-info-all.csv"
    if log_date != "None":
        output_filename = "debug-info-" + str(log_date) + ".csv"
    # Write a header for this CSV file.
    log_dir = "./logs"
    out_csv_filename = log_dir + "/" + output_filename
    line = f"DATE, UID, QUESTION, PROBABILITY, TOP SOURCE URL, DEBUG LINK, FEEDBACK"
    with open(out_csv_filename, "w", encoding="utf-8") as csv_file:
        csv_file.write(line + "\n")
        csv_file.close()
    # Search the debugs directory.
    debug_dir = "./logs/debugs"
    debug_filename = ""
    for root, dirs, files in os.walk(debug_dir):
        for file in files:
            # Read all files if date is "None" else read files from the input date only.
            ok_to_read = False
            if file.endswith("txt"):
                ok_to_read = True
            if log_date != "None":
                if file.startswith(log_date):
                    ok_to_read = True
                else:
                    ok_to_read = False
            if ok_to_read:
                debug_filename = f"{debug_dir}/{file}"
                debug_record = ""
                # Open and read this debug information file.
                with open(debug_filename, "r", encoding="utf-8") as debug_file:
                    debug_record = debug_file.readlines()
                    debug_file.close()
                uid = ""
                date = ""
                server_url = "None"
                top_source_url = ""
                probability = ""
                question = ""
                like = "None"
                dislike = "None"
                filename = str(file)
                # Scan the lines from thi debug info and extract fields.
                for line in debug_record:
                    match_uid = re.search(r"^UID:\s+(.*)$", line)
                    match_date = re.search(r"^DATE:\s+(.*)$", line)
                    match_server_url = re.search(r"^SERVER URL:\s+(.*)$", line)
                    match_top_url = re.search(r"^TOP SOURCE URL:\s+(.*)$", line)
                    match_prob = re.search(r"^ANSWERABLE PROBABILITY:\s+(.*)$", line)
                    match_question = re.search(r"^QUESTION:\s+(.*)$", line)
                    match_like = re.search(r"^LIKE:\s+(.*)$", line)
                    match_dislike = re.search(r"^DISLIKE:\s+(.*)$", line)
                    # Extract fields.
                    if match_uid:
                        uid = match_uid.group(1)
                    elif match_date:
                        date = match_date.group(1)
                    elif match_server_url:
                        server_url = match_server_url.group(1)
                    elif match_top_url:
                        top_source_url = match_top_url.group(1)
                    elif match_prob:
                        probability = match_prob.group(1)
                    elif match_question:
                        question = match_question.group(1)
                    elif match_like:
                        like = match_like.group(1)
                    elif match_dislike:
                        dislike = match_dislike.group(1)
                # Write a short version of this debug information to the CSV file.
                debug_file_link = filename
                if server_url != "None":
                    debug_file_link = server_url + "debugs/" + filename
                feedback = "None"
                if like == "True":
                    feedback = "Like"
                elif dislike == "True":
                    feedback = "Dislike"
                log_debug_info_to_csv_file(
                    output_filename=output_filename,
                    date=date,
                    uid=uid,
                    question=question,
                    probability=probability,
                    top_source_url=top_source_url,
                    debug_file_link=debug_file_link,
                    feedback=feedback,
                )


# Save the short version of debug information into a CSV file.
def log_debug_info_to_csv_file(
    output_filename: str,
    date: str,
    uid: str,
    question: str,
    probability: str = "None",
    top_source_url: str = "None",
    debug_file_link: str = "None",
    feedback: str = "None",
):
    log_dir = "./logs"
    log_filename = log_dir + "/" + str(output_filename)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    question_formatted = str(question).lower().replace(",", " ").replace(";", "")
    line = f"{date}, {uid}, {question_formatted}, {probability}, {top_source_url}, {debug_file_link}, {feedback}"
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(line + "\n")
        log_file.close()


# Print and log the question and response.
def log_question(
    uid,
    user_question: str,
    response: str,
    probability: str = "None",
    save: bool = True,
    logs_to_markdown: str = "False",
):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))
    print("UID: " + str(uid))
    print("Question: " + user_question.strip() + "\n")
    print("Response:")
    print(response.strip() + "\n")
    # For the AQA model, also print the response's answerable_probability
    if probability != "None":
        print("Answerable probability: " + str(probability) + "\n")
    if save:
        log_dir = "./logs"
        log_filename = log_dir + "/chatui_logs.txt"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(
                "[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n"
            )
            log_file.write("# " + user_question.strip() + "\n\n")
            log_file.write(response.strip() + "\n\n")
            if probability != "None":
                log_file.write("Answerable probability: " + str(probability) + "\n\n")
            log_file.close()
        if probability != "None":
            # Track the answerable_probability scores.
            log_answerable_probability(user_question, probability)
        if logs_to_markdown == "True":
            log_question_to_file(user_question, response, probability)


def log_like(is_like, uid, save: bool = True):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))
    print()
    print("UID: " + str(uid))
    print("Like: " + str(is_like))
    if save:
        log_dir = "./logs"
        log_filename = log_dir + "/chatui_logs.txt"
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(
                "[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n"
            )
            log_file.write("Like: " + str(is_like) + "\n\n")
            log_file.close()


def log_dislike(is_dislike, uid, save: bool = True):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))
    print()
    print("UID: " + str(uid))
    print("Dislike: " + str(is_dislike))
    if save:
        log_dir = "./logs"
        log_filename = log_dir + "/chatui_logs.txt"
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(
                "[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n"
            )
            log_file.write("Disike: " + str(is_dislike) + "\n\n")
            log_file.close()
