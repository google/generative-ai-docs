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

import {useEffect, useState, useRef} from 'react'
import {find} from '~/lib/utils'

import Lottie from 'react-lottie-player'
import lupeSignature from '~/assets/lupe_signature_animation_lottie.json'

import styles from './welcome.module.scss'
import c from 'classnames'

const greeting = 'Welcome to TextFX.'
const p1a =
  'These tools were inspired by some of the lyrical and linguistic techniques I have developed over 20 years of writing Raps. '
const p1b =
  "But TextFX won't write Raps for you. Instead, these tools are designed to empower your writing, provide creative possibilities and help you see text in new ways. "
const p1c =
  'Like with any tool, you still need to bring your own creativity and skillset to them.'

const p2a =
  'TextFX was created in collaboration with Google using MakerSuite and the PaLM API. '
const p2b =
  "Hopefully, it will show you what's possible with the PaLM API and inspire you to bring your own ideas to life, in whatever your craft may be."

const signoff = 'Enjoy the journey,'
const postSignature = 'Lupe Fiasco'

const wait = async (time: number) => {
  return await new Promise(resolve => setTimeout(resolve, time))
}

const Step1 = () => {
  const [mounted, setMounted] = useState<boolean>(false)
  const [playLottie, setPlayLottie] = useState<boolean>(false)
  const screenRef = useRef<HTMLDivElement>(null)

  const animateText = (spans: HTMLSpanElement[]) => {
    let index: number = 0

    return new Promise(resolve => {
      const intervalId = setInterval(() => {
        spans[index++].style.opacity = '1'
        if (index >= spans.length) {
          clearInterval(intervalId)
          resolve('done')
        }
      }, 30)
    })
  }

  useEffect(() => {
    const doEffect = async () => {
      const greetingSpans = find('.js-char-hi', screenRef.current)
      const p1a = find('.js-char-p1a', screenRef.current)
      const p1b = find('.js-char-p1b', screenRef.current)
      const p1c = find('.js-char-p1c', screenRef.current)
      const p2a = find('.js-char-p2a', screenRef.current)
      const p2b = find('.js-char-p2b', screenRef.current)
      const signoffSpans = find('.js-char-bye', screenRef.current)
      const postSignatureSpans = find('.js-char-lupe', screenRef.current)

      await animateText(greetingSpans)
      await wait(1500)
      await animateText(p1a)
      await wait(1000)
      await animateText(p1b)
      await wait(1000)
      await animateText(p1c)
      await wait(1500)
      await animateText(p2a)
      await wait(1000)
      await animateText(p2b)
      await wait(1000)
      await animateText(signoffSpans)

      setPlayLottie(true)
      await animateText(postSignatureSpans)
    }

    doEffect()

    setMounted(true)
  }, [])
  return (
    <div
      ref={screenRef}
      className={c(styles.greeting, mounted && styles.animate)}
    >
      {greeting.split('').map((char, i) => {
        return (
          <span key={i} className={c('js-char-hi', styles.char)}>
            {char}
          </span>
        )
      })}
      <br />
      <br />
      <p>
        {p1a.split('').map((char, i) => {
          return (
            <span key={i} className={c('js-char-p1a', styles.char)}>
              {char}
            </span>
          )
        })}
        {p1b.split('').map((char, i) => {
          return (
            <span key={i} className={c('js-char-p1b', styles.char)}>
              {char}
            </span>
          )
        })}
        {p1c.split('').map((char, i) => {
          return (
            <span key={i} className={c('js-char-p1c', styles.char)}>
              {char}
            </span>
          )
        })}
      </p>
      <br />
      <p>
        {p2a.split('').map((char, i) => {
          return (
            <span key={i} className={c('js-char-p2a', styles.char)}>
              {char}
            </span>
          )
        })}
        {p2b.split('').map((char, i) => {
          return (
            <span key={i} className={c('js-char-p2b', styles.char)}>
              {char}
            </span>
          )
        })}
      </p>
      <br />
      <br />
      {signoff.split('').map((char, i) => {
        return (
          <span key={i} className={c('js-char-bye', styles.char)}>
            {char}
          </span>
        )
      })}
      <br />
      <div>
        <div className={styles.signature}>
          <Lottie
            play={playLottie}
            loop={false}
            animationData={lupeSignature}
          />
        </div>

        {postSignature.split('').map((char, i) => {
          return (
            <span key={i} className={c('js-char-lupe', styles.char)}>
              {char}
            </span>
          )
        })}
      </div>
    </div>
  )
}
export default Step1
