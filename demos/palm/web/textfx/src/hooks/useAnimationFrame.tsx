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

import {useRef, useEffect, useState} from 'react'

interface IUseAnimationFrame {
  start: Function
  stop: Function
}

const useAnimationFrame = (): IUseAnimationFrame => {
  const rafRef = useRef<number>()
  const previousTimeRef = useRef(performance.now())
  const [playing, setPlaying] = useState(false)
  const [callback, setCallback] = useState<Function | undefined>()

  const animate = (timeStamp: number) => {
    if (!callback || !playing) return

    if (previousTimeRef.current != undefined) {
      const deltaTime = timeStamp - previousTimeRef.current
      callback(deltaTime)
    }
    previousTimeRef.current = timeStamp
    rafRef.current = requestAnimationFrame(animate)
  }

  useEffect(() => {
    if (!callback || !playing) return

    rafRef.current = requestAnimationFrame(animate)
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [playing, callback])

  return {
    start: (callback: Function) => {
      setCallback(() => callback)
      setPlaying(true)
    },
    stop: () => setPlaying(false)
  }
}

export default useAnimationFrame
