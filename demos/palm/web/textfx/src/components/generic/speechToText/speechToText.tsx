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

/* eslint-disable no-unused-vars */

import {useState, useEffect} from 'react'
import {tippyOptions} from '~/constants'

import Tippy from '@tippyjs/react'
import Icon from '../icon/icon'

import styles from './speechToText.module.scss'

interface ISpeechToText {
  onResult: (text: string) => void
}

const SpeechToText = ({onResult}: ISpeechToText) => {
  const [isListening, setIsListening] = useState(false)
  const [isWaitingForResult, setIsWaitingForResult] = useState(false)
  const [speechRecognition, setSpeechRecognition] = useState(null)

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'

      recognition.onresult = (event: any) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            const text = event.results[i][0].transcript
            setIsListening(false)
            onResult(text.trim())
            // @ts-ignore
            recognition.stop()
          }
        }
      }

      recognition.onend = () => {
        setIsListening(false)
        setIsWaitingForResult(true)
        setTimeout(() => {
          setIsWaitingForResult(false)
        }, 1000)
      }

      recognition.onerror = () => {
        setIsListening(false)
        setIsWaitingForResult(false)
      }

      setSpeechRecognition(recognition)
    } else {
      console.error('Speech Recognition API not supported')
    }
  }, [onResult])

  const toggleListening = () => {
    if (isListening) {
      // @ts-ignore
      speechRecognition.stop()
    } else {
      // @ts-ignore
      speechRecognition.start()
    }
    setIsListening(!isListening)
  }

  return (
    <Tippy content="Speak" {...tippyOptions}>
      <button title="Speak" className={styles.root} onClick={toggleListening}>
        {!isListening && !isWaitingForResult && <Icon name="mic" />}
        {isListening && !isWaitingForResult && <Icon name="micListening" />}
        {isWaitingForResult && <Icon name="micWaiting" />}
      </button>
    </Tippy>
  )
}

export default SpeechToText
