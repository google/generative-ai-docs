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

import {useRef, useState, useEffect} from 'react'
import {useMacros, useOutputs, useOutputPins} from '~/store'
import {colors} from '~/constants'

import MacroButtons from '~/components/generic/macroButtons/macroButtons'
import MacroDescription from '~/components/generic/macroDescription/macroDescription'
import MacroInput from '~/components/generic/macroInput/macroInput'
import OutputSection from '~/components/generic/outputSection/outputSection'
import useSticky from '~/hooks/useSticky'
import Icon from '~/components/generic/icon/icon'
import useIsMobile from '~/hooks/useIsMobile'

import styles from './mainScreen.module.scss'
import c from 'classnames'

const MainScreen = () => {
  const mainScreenRef = useRef<HTMLDivElement | null>(null)
  const inputSectionRef = useRef<HTMLDivElement | null>(null)
  const macroButtonsRef = useRef<HTMLDivElement | null>(null)
  // const splitScreenRef = useRef<HTMLDivElement | null>(null)
  const descriptionRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLDivElement | null>(null)

  const {activeMacro} = useMacros()
  const {outputs = []} = useOutputs()
  const {isSticky} = useSticky(inputSectionRef)
  const [hover, setHover] = useState<boolean>(false)
  const isMobile = useIsMobile(null, 'large')
  const pins = useOutputPins()

  // Using js for hover to fix Safari scroll issue
  const onMouseEnter = () => {
    if (!isSticky || outputs.length === 0) return
    setHover(true)
  }

  const onMouseLeave = () => {
    setHover(false)
  }

  useEffect(() => {
    if (isMobile === null) return

    if (outputs.length === 0 && pins.length === 0) {
      mainScreenRef?.current?.style.setProperty(
        '--inputSectionHeight',
        window.innerHeight + 'px'
      )
      return
    }

    const padding = isMobile ? 25 : 50
    const header = 80
    let inputSectionHeight =
      header +
      padding +
      (macroButtonsRef?.current?.offsetHeight || 0) +
      (descriptionRef?.current?.offsetHeight || 0)

    if (isMobile) {
      inputSectionHeight += inputRef?.current?.offsetHeight || 0
    }

    mainScreenRef?.current?.style.setProperty(
      '--inputSectionHeight',
      inputSectionHeight + 'px'
    )
  }, [activeMacro, outputs.length, pins.length])

  useEffect(() => {
    if (!mainScreenRef.current) return

    mainScreenRef.current.addEventListener('scroll', () => {
      setHover(false)
    })
  }, [])

  return (
    <>
      <div
        ref={mainScreenRef}
        className={c(
          'js-mainScreen',
          styles.mainScreen,
          (outputs.length > 0 || pins.length > 0) && styles.hasOutputs,
          isSticky && outputs.length > 0 && styles.isSticky,
          hover && styles.isHover
        )}
        style={{
          backgroundColor: activeMacro ? activeMacro.color : colors.mid_grey
        }}
      >
        <section
          ref={inputSectionRef}
          className={c(styles.inputSection)}
          onMouseEnter={() => onMouseEnter()}
          onMouseLeave={() => onMouseLeave()}
        >
          <div
            className={styles.collapsedBar}
            style={{
              backgroundColor: activeMacro ? activeMacro.color : colors.mid_grey
            }}
          >
            <div className="container">
              <span className={styles.macroName}>
                {activeMacro && activeMacro.name}
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g clipPath="url(#clip0_457_9752)">
                    <path d="M12 15L7 10H17L12 15Z" fill="#444746" />
                  </g>
                  <defs>
                    <clipPath id="clip0_457_9752">
                      <rect width="24" height="24" fill="white" />
                    </clipPath>
                  </defs>
                </svg>
              </span>
            </div>
          </div>
          <div
            className={styles.inputSectionWrapper}
            style={{
              backgroundColor: activeMacro ? activeMacro.color : colors.mid_grey
            }}
          >
            <div className={styles.topBar}>
              <a
                href="/"
                onClick={() => {
                  sessionStorage.removeItem('macroId')
                }}
              >
                <Icon name="logo" className={styles.logo} />
              </a>
            </div>
            <div ref={macroButtonsRef}>
              <MacroButtons />
            </div>
            {activeMacro && (
              <div className="container">
                <div className={styles.splitScreen}>
                  <div ref={descriptionRef}>
                    <MacroDescription macro={activeMacro} />
                  </div>
                  <div ref={inputRef}>
                    <MacroInput macro={activeMacro} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
        <div
          className={c(
            styles.outputSection,
            (outputs.length > 0 || pins.length > 0) && styles.active
          )}
        >
          <OutputSection />
        </div>
      </div>
    </>
  )
}

export default MainScreen
