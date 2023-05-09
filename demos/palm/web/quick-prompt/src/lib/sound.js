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

const audioContext = new AudioContext()
const audioBuffers = {}

/**
 * Get audio buffer from cache or fetch it
 * @param {string} url
 * @returns {Promise<AudioBuffer>}
 */
const getAudio = async url => {
  if (!audioBuffers[url]) {
    audioBuffers[url] = await fetchAudio(url)
  }
  return audioBuffers[url]
}

/**
 * Fetch audio buffer from url
 * @param {string} url
 * @returns {Promise<AudioBuffer>}
 */
const fetchAudio = async url => {
  const response = await fetch(url)
  const arrayBuffer = await response.arrayBuffer()
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
  return audioBuffer
}

/**
 * Play audio buffer from url
 * @param {string} url
 * @returns {Promise}
 */
export const playSound = async url => {
  const audioBuffer = await getAudio(url)
  const source = audioContext.createBufferSource()
  source.buffer = audioBuffer
  source.connect(audioContext.destination)
  source.start()
}
