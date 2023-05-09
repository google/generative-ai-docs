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

import {useEffect, useState} from 'react'
import excluded_words from './excluded_words'

export const getRand = xs => xs[Math.floor(Math.random() * xs.length)]

export const roundSeconds = 120
// export const roundSeconds = 5

export const useIsMobile = () => {
  // store if window inner width is smaller than 768px
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)
  // add event listener to window to update isMobile state
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])
  return isMobile
}

/**
 * The AI will return a string with [] to indicate the part of the string
 * that is the guess. Replace [] with <mark> tag to style the guessed word,
 * then split the text into an array of objects with word and count properties
 * to be used in the wordByWord animation.
 *
 * @param {string} str - string to split
 * @returns {array} - array of objects with word and count properties
 * @example
 * splitText('Hello world')
 * // returns [{word: 'Hello', count: 0}, {word: 'world', count: 6}]
 **/
export const splitText = str => {
  let count = 0
  const re = new RegExp('(<mark.*?</mark>)', 'g')

  return str
    .trim()
    .replace(/\[(.+)\]/, '<mark class="guess">$1</mark>')
    .split(re)
    .reduce((acc, curr) => {
      if (curr.match(re)) return [...acc, curr]
      return [...acc, ...curr.split(' ').filter(Boolean)]
    }, [])
    .map(word => {
      const wordObject = {
        word,
        count
      }
      count += word.length + 1
      return wordObject
    })
}

/**
 * Will match if a word from the user input (userInputWords) matches part or all of gamePrompt.word
 * Will match if a word from the user input (userInputWords) exactly matches a disallowed word
 *
 * @param {object} gamePrompt - object representing the game prompt
 * @param {array} userInputWords - the user input, as an array of words
 * @returns {array} - array of matches
 */
export const matchDisallowedWords = (gamePrompt, userInputWords) => {
  const {word, disallowed} = gamePrompt

  const matches = userInputWords.reduce((acc, word2) => {
    const ignore =
      word2.length < 2 || excluded_words.includes(word2.toLowerCase())
    if (ignore) return acc

    if (word.toLowerCase().match(word2.toLowerCase())) acc.push(word2)

    const filtered = disallowed.filter(disallowedWord => {
      return disallowedWord.toLowerCase() === word2.toLowerCase()
    })

    if (filtered.length) {
      acc.push(...filtered)
    }

    return acc
  }, [])

  return matches
}

export const checkIsAndroid = () => {
  const ua = (window.navigator || {}).userAgent || ''
  return /android/i.test(ua)
}
