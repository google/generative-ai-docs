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

import {useState, useRef, useEffect, useLayoutEffect} from 'react'
import {useActions} from '~/store'
import {IMacro, watchLupeUseItVideos} from '~/constants'
import Icon, {IIcon} from '~/components/generic/icon/icon'

import Portal from '~/components/generic/portal/portal'
import useOnClickOutside from '~/hooks/useOnClickOutside'

import styles from './macroDescription.module.scss'
import c from 'classnames'

export interface IMacroDescription {
  macro: IMacro
}

const MacroDescription = ({macro}: IMacroDescription) => {
  const [showLupeUseIt, setShowLupeUseIt] = useState<boolean>(false)
  const previousMacroRef = useRef<IMacro | null>(null)
  const [previousMacro, setPreviousMacro] = useState<IMacro | null>(null)
  const [hidePreviousMacro, setHidePreviousMacro] = useState(false)
  const [showCurrentMacro, setShowCurrentMacro] = useState(false)
  const videoBoxRef = useRef<HTMLDivElement | null>(null)
  const {setShowPromptData} = useActions()

  useOnClickOutside(videoBoxRef, () => setShowLupeUseIt(false))

  useLayoutEffect(() => {
    setHidePreviousMacro(false)
    setShowCurrentMacro(false)

    if (previousMacroRef.current) {
      setPreviousMacro(previousMacroRef.current)
    }

    setTimeout(() => {
      setShowCurrentMacro(true)
    }, 100)

    previousMacroRef.current = macro
  }, [macro])

  useEffect(() => {
    setTimeout(() => {
      setHidePreviousMacro(true)
    }, 100)
  }, [previousMacro])

  return (
    <>
      <div className={c(styles.descriptionsWrapper)}>
        {previousMacro && (
          <div
            aria-hidden="true"
            className={c(
              styles.macroDescription,
              styles.previousMacroDescription,
              hidePreviousMacro && styles.hide
            )}
          >
            <Icon
              name={previousMacro.icon as IIcon['name']}
              className={styles.icon}
            />
            <h1>{previousMacro.name}</h1>
            <p className={styles.description}>{previousMacro.description}</p>
            <ul>
              <li>
                <a
                  href={previousMacro.videoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.lupeLink}
                  onClick={event => {
                    event.preventDefault()
                    setShowLupeUseIt(true)
                  }}
                >
                  <Icon name="play" />
                  <span>Watch Lupe use it</span>
                </a>
              </li>
              <li>
                <a href="/" className={styles.lupeLink}>
                  <Icon name="info" />
                  <span>Look under the hood</span>
                </a>
              </li>
            </ul>
          </div>
        )}
        <div
          className={c(
            styles.currentMacroDescription,
            styles.macroDescription,
            showCurrentMacro && styles.show
          )}
        >
          <Icon name={macro.icon as IIcon['name']} className={styles.icon} />
          <h1>{macro.name}</h1>
          <p className={styles.description}>{macro.description}</p>
          <ul>
            <li>
              <a
                href={macro.videoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.lupeLink}
                onClick={event => {
                  event.preventDefault()
                  setShowLupeUseIt(true)
                }}
              >
                <Icon name="play" />
                <span>Watch Lupe use it</span>
              </a>
            </li>
            <li>
              <a
                href="/"
                className={styles.lupeLink}
                onClick={event => {
                  event.preventDefault()
                  setShowPromptData(true)
                }}
              >
                <Icon name="info" />
                <span>Look under the hood</span>
              </a>
            </li>
          </ul>
        </div>
      </div>
      {showLupeUseIt && (
        <Portal>
          <div className={styles.videoPopup}>
            <div className={c(styles.videoPopupContent, 'container')}>
              <div ref={videoBoxRef} className={styles.videoBox}>
                <iframe
                  title="Watch Lupe use it"
                  src={watchLupeUseItVideos[macro.slug]}
                  width="640"
                  height="480"
                  allow="autoplay"
                ></iframe>
              </div>
            </div>
          </div>
        </Portal>
      )}
    </>
  )
}

export default MacroDescription
