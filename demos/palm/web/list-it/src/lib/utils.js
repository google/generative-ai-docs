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

export const getErrorMessage = error => {
  if (
    error.httpStatusCode &&
    error.httpStatusCode >= 400 &&
    error.httpStatusCode < 520 &&
    error.httpStatusCode !== 404
  ) {
    return {
      code: error.code,
      httpStatusCode: error.httpStatusCode,
      message: 'Technical error. Something went wrong.',
      type: 'technical',
      query: error.query
    }
  }
  return {
    code: error.code,
    message: 'Error. No list generated.',
    type: 'notAllowed',
    query: error.query
  }
}

export const capitalize = string =>
  string.charAt(0).toUpperCase() + string.slice(1)

export const moveCursorToEnd = element => {
  if (!element) return

  let range, selection

  if (document.createRange) {
    range = document.createRange()

    range.selectNodeContents(element)
    range.collapse(false)

    selection = window.getSelection()

    if (selection) {
      selection.removeAllRanges()
      selection.addRange(range)
    }
  }
}

export const useIsMobile = () => {
  // Store if window inner width is smaller than 768px
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  // Add event listener to window to update isMobile state
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return isMobile
}

const isTouchDevice = () => {
  return (
    !!(
      typeof window !== 'undefined' &&
      ('ontouchstart' in window ||
        (window.DocumentTouch &&
          typeof document !== 'undefined' &&
          document instanceof window.DocumentTouch))
    ) ||
    !!(
      typeof navigator !== 'undefined' &&
      (navigator.maxTouchPoints || navigator.msMaxTouchPoints)
    )
  )
}

export const useIsTouchDevice = () => {
  const [isTouch] = useState(isTouchDevice())

  return isTouch
}

const copyPrefix = [
  '📄 This is a transcript from List It, a demo app that uses the PaLM API.',
  '🗣 It records an interaction with a large language model (LLM).',
  '🛠 This is an early-stage technology. It may generate inaccurate or inappropriate information.',
  ''
]

export const copyLists = async lists => {
  const tips = document.querySelectorAll('.js-tip-box')
  const listTips = {}

  tips.forEach(tip => {
    const listId = tip.getAttribute('data-list-id')
    const content = tip.querySelector('.js-tip-text')
    listTips[listId] = content.textContent
  })

  const textToCopy = lists
    .map(list => {
      const tipText = listTips[list.id] ? `\n${listTips[list.id]}` : ''
      return `\n${capitalize(list.title)}\n• ${list.items.join(
        '\n• '
      )}${tipText}`
    })
    .join('\n')

  try {
    await navigator.clipboard.writeText(copyPrefix.join('\n') + textToCopy)
  } catch (error) {
    console.error('Failed to copy: ', error)
  }
}
