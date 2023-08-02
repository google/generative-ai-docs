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

import {useState, useEffect} from 'react'

const useWindowSize = () => {
  const [size, setSize] = useState([0, 0])

  useEffect(() => {
    // TimeoutId for debounce mechanism
    let timeoutId: number | undefined = undefined
    const resizeListener = () => {
      // Prevent execution of previous setTimeout
      clearTimeout(timeoutId)
      // Change width from the state object after 150 milliseconds
      timeoutId = setTimeout(
        () => setSize([window.innerWidth, window.innerHeight]),
        150
      )
    }
    // Set resize listener
    window.addEventListener('resize', resizeListener)
    setSize([window.innerWidth, window.innerHeight])

    // Clean up function
    return () => {
      // Remove resize listener
      window.removeEventListener('resize', resizeListener)
    }
  }, [])

  return size
}

export default useWindowSize
