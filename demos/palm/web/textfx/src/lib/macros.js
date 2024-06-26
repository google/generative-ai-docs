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

import {predict} from './api.js'
import {parseOutputs} from './parse.js'
import {postprocess} from './postprocess.js'

import * as priming from './priming.js'

/**
 * Create a simile about a thing or concept.
 *
 * @param {string} input       A thing or concept.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of outputs.
 */
export const runSimile = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const similePrompt = priming.constructPrompt(
    priming.SIMILE_PROMPT_COMPONENTS,
    [input]
  )
  const response = await predict(similePrompt, temperature)
  const outputs = parseOutputs(response, priming.SIMILE_PROMPT_COMPONENTS)
  return postprocess('simile', [input], outputs)
}

/**
 * Break a word into similar-sounding phrases.
 *
 * @param {string} input       A word.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runExplode = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const explodePrompt = priming.constructPrompt(
    priming.EXPLODE_PROMPT_COMPONENTS,
    [`"${input}"${priming.PREFIX_DELIMITER}`]
  )
  const response = await predict(explodePrompt, temperature)
  const outputs = parseOutputs(response, priming.EXPLODE_PROMPT_COMPONENTS)
  return postprocess('explode', [input], outputs)
}

/**
 * Make a scene more unexpected and imaginative.
 *
 * @param {string} input       A scene.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runUnexpect = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const unexpectPrompt = priming.constructPrompt(
    priming.UNEXPECT_PROMPT_COMPONENTS,
    [input]
  )
  const response = await predict(unexpectPrompt, temperature)
  const outputs = parseOutputs(response, priming.UNEXPECT_PROMPT_COMPONENTS)
  return postprocess('unexpect', [input], outputs)
}

/**
 * Build a chain of semantically related items.
 *
 * @param {string} input       A word.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runChain = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const chainPrompt = priming.constructPrompt(priming.CHAIN_PROMPT_COMPONENTS, [
    `"${input}"${priming.PREFIX_DELIMITER}`
  ])
  const response = await predict(chainPrompt, temperature)
  const outputs = parseOutputs(response, priming.CHAIN_PROMPT_COMPONENTS)
  return postprocess('chain', [input], outputs)
}

/**
 * Evaluate a topic through different points of view.
 *
 * @param {string} input       A topic.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runPOV = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const povPrompt = priming.constructPrompt(priming.POV_PROMPT_COMPONENTS, [
    `${input}${priming.PREFIX_DELIMITER}`
  ])
  const response = await predict(povPrompt, temperature)
  const outputs = parseOutputs(response, priming.POV_PROMPT_COMPONENTS)
  return postprocess('pov', [input], outputs)
}

/**
 * Curate topic-specific words that start with a chosen letter.
 *
 * @param {string} input1       A topic.
 * @param {string} input2       A letter or phoneme.
 * @param {number} temperature  The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runAlliteration = async (input1, input2, temperature) => {
  input1 = input1.toLowerCase().trim()
  input2 = input2.toUpperCase().trim()
  if (input2 === 'F') {
    input2 = 'F or PH'
  }
  const alliterationPrompt = priming.constructPrompt(
    priming.ALLITERATION_PROMPT_COMPONENTS,
    [input1, `${input2}${priming.PREFIX_DELIMITER}`]
  )
  const response = await predict(alliterationPrompt, temperature)
  const outputs = parseOutputs(response, priming.ALLITERATION_PROMPT_COMPONENTS)
  return postprocess('alliteration', [input1, input2], outputs)
}

/**
 * Create an acronym using the letters of a word.
 *
 * @param {string} input       A word.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runAcronym = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const acronymPrompt = priming.constructPrompt(
    priming.ACRONYM_PROMPT_COMPONENTS,
    [`"${input}"${priming.PREFIX_DELIMITER}`]
  )
  const response = await predict(acronymPrompt, temperature)
  const outputs = parseOutputs(response, priming.ACRONYM_PROMPT_COMPONENTS)
  return postprocess('acronym', [input], outputs)
}

/**
 * Find intersections between two things.
 *
 * @param {string} input1       A thing.
 * @param {string} input2       Another thing.
 * @param {number} temperature  The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runFuse = async (input1, input2, temperature) => {
  input1 = input1.toLowerCase().trim()
  input2 = input2.toLowerCase().trim()
  const fusePrompt = priming.constructPrompt(priming.FUSE_PROMPT_COMPONENTS, [
    input1,
    input2
  ])
  const response = await predict(fusePrompt, temperature)
  const outputs = parseOutputs(response, priming.FUSE_PROMPT_COMPONENTS)
  return postprocess('fuse', [input1, input2], outputs)
}

/**
 * Generate sensory details about a scene.
 *
 * @param {string} input       A scene.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runScene = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const scenePrompt = priming.constructPrompt(priming.SCENE_PROMPT_COMPONENTS, [
    input
  ])
  const response = await predict(scenePrompt, temperature)
  const outputs = parseOutputs(response, priming.SCENE_PROMPT_COMPONENTS)
  return postprocess('scene', [input], outputs)
}

/**
 * Slot a word into other existing words or phrases.
 *
 * @param {string} input       A word.
 * @param {number} temperature The model temperature. May range from 0.0 to 1.0.
 *
 * @returns A Promise object that, if fulfilled, returns an array of string outputs.
 */
export const runUnfold = async (input, temperature) => {
  input = input.toLowerCase().trim()
  const unfoldPrompt = priming.constructPrompt(
    priming.UNFOLD_PROMPT_COMPONENTS,
    [input]
  )
  const response = await predict(unfoldPrompt, temperature)
  const outputs = parseOutputs(response, priming.UNFOLD_PROMPT_COMPONENTS)
  return postprocess('unfold', [input], outputs)
}
