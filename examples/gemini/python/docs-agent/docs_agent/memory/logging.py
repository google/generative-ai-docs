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

"""Module to log interactions with the chatbot"""


# Log the question and response to the server's log file.
def log_question(uid, user_question: str, response: str, probability: str = "None", save: str = "txt"):
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
    if save == "txt":
        with open("chatui_logs.txt", "a", encoding="utf-8") as log_file:
            log_file.write(
                "[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n"
            )
            log_file.write("# " + user_question.strip() + "\n\n")
            log_file.write(response.strip() + "\n\n")
            if probability != "None":
                log_file.write("Answerable probability: " + str(probability) + "\n\n")
            log_file.close()
        # Added to track the answerable_probability scores.
        if probability != "None":
            with open("answerable_logs.txt", "a", encoding="utf-8") as log2_file:
                log2_file.write(
                    str("{:.16f}".format(probability))
                    + "    "
                    + user_question.strip()
                    + "\n"
                )
                log2_file.close()

def log_like(is_like, uid, save: str = "txt"):
    date_format = "%m/%d/%Y %H:%M:%S %Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone("US/Pacific"))
    print("UID: " + str(uid))
    print("Like: " + str(is_like))
    if save == "txt":
        with open("chatui_logs.txt", "a", encoding="utf-8") as log_file:
            log_file.write(
                "[" + date.strftime(date_format) + "][UID " + str(uid) + "]\n"
            )
            log_file.write("Like: " + str(is_like) + "\n\n")
            log_file.close()
