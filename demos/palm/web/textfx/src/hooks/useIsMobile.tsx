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
import {breakPoints} from '~/constants'

/**
 *
 * Returns true if current window width matches mobile breakpoint
 * @param defaultState - Default state for initial render. Default is false.
 * @param breakPoint - Tailwind breakpoint to use as max width. Default is md.
 * @returns isMobile - (Boolean)
 */
const useIsMobile = (defaultState = null, breakPoint = 'medium') => {
  const [isMobile, setIsMobile] = useState<boolean | null>(defaultState)
  const bpWidth = breakPoints[breakPoint]

  const onResize = () => {
    setIsMobile(window.innerWidth < bpWidth)
  }

  const events = ['resize', 'orientationchange']

  useEffect(() => {
    // Trigger callback after initial rendering
    onResize()

    // Trigger callback 1 second after initial rendering for safety
    // setTimeout(onResize, 1000)

    // Add event listeners for all events from the array above
    events.forEach(e => {
      window.addEventListener(e, () => {
        onResize()
      })
    })
    // Remove event listeners for all events from the array above
    return () => {
      events.forEach(e => {
        window.removeEventListener(e, () => {})
      })
    }
  }, [])

  return isMobile
}

export default useIsMobile
