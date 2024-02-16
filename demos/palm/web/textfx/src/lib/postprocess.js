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

import {ERROR_MESSAGE, NO_RESULTS_MESSAGE} from '~/constants'

export const postprocess = (macroName, inputs, outputs) => {
  if (
    outputs[0] &&
    (outputs[0].includes(ERROR_MESSAGE) ||
      outputs[0].includes(NO_RESULTS_MESSAGE))
  ) {
    return outputs
  }

  let candidates

  if (!['pov', 'scene', 'unfold'].includes(macroName)) {
    // If a newline appears in the output, ignore everything after it
    // (unless the output is from POV, Scene, or Unfold)
    candidates = outputs.map(item => item.split('\n')[0].trim())
  } else {
    candidates = flatten(outputs)
  }

  candidates = removeEmptyStrings(deduplicate(candidates))
  let results

  switch (macroName) {
    case 'simile': {
      results = processSimileOutputs(candidates)
      break
    }
    case 'explode': {
      results = processExplodeOutputs(inputs[0], candidates)
      break
    }
    case 'unexpect': {
      results = processUnexpectOutputs(candidates)
      break
    }
    case 'chain': {
      results = processChainOutputs(inputs[0], candidates)
      break
    }
    case 'pov': {
      results = processPOVOutputs(inputs[0], candidates)
      break
    }
    case 'alliteration': {
      results = processAlliterationOutputs(inputs, candidates)
      break
    }
    case 'acronym': {
      results = processAcronymOutputs(inputs[0], candidates)
      break
    }
    case 'fuse': {
      results = processFuseOutputs(candidates)
      break
    }
    case 'scene': {
      results = processSceneOutputs(candidates)
      break
    }
    case 'unfold': {
      results = processUnfoldOutputs(inputs[0], candidates)
      break
    }
  }

  if (results.length > 0) {
    return results
  }

  return [NO_RESULTS_MESSAGE]
}

// For macros where a single model output contains a series of items separated by newlines
// (i.e., POV, Scene, Unfold), combine all items across all outputs into a single list.
const flatten = outputs => {
  return outputs
    .map(item => item.split('\n'))
    .flat()
    .map(item => item.trim())
}

// Remove duplicates
const deduplicate = outputs => {
  return [...new Set(outputs)]
}

// Remove duplicates in an array of strings, but for each element
// only the segment occurring BEFORE the specified character is evaluated
const deduplicateBasedOnSegmentBeforeChar = (outputs, char) => {
  const segments = []
  outputs.forEach(item => {
    segments.push(item.split(char)[0].trim())
  })

  const deduplicatedSegments = [...new Set(segments)]

  const results = []
  deduplicatedSegments.forEach(item => {
    results.push(outputs[outputs.findIndex(str => str.includes(item))])
  })

  return results
}

// Remove duplicates in an array of strings, but for each element,
// only the segment occurring AFTER the specified character is evaluated
const deduplicateBasedOnSegmentAfterChar = (outputs, char) => {
  const segments = []
  outputs.forEach(item => {
    try {
      segments.push(item.split(new RegExp(`\\${char}(.*)`))[1].trim())
    } catch {
      // Do nothing
    }
  })

  const deduplicatedSegments = [...new Set(segments)]

  const results = []
  deduplicatedSegments.forEach(item => {
    results.push(outputs[outputs.findIndex(str => str.includes(item))])
  })

  return results
}

// Remove empty strings
const removeEmptyStrings = outputs => {
  return outputs.filter(item => item)
}

// Shuffle outputs using the Fisher–Yates algorithm
const shuffle = array => {
  let currentIndex = array.length
  let currentItem
  let randomIndex

  while (currentIndex) {
    randomIndex = Math.floor(Math.random() * currentIndex--)
    currentItem = array[currentIndex]
    array[currentIndex] = array[randomIndex]
    array[randomIndex] = currentItem
  }

  return array
}

