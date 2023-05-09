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
import {QUICKPROMPT_PROMPT_COMPONENTS} from './priming'

const MODEL_TEMPERATURE = 0.25
const NUM_CANDIDATE_RESPONSES = 8

const getGuess = async (prompt, temperature = MODEL_TEMPERATURE) => {
  try {
    const result = await post({
      model: 'chat-bison-001',
      method: 'generateMessage',
      prompt: prompt,
      temperature: temperature,
      candidateCount: NUM_CANDIDATE_RESPONSES
    })

    let candidateGuesses = []

    result.data.candidates.forEach(candidate => {
      candidateGuesses.push(
        candidate.content.split('\n')[0].split('\r')[0].trim()
      )
    })

    // Filter model responses that do not contain an item enclosed in square brackets,
    // as well as responses that contain more than one bracketed item
    candidateGuesses = candidateGuesses.filter(candidate => {
      return (candidate.match(/\[[^\[\]]*\]/gm) || []).length === 1
    })

    if (candidateGuesses.length > 0) {
      // Prioritize responses that contain a question mark so it feels like a conversation
      const candidateIndex = candidateGuesses.findIndex(candidate =>
        candidate.includes('?')
      )
      if (candidateIndex !== -1) {
        return {
          text: candidateGuesses[candidateIndex]
        }
      }
      return {
        text: candidateGuesses[0]
      }
    } else {
      return {error: 'No valid response was generated.'}
    }
  } catch (error) {
    console.error(error)
    return {error: error.message}
  }
}

export const performTurn = async convo => {
  const messages = convo.map((content, i) => ({author: `${i % 2}`, content}))

  return getGuess({
    context: QUICKPROMPT_PROMPT_COMPONENTS.context,
    examples: QUICKPROMPT_PROMPT_COMPONENTS.examples,
    messages: messages
  })
}
