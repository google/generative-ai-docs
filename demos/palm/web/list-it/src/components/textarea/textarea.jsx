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

import {useState, useRef, useCallback, useEffect} from 'react'
import c from 'classnames'
import PropTypes from 'prop-types'

import Icon from '~/components/ui/icon/icon'

import {useRestarted} from '~/store'
import {moveCursorToEnd} from '~/lib/utils'

import styles from './textarea.module.scss'

const Textarea = ({onSubmit, placeholder, prefix, onRestart, showRestart}) => {
  const [val, setVal] = useState('')
  const [focused, setFocused] = useState(false)
  const [didSubmit, setDidSubmit] = useState(false)
  const inputRef = useRef(null)
  const restarted = useRestarted()

  const maxCharacters = 100
  const valIsValid = () => val.replace(/\s/g, '').length !== 0

  const onSubmitAction = () => {
    onSubmit({query: val})
    inputRef.current?.blur()
    setDidSubmit(true)
  }

  const onRestartAction = useCallback(() => {
    if (inputRef.current) {
      inputRef.current.textContent = ''
      inputRef.current.focus()
      moveCursorToEnd(inputRef.current)
    }
    setVal('')
    setDidSubmit(false)
    onRestart()
  }, [onRestart])

  // clear input on restart from outside
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.textContent = ''
    }
    setVal('')
    setDidSubmit(false)
  }, [restarted])

  const onKeyDown = e => {
    //  do nothing on an android device or when submit has happened
    if (didSubmit) {
      e.preventDefault()
      return
    }

    if (e.key === 'Enter' && valIsValid()) {
      e.preventDefault()
      onSubmitAction()
    }
  }

  const onAreaFocus = focus => {
    if (didSubmit && focus) {
      if (focused) setFocused(false)
      inputRef.current?.blur()
      return
    }

    setFocused(focus)
    if (focus) moveCursorToEnd(inputRef.current)
  }

  /**
   * Handle user input
   * @param event - Event
   * gets fired everytime the user types while focusing the input
   */
  const handleInput = event => {
    if (didSubmit) {
      event.preventDefault()
      return
    }

    const {target} = event

    if (target.innerText.length > maxCharacters) {
      if (inputRef.current) {
        inputRef.current.textContent = val
        moveCursorToEnd(inputRef.current)
      }
      return
    }

    // ignore paragraph breaks
    if (event.nativeEvent.inputType === 'insertParagraph') {
      if (inputRef.current) {
        inputRef.current.textContent = val
      }
      event.preventDefault()
      return
    }

    // ignore line breaks
    if (event?.nativeEvent?.data?.endsWith('\n')) {
      if (inputRef.current?.textContent) {
        const string = inputRef.current.textContent.replace('\n', '')
        inputRef.current.textContent = string

        if (string?.replace(/\s/g, '').length) onSubmitAction()
      }

      event.preventDefault()
      return
    }

    setVal(target.innerText || '')
  }

  /**
   * Handle user pasting into textarea
   * @param event - Event
   */
  const onPaste = event => {
    if (!focused) setFocused(true)
    if (didSubmit || !inputRef.current) {
      event.preventDefault()
      return
    }

    if (event.clipboardData) {
      let parsedText =
        inputRef.current.textContent + event.clipboardData.getData('Text')
      event.preventDefault()

      if (!parsedText) return
      if (parsedText.length > maxCharacters)
        parsedText = parsedText.slice(0, maxCharacters)

      inputRef.current.textContent = parsedText
      setVal(parsedText)
      moveCursorToEnd(inputRef.current)
      inputRef.current.focus()
    }
  }

  return (
    <div
      className={c(
        styles.textareaBox,
        {[styles.expand]: didSubmit},
        {[styles.hasFocus]: focused}
      )}
    >
      <div className={c(styles.textarea)}>
        <div role="none" className={styles.wrapper}>
          <div className={c(styles.prompt, styles.text)}>{prefix}&nbsp;</div>
          <span className={c(styles.spanParent, styles.text)}>
            <span
              id="query-input"
              ref={inputRef}
              role="textbox"
              aria-label="Text input to generate a list"
              tabIndex={0}
              data-placeholder={placeholder || 'type something'}
              className={c(styles.editableContent, styles.text, {
                [styles.disabled]: didSubmit
              })}
              spellCheck="false"
              onBlur={() => onAreaFocus(false)}
              onInput={handleInput}
              onKeyDown={onKeyDown}
              onFocus={() => onAreaFocus(true)}
              onPaste={onPaste}
              autoCapitalize="off"
              contentEditable
              suppressContentEditableWarning
            >
              {!focused && val === '' && !didSubmit && 'type something'}
            </span>
            {val === '' && !didSubmit && (
              <div
                aria-hidden={true}
                className={c(styles.placeholder, styles.text)}
              >
                {placeholder || 'type something'}
              </div>
            )}
          </span>
        </div>
        <div className={styles.rightColumn}>
          <button
            aria-hidden={val === '' || didSubmit}
            tabIndex={val === '' || didSubmit ? -1 : 0}
            aria-label="submit text"
            onClick={onSubmitAction}
            className={c(styles.submit, {
              [styles.hide]: !valIsValid() || didSubmit
            })}
          >
            <Icon icon="east" />
          </button>
        </div>
        {showRestart && (
          <div className={styles.restart}>
            <button
              type="button"
              aria-label="restart"
              tabIndex={0}
              onClick={onRestartAction}
            >
              <Icon icon="restart_alt" size="small" />
              <span className={styles.restartText}>restart</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

Textarea.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onRestart: PropTypes.func.isRequired,
  prefix: PropTypes.string,
  placeholder: PropTypes.string,
  showRestart: PropTypes.bool
}

export default Textarea
