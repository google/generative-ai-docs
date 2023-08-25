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

import Cookies from 'js-cookie'
import styles from './welcome.module.scss'
import Button from '~/components/generic/button/button'
import Screen1 from './screen1'
import Screen2 from './screen2'

import c from 'classnames'

interface IWelcome {
  onNext: () => void
}

const WelcomeScreen = ({onNext = () => {}}: IWelcome) => {
  const [step, setStep] = useState<number>(0)

  useEffect(() => {}, [step])

  return (
    <div className={c(styles.welcomeScreen)}>
      <div>&nbsp;</div>
      <div className={styles.content}>
        {step === 0 && <Screen1 />}
        {step === 1 && <Screen2 />}
      </div>
      <div className={styles.actions}>
        <Button
          label={step === 1 ? "LET'S GO" : 'Next'}
          className={styles.nextButton}
          variant="white"
          onClick={() => {
            if (step >= 1) {
              Cookies.set('showWelcome', 'false', {expires: 365})
              onNext()
              return
            }

            setStep((prevStep) => prevStep + 1)
          }}
        />
      </div>
    </div>
  )
}

export default WelcomeScreen
