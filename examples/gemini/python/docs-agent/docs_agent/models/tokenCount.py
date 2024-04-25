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
from docs_agent.utilities import config

# Per the docs 60-80 words ~= 100 tokens
lower_word_limit = 60 / 100
higher_word_limit = 80 / 100

# Per the docs 4 characters ~= 1 token
lower_char_limit = 4
higher_char_limit = 4

"""Estimate or return token count for a given string"""


# Hard coded, replace with function for model selection
# This value should be set in config.yaml file to avoid unecessary API calls as
# it will mostly remain static until a different model is used
# todo: clean these functions
# def returnMaxInputTokenModelAPI() -> float:
#     model = "models/gemini-pro"
#     maxInputToken = model.input_token_limit
#     max_context_tokens_api = maxInputToken - max_token_count_api
#     print("Max input token: " + str(maxInputToken))
#     max_context_tokens = maxInputToken - max_token_count_prompt
#     print("Max input token removing prompt: " + str(max_context_tokens))
#     print("Max input token removing prompt API: " + str(max_context_tokens_api))

#     number_of_context_per_prompt = 3

#     # Remove 5 tokens to give additional token buffer
#     max_chunk_size = max_context_tokens / number_of_context_per_prompt - 5
#     print("Max chunk size is: " + str(max_chunk_size))
#     max_chunk_size_api = max_context_tokens_api / number_of_context_per_prompt - 5
#     print("Max chunk size is API: " + str(max_chunk_size_api))
#     max_token_count_prompt = estimateTokensAverage(CONDITION_TEXT) + 5
#     max_token_count_api = palm.tokenCount(CONDITION_TEXT) + 5

#     return max_token_count_api


# def returnMaxInputTokenModelEstimate() -> float:
# #    model = "models/gemini-pro"
#     maxInputToken = model.input_token_limit
#     max_context_tokens_api = maxInputToken - max_token_count_api
#     print("Max input token: " + str(maxInputToken))
#     max_context_tokens = maxInputToken - max_token_count_prompt
#     print("Max input token removing prompt: " + str(max_context_tokens))
#     print("Max input token removing prompt API: " + str(max_context_tokens_api))

#     number_of_context_per_prompt = 3

#     # Remove 5 tokens to give additional token buffer
#     max_chunk_size = max_context_tokens / number_of_context_per_prompt - 5
#     print("Max chunk size is: " + str(max_chunk_size))
#     max_chunk_size_api = max_context_tokens_api / number_of_context_per_prompt - 5
#     print("Max chunk size is API: " + str(max_chunk_size_api))
#     max_token_estimate = estimateTokensAverage(CONDITION_TEXT) + 5

#     return max_token_estimate


# Function to return a character count of a string
def countChars(input):
    charCount = len(input)
    return charCount


# Function to return a word count of a string
def countWords(input):
    wordCount = len(input.split())
    return wordCount


# Function to estimate token count based on characters
def estimateTokensFromChars(input, lower_char_limit, higher_char_limit):
    char_count = countChars(input)
    lower_token_estimate = char_count / lower_char_limit
    higher_token_estimate = char_count / higher_char_limit
    # Estimate is multiplied by 1.27 to more closely match samples
    average_token_estimate = ((lower_token_estimate + higher_token_estimate) / 2) * 1.27
    return average_token_estimate


# Function to estimate token count based on words
def estimateTokensFromWords(input, lower_word_limit, higher_word_limit):
    word_count = countWords(input)
    lower_token_estimate = word_count / lower_word_limit
    higher_token_estimate = word_count / higher_word_limit
    # Estimate is multiplied by 1.55 to more closely match samples
    average_token_estimate = (
        ((lower_token_estimate * 1.1) + higher_token_estimate) / 2
    ) * 1.55
    return average_token_estimate


# Function to return the average between the character and word estimate
def estimateTokensAverage(input):
    char_estimate = estimateTokensFromChars(input, lower_char_limit, higher_char_limit)
    word_estimate = estimateTokensFromWords(input, lower_word_limit, higher_word_limit)
    average_token_estimate = (char_estimate + word_estimate) / 2
    return average_token_estimate


# Function to return the highest token count between estimateTokensFromChars and
# estimateTokensFromWords. This improved accuracy to what PaLM returns
def returnHighestTokens(input):
    char_estimate = estimateTokensFromChars(input, lower_char_limit, higher_char_limit)
    word_estimate = estimateTokensFromWords(input, lower_word_limit, higher_word_limit)
    if char_estimate >= word_estimate:
        return char_estimate
    else:
        return word_estimate