/*
// Divide outputs into equal-sized groups
const chunk = (array, chunkSize) => {
  const numChunks = Math.ceil(array.length / chunkSize)
  const chunks = [...Array(numChunks)].map((value, index) => {
    return array.slice(index * chunkSize, (index + 1) * chunkSize)
  })
  return chunks
}
*/

const processSimileOutputs = outputs => {
  // Remove candidates that don't contain "like" or "as"
  return outputs.filter(item => item.includes('like') || item.includes('as'))
}

const processExplodeOutputs = (input, outputs) => {
  // De-duplicate candidates based on the segment that occurs before the initial parenthesis
  return deduplicateBasedOnSegmentBeforeChar(outputs, '(').filter(
    item => !item.split('(')[0].includes(input.toLowerCase().trim())
  )
}

const processUnexpectOutputs = outputs => {
  return shuffle(outputs)
}

const processChainOutputs = (input, outputs) => {
  const chains = outputs.map(item => item.split(',').map(item => item.trim()))
  return (
    chains
      // Remove candidates that contain repeated elements
      .map(chain => [...new Set(chain)])
      // Remove candidates that do not (1) start with the input query and (2) contain exactly 8 items
      .filter(
        chain => chain[0] === input.toLowerCase().trim() && chain.length == 8
      )
      .map(chain => chain.join(', '))
  )
}

const processPOVOutputs = (input, outputs) => {
  return shuffle(
    outputs
      // Remove candidates that don't contain the input query
      .filter(item => item.toLowerCase().includes(input.toLowerCase()))
      // Clip everything after the end punctuation
      .map(item => {
        item = `${item.split('.')[0].trim()}.`
        if (item.includes('?')) {
          return `${item.split('?')[0].trim()}?`
        } else if (item.includes('!')) {
          return `${item.split('!')[0].trim()}!`
        }
        return item
      })
  )
}

const processAlliterationOutputs = (inputs, outputs) => {
  let results = removeEmptyStrings(
    // Combine all words across all model outputs into a single array
    // Remove duplicates
    [
      ...new Set(
        outputs.map(item => item.split(',').map(item => item.trim())).flat()
      )
    ]
      // Remove items that contain anything other than alphanumeric characters, spaces, or hyphens
      .filter(item => new RegExp(/^[a-zA-Z0-9 -]+$/g).test(item))
      // Sort alphabetically
      .sort()
  )

  // Remove items that don't start with the specified letter(s)
  if (inputs[1] === 'F or PH') {
    results = results.filter(
      item =>
        item.toLowerCase().startsWith('f') ||
        item.toLowerCase().startsWith('ph')
    )
  } else {
    results = results.filter(item =>
      item.toLowerCase().startsWith(inputs[1].toLowerCase())
    )
  }

  return results
}

const processAcronymOutputs = (input, outputs) => {
  const inputChars = input
    .toLowerCase()
    .split('')
    .filter(char => /[a-z]/.test(char))
    .join('')

  // Check each model output to make sure it is a valid acronym of the input query
  return deduplicateBasedOnSegmentAfterChar(
    outputs
      // Remove outputs that don't follow the expected format
      .filter(item => item.includes('-'))
      .filter(item => {
        const itemChars = item
          // For each item, only consider the part that occurs after the first "-"
          .split(/-(.*)/)[1]
          .trim()
          .split(' ')
          // Remove empty strings
          .filter(str => str)
          // Only consider words that start with capital letters
          .filter(word => word[0] === word[0].toUpperCase())
          .map(word => word[0])
          .join('')
          .toLowerCase()
        return inputChars === itemChars
      }),
    '-'
  )
}

const processFuseOutputs = outputs => {
  // NOTE: The character of interest is an em dash, NOT a hyphen
  return deduplicateBasedOnSegmentBeforeChar(outputs, '—')
}

const processSceneOutputs = outputs => {
  return shuffle(outputs)
}

const processUnfoldOutputs = (input, outputs) => {
  // Group results into fixed-sized chunks
  return shuffle(
    // Remove items that don't contain the input query
    outputs.filter(item =>
      item.toLowerCase().includes(input.toLowerCase().trim())
    )
  )
}
