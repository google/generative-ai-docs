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

import {IPromptDataItem} from '~/constants'

const adaptPromptData = (input: any) => {
  const promptData: IPromptDataItem['data'] = []

  Object.entries(input).forEach(([key, value]) => {
    if (value === '') return

    let rows: any = []

    // single value
    if (!Array.isArray(value)) {
      rows = [
        {
          cols: [
            {
              text: value
            }
          ]
        }
      ]
    } else if (Array.isArray(value)) {
      if (key === 'prefixes') {
        rows = [
          {
            cols: value.map((col, i) => {
              return {
                title: i === 0 ? 'Input' : 'Output',
                text: col !== '' ? col : 'No output prefix',
                background: 'cards',
                style: col !== '' ? 'bold' : 'italic'
              }
            })
          }
        ]
      } else {
        rows = value.map(row => {
          return {
            cols: row.map((col: any) => {
              return {
                text: col
              }
            })
          }
        })
      }
    }

    promptData.push({
      title: key.charAt(0).toUpperCase() + key.slice(1),
      rows
    })
  })

  return promptData
}

export default adaptPromptData
