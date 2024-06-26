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

import {post} from './firebase.config'

const NUM_CANDIDATES_DESIRED_PER_CALL = 8
const MAX_OUTPUT_TOKENS = 200
const SAFETY_THRESHOLD = 'BLOCK_ONLY_HIGH'

/**
 *
 * @param {string} prompt      The text prompt to send to the model.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an object that represents the model's response.
 */
export const predict = async (prompt, temperature) => {
  try {
    const response = await post({
      model: 'text-bison-001',
      method: 'generateText',
      prompt: {
        text: prompt
      },
      temperature: temperature,
      candidateCount: NUM_CANDIDATES_DESIRED_PER_CALL,
      maxOutputTokens: MAX_OUTPUT_TOKENS,
      safetySettings: [
        'HARM_CATEGORY_UNSPECIFIED',
        'HARM_CATEGORY_DEROGATORY',
        'HARM_CATEGORY_TOXICITY',
        'HARM_CATEGORY_VIOLENCE',
        'HARM_CATEGORY_SEXUAL',
        'HARM_CATEGORY_MEDICAL',
        'HARM_CATEGORY_DANGEROUS'
      ].map(category => ({
        category: category,
        threshold: SAFETY_THRESHOLD
      }))
    })
    return response.data
  } catch (error) {
    console.error(error)
    const result = {
      error: {
        code: error.code,
        message: error.message
      }
    }
    if (error.details && error.details.httpErrorCode) {
      result.error.httpStatusCode = error.details.httpErrorCode
      console.error(
        `HTTP request failed with status code ${result.error.httpStatusCode}`
      )
    }
    return result
  }
}
