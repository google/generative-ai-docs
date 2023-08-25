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

import Step1Image from '~/assets/images/welcome/welcome-step-1.jpg'
import Step2Image from '~/assets/images/welcome/welcome-step-2.jpg'
import Step3Image from '~/assets/images/welcome/welcome-step-3.jpg'

import styles from './welcome.module.scss'
import c from 'classnames'

const howItGoes = [
  {
    title: 'Select a tool',
    image: Step1Image
  },
  {
    title: 'Enter an input',
    image: Step2Image
  },
  {
    title: 'Explore outputs',
    image: Step3Image
  }
]

const Step2 = () => {
  const [mounted, setMounted] = useState<boolean>(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div className={c(styles.screen2, mounted && styles.animate)}>
      <span className={styles.heading}>How it works:</span>
      <ul className={styles.steps}>
        {howItGoes.map((hig, i) => {
          return (
            <li key={hig.title} className={styles.higItem}>
              <span className={c(styles.index, styles.fade, styles.fade1)}>
                {i + 1}.
              </span>
              <span className={c(styles.title, styles.fade, styles.fade2)}>
                {hig.title}
              </span>
              {i === 0 && (
                <img
                  src={Step1Image}
                  className={c(styles.fade, styles.fade3)}
                  alt={hig.title}
                  decoding="async"
                />
              )}
              {i === 1 && (
                <img
                  src={Step2Image}
                  className={c(styles.fade, styles.fade3)}
                  alt={hig.title}
                  decoding="async"
                />
              )}
              {i === 2 && (
                <img
                  src={Step3Image}
                  className={c(styles.fade, styles.fade3)}
                  alt={hig.title}
                  decoding="async"
                />
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
export default Step2
