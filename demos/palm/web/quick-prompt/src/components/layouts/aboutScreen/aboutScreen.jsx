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

import {useEffect, useRef} from 'react'
import c from 'classnames'
import {useHelp} from '../../../store'
import {useIsMobile} from '../../../lib/utils'
import styles from './aboutScreen.module.scss'

const AboutScreen = () => {
  const help = useHelp()
  const isMobile = useIsMobile()
  const aboutRef = useRef()

  /**
   * Set tabIndex to -1 when help is false, and 0 when help is true
   * to prevent tabbing to the about screen when it's not visible and vice versa
   */
  useEffect(() => {
    if (help) {
      aboutRef.current.tabIndex = 0
      aboutRef.current.setAttribute('aria-hidden', false)
    } else {
      aboutRef.current.tabIndex = -1
      aboutRef.current.setAttribute('aria-hidden', true)
    }
  }, [help])

  return (
    <div
      ref={aboutRef}
      tabIndex={-1}
      className={c(styles.aboutScreen, !isMobile && help && styles.show)}
    >
      <div className="container container--wide">
        <h2>About this game</h2>
        <img
          src="https://storage.googleapis.com/experiments-uploads/quick-prompt/quick-prompt.gif"
          alt="Quick Prompt demo gif"
        />
        <p>
          <em>Quick, Prompt!</em> is a game where you try to get your AI
          teammate to guess a given word without using the word itself or any of
          the “forbidden” words. This demo is an example of how you can use the
          PaLM API to build conversation-driven applications that leverage
          Google’s state of the art large language models (LLMs).
        </p>
        <p>Built by Google Creative Lab</p>
        <h2>License</h2>
        <p>Apache License, Version 2.0</p>
      </div>
    </div>
  )
}

export default AboutScreen
