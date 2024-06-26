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
import {useActions} from '~/store'
import {IMacro, colors, tippyOptions} from '~/constants'

import Tippy from '@tippyjs/react'
// @ts-ignore
import RangeSlider from 'react-range-slider-input'
import 'react-range-slider-input/dist/style.css'
import Button from '~/components/generic/button/button'
import SpeechToText from '../speechToText/speechToText'
import Icon from '../icon/icon'
import useIsMobile from '~/hooks/useIsMobile'

import styles from './macroInput.module.scss'
import c from 'classnames'

export interface IMacroInput {
  macro: IMacro
}
const MacroInput = ({macro}: IMacroInput) => {
  const {addOutput} = useActions()
  const inputsRef = useRef<HTMLUListElement>(null)
  const [temperature, setTemperature] = useState([0, 0.7])
  const inputRefs = useRef<HTMLInputElement[]>([])
  const [currentInputs, setCurrentInputs] = useState<string[]>(
    macro.inputs.map(() => '')
  )
  const [resubmit, setResubmit] = useState<boolean>(false)

  // Placeholder
  const intervalId = useRef<number>(-1)
  const timeoutId = useRef<number>(-1)
  const placeholderIndexes = useRef<number[]>(macro.inputs.map(() => 0))
  const [placeholders, setPlaceholders] = useState<string[]>(
    macro.inputs.map((m, i) => m.placeholder[placeholderIndexes.current[i]])
  )

  const isTabletOrLower = useIsMobile(null, 'medium')

  const getValues = () => {
    if (!inputsRef.current) return

    return [].slice
      .call(inputsRef.current.querySelectorAll('input, select'))
      .map((i: HTMLInputElement) => i.value)
  }

  const isValid = () => {
    const validInputs = macro.inputs.filter((input, index) => {
      if (input.type === 'dropdown') return true

      // Empty values
      if (currentInputs[index].length === 0) return false

      // Check max length
      if (
        typeof input.maxLength === 'number' &&
        currentInputs[index].length > input.maxLength
      )
        return false

      // All good
      return true
    })

    return validInputs.length === macro.inputs.length
  }

  const onSubmit = () => {
    let emptyInputs = false
    const inputs = [...currentInputs]
    macro.inputs.map((input, index) => {
      if (input.type === 'dropdown') return

      // Empty values
      if (currentInputs[index].length === 0) {
        emptyInputs = true
        inputs[index] = placeholders[index]
        inputRefs.current[index].value = placeholders[index]
        return true
      }
    })

    if (emptyInputs) {
      setCurrentInputs(inputs)
      setResubmit(true)
      return
    }

    if (!isValid()) return

    addOutput(getValues() || [], temperature[1])
  }

  useEffect(() => {
    if (resubmit) {
      setResubmit(false)
      onSubmit()
    }
  }, [currentInputs, resubmit])

  useEffect(() => {
    setCurrentInputs(macro.inputs.map(() => ''))

    if (isTabletOrLower === null || isTabletOrLower) return

    // Focus on macro switch
    inputRefs.current[0]
      ? inputRefs.current[0].focus()
      : inputRefs.current[1].focus()
  }, [macro, isTabletOrLower])

  useEffect(() => {
    //reset on macro change
    if (intervalId.current > 0) {
      clearInterval(intervalId.current)
    }
    if (timeoutId.current > 0) {
      clearTimeout(timeoutId.current)
    }
    placeholderIndexes.current = macro.inputs.map(() => 0)
    setPlaceholders(
      macro.inputs.map((m, i) => m.placeholder[placeholderIndexes.current[i]])
    )

    intervalId.current = setInterval(() => {
      placeholderIndexes.current = placeholderIndexes.current.map((cur, i) => {
        if (inputRefs.current[i]) {
          inputRefs.current[i].classList.add('hide-placeholder')
        }
        return cur < macro.inputs[i].placeholder.length - 1 ? cur + 1 : 0
      })

      timeoutId.current = setTimeout(() => {
        setPlaceholders(
          macro.inputs.map(
            (m, i) => m.placeholder[placeholderIndexes.current[i]]
          )
        )

        macro.inputs.map((m, i) => {
          if (inputRefs.current[i]) {
            inputRefs.current[i].classList.remove('hide-placeholder')
          }
        })
      }, 500)
    }, 3000)

    return () => {
      clearInterval(intervalId.current)
    }
  }, [macro])

  return (
    <div className={c(styles.macroInput, styles[macro.slug])}>
      <ul ref={inputsRef} className={styles.fieldsets}>
        {macro.inputs.map((input, index) => {
          return (
            <li key={input.label} className={styles.fieldset}>
              <label className={styles.label}>{input.label}</label>
              {input.type === 'dropdown' ? (
                <div className={styles.inputBox}>
                  <select className={styles.select}>
                    <option value="a">A</option>
                    <option value="b">B</option>
                    <option value="c">C</option>
                    <option value="d">D</option>
                    <option value="e">E</option>
                    <option value="f">F</option>
                    <option value="g">G</option>
                    <option value="h">H</option>
                    <option value="i">I</option>
                    <option value="j">J</option>
                    <option value="k">K</option>
                    <option value="l">L</option>
                    <option value="m">M</option>
                    <option value="n">N</option>
                    <option value="o">O</option>
                    <option value="p">P</option>
                    <option value="q">Q</option>
                    <option value="r">R</option>
                    <option value="s">S</option>
                    <option value="t">T</option>
                    <option value="u">U</option>
                    <option value="v">V</option>
                    <option value="w">W</option>
                    <option value="x">X</option>
                    <option value="y">Y</option>
                    <option value="z">Z</option>
                    <option value="ch">CH</option>
                    <option value="sh">SH</option>
                    <option value="th">TH</option>
                  </select>
                  <Icon name="dropdown" />
                </div>
              ) : (
                <div className={styles.inputBox}>
                  <input
                    className={styles.input}
                    type="text"
                    ref={(ref: HTMLInputElement) =>
                      (inputRefs.current[index] = ref)
                    }
                    onKeyDown={event => {
                      if (event.key === 'Enter') {
                        event.preventDefault()
                        onSubmit()
                      }
                    }}
                    onFocus={() => {
                      inputRefs.current[index].select()
                    }}
                    /* eslint-disable-next-line no-undef */
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      if (
                        e?.target &&
                        /\s/.test((e.target as HTMLInputElement).value) &&
                        input.allowSpaces === false
                      ) {
                        // If spaces are found, prevent default behavior
                        e.preventDefault()
                        return
                      }

                      if (!input.maxLength) {
                        inputRefs.current[index].value = e.target.value

                        const inputs = [...currentInputs]
                        inputs[index] = e.target.value
                        setCurrentInputs(inputs)
                        return
                      }

                      let value = e.target.value

                      // maxLength === word
                      if (
                        value.length >= 1 &&
                        input.maxLength === 'word' &&
                        value.indexOf(' ') !== -1
                      ) {
                        value = value.substring(0, value.indexOf(' '))
                      }

                      // maxLength === number
                      if (
                        typeof input.maxLength === 'number' &&
                        value.length >= input.maxLength
                      ) {
                        value = value.substring(0, input.maxLength)
                      }
                      inputRefs.current[index].value = value

                      const inputs = [...currentInputs]
                      inputs[index] = value
                      setCurrentInputs(inputs)
                    }}
                    placeholder={placeholders[index]}
                    value={currentInputs[index] || ''}
                  />
                  <SpeechToText
                    onResult={e => {
                      inputRefs.current[index].value = e

                      const inputs = [...currentInputs]
                      inputs[index] = e
                      setCurrentInputs(inputs)
                    }}
                  />
                </div>
              )}
              {input.maxLength && input.maxLength !== 'word' && (
                <span
                  className={c(
                    styles.maxLength,
                    input.maxLength &&
                      typeof input.maxLength === 'number' &&
                      currentInputs[index]?.length >= input.maxLength &&
                      styles.isMaxLength
                  )}
                >
                  {currentInputs[index]?.length} / {input.maxLength}{' '}
                  {input.maxLengthDescription || ''}
                </span>
              )}
            </li>
          )
        })}
      </ul>
      <div className={styles.actions}>
        <div className={styles.rangeSlider}>
          <Tippy
            content="Amount of creativity allowed in outputs"
            {...tippyOptions}
          >
            {/* eslint-disable */}
            {/* tabIndex is needed for tippy to work */}
            <span tabIndex={0}>Temperature</span>
            {/* eslint-enable */}
          </Tippy>
          <RangeSlider
            value={temperature}
            onInput={setTemperature}
            thumbsDisabled={[true, false]}
            rangeSlideDisabled={true}
            min={0}
            max={1}
            step={0.1}
          />
          <span>{temperature[1]}</span>
        </div>
        <Button
          size="default"
          label="run"
          variant={
            Object.keys(colors).find(
              (c: string) => colors[c as keyof typeof colors] === macro.color
            ) || 'dark'
          }
          onClick={() => onSubmit()}
        />
      </div>
    </div>
  )
}

export default MacroInput
