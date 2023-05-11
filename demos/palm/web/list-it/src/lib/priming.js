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

export const LIST_ITEMS_SEPARATOR = '\n'

export const LISTIT_PROMPT_COMPONENTS = {
  prefixes: [
    'You want to:',
    'Here is a list of tasks you might need to complete for that activity:',
    'Something additional to consider that newcomers may overlook:'
  ],
  examples: [
    [
      'go camping',
      [
        'Choose a campsite that suits your needs and preferences.',
        'Pack clothing suitable for the climate and activities you have planned.',
        'Bring a tent or other shelter that will keep you safe and comfortable.',
        'Plan and pack your meals, snacks, and cooking supplies.',
        'Bring enough water or a way to purify it.'
      ].join(LIST_ITEMS_SEPARATOR),
      'Food attracts wildlife! Never leave food, trash, or other scented products inside your tent.'
    ],
    [
      'buy a house',
      [
        'Consider the neighborhood, proximity to amenities, and commute times.',
        'Figure out how much space you need.',
        'Research mortgage options and get pre-approved before house hunting.',
        'Determine if there is sufficient parking for your needs.',
        'Consider the potential resale value of the property.'
      ].join(LIST_ITEMS_SEPARATOR),
      'When budgeting, make sure to account for unexpected expenses such as repairs or upgrades, as these can significantly impact the total cost.'
    ],
    [
      'plan a family vacation',
      [
        'Choose a destination that suits the interests of everyone in the family.',
        'Make a packing list and ensure that everyone has what they need for the trip.',
        "Plan how you will get to and from your destination and how you will get around once you're there.",
        'Research dining options and consider any dietary restrictions or preferences.',
        'Bring books, games, or other entertainment for the journey and downtime.'
      ].join(LIST_ITEMS_SEPARATOR),
      'When planning activities, remember to allow space for downtime so you can relax and recharge.'
    ],
    [
      'apply to a job',
      [
        'Research the company and the position you are applying for.',
        'Review the job requirements and ensure that you meet them.',
        'Ensure that your resume or CV is up-to-date and tailored to the position.',
        'Determine your salary requirements before the interview and be prepared to negotiate if necessary.',
        'Send a thank-you note or email after the interview to express your appreciation and reiterate your interest in the position.'
      ].join(LIST_ITEMS_SEPARATOR),
      "Make sure to look into the company's work culture and values, as this could have a large impact on your job satisfaction if you are hired."
    ],
    [
      'go on a first date',
      [
        "Choose a location that is convenient for both people and suits the vibe that you're after.",
        'Plan an activity that allows for conversation and helps you get to know each other.',
        'Dress appropriately for the activity and location.',
        'Prepare some conversation topics to avoid awkward silence and ensure interesting conversation.',
        'Put your phone on silent to avoid distractions during the date.'
      ].join(LIST_ITEMS_SEPARATOR),
      "Keep your expectations reasonable and remember that a first date is just the beginning of getting to know someone. Not all first dates lead to a second date or a relationship, and that's ok!"
    ]
  ]
}

/**
 * @typedef {Object} PromptComponents
 * @property {string[]} prefixes
 * @property {string[][]} examples
 * 
 * Each element in examples has a length of prefixes.length.
 * The value at prefixes[i] corresponds to the value at examples[<any>][i].
 */

/**
 * Construct a prompt string from a PromptComponents object and an input.
 * 
 * @param {PromptComponents} promptComponents The prompt components.
 * @param {string} input                      The input to the prompt.
 * @returns A prompt string.
 */
export const constructPrompt = (promptComponents, input) => {
  const lines = []
  if (promptComponents.preamble) {
    lines.push(promptComponents.preamble)
  }
  let currentPrefixIndex
  ;[...promptComponents.examples, [input]].forEach(values => {
    for (let i = 0; i < values.length; i++) {
      const prefix = promptComponents.prefixes[i]
      const value = values[i]
      if (prefix) {
        lines.push(`${prefix} ${value}`)
      } else {
        lines.push(value)
      }
      currentPrefixIndex = i
    }
  })
  if (currentPrefixIndex < promptComponents.prefixes.length - 1) {
    const nextPrefix = promptComponents.prefixes[currentPrefixIndex + 1]
    if (nextPrefix) {
      lines.push(nextPrefix)
    }
  }
  return lines.join('\n')
}
