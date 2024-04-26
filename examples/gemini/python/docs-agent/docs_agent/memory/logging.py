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

"""Module to log interactions with the chatbot"""


# Save this question and response pair as a file.
def log_question_to_file(user_question: str, response: str, probability: str = "None"):
    filename = str(user_question).lower().replace(" ", "-").replace("?", "")
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


# Print and log the question and response.
def log_question(
    uid,
    user_question: str,
    response: str,
    probability: str = "None",
    save: str = "True",
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
    if save == "True":
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


def log_like(is_like, uid, save: str = "True"):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))
    print("UID: " + str(uid))
    print("Like: " + str(is_like))
    if save == "True":
        log_dir = "./logs"
        log_filename = log_dir + "/chatui_logs.txt"
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(
                "[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n"
            )
            log_file.write("Like: " + str(is_like) + "\n\n")
            log_file.close()
