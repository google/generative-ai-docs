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
import {
  constructPrompt,
  LISTIT_PROMPT_COMPONENTS,
  LIST_ITEMS_SEPARATOR
} from './priming'

const MODEL_TEMPERATURE = 0.25


/**
 * @typedef {Object} TextPrompt
 * @property {string} text The text to continue.
 */

/**
 * Generate a continuation of a text.
 * 
 * @param {TextPrompt} prompt  The TextPrompt to send to the model.
 * @param {number} temperature The model temperature.
 * @returns A Promise object that, if fulfilled, returns an object that represents the model's response.
 */
const predict = async (prompt, temperature = MODEL_TEMPERATURE) => {
  try {
    const response = await post({
      model: 'text-bison-001',
      method: 'generateText',
      prompt: {
        text: prompt
      },
      temperature: temperature
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
    }
    return result
  }
}

export const getListAndTip = async input => {
  const prompt = constructPrompt(LISTIT_PROMPT_COMPONENTS, input.trim())
  const llmResult = await predict(prompt)

  if (llmResult.error) {
    llmResult.error.query = input
    return {
      title: input,
      items: [],
      tip: '',
      error: llmResult.error
    }
  }

  const outputString = llmResult.candidates[0].output
  const listAndTip = postprocess(
    parseListAndTip(
      outputString,
      LISTIT_PROMPT_COMPONENTS,
      LIST_ITEMS_SEPARATOR
    )
  )

  return {
    title: input,
    items: listAndTip.list,
    tip: listAndTip.tip
  }
}

const parseListAndTip = (
  outputString,
  promptComponents,
  listItemsSeparator
) => {
  const listAndTip = outputString.split(promptComponents.prefixes[0])[0]
  const list = listAndTip
    .split(promptComponents.prefixes[2])[0]
    .split(':')
    .slice(-1)[0]
    .split(listItemsSeparator)
    .map(item => item.trim())
  const tip = listAndTip.split(':').slice(-1)[0].trim()

  return {
    list: list,
    tip: tip
  }
}

const postprocess = listAndTip => {
  const list = listAndTip['list']
  const tip = listAndTip['tip']

  // Add additional postprocessing logic here, if necessary
  const cleanedList = list.map(item => item.trim()).filter(item => item)
  const cleanedTip = tip.trim()

  return {
    list: cleanedList,
    tip: cleanedTip
  }
}
