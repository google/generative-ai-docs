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

import {PREFIX_DELIMITER} from './priming'
import {ERROR_MESSAGE, NO_RESULTS_MESSAGE} from '~/constants'

export const parseOutputs = (llmResponse, promptComponents) => {
  if (llmResponse.error) {
    return [ERROR_MESSAGE]
  }
  const results = []

  try {
    llmResponse.candidates.forEach(candidate => {
      results.push(
        candidate.output
          .split(promptComponents.prefixes[0])[0]
          .split(new RegExp(`\\${PREFIX_DELIMITER}(.*)`))
          .slice(-1)[0]
          .trim()
      )
    })
  } catch (error) {
    console.error(
      'No results generated (see API response below).\n',
      llmResponse
    )
    return [NO_RESULTS_MESSAGE]
  }
  return results
}
