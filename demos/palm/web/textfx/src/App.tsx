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
import {useActions, useShowAbout, useShowNav, useShowPromptData} from './store'

import MainScreen from '~/components/layouts/mainScreen/mainScreen'
import Landing from './components/layouts/landing/landing'
import AboutScreen from './components/layouts/about/about'
import PromptData from './components/layouts/promptData/promptData'
import Portal from './components/generic/portal/portal'
import SiteNav from './components/generic/siteNav/siteNav'
import Hamburger from '~/components/generic/hamburger/hamburger'

import 'tippy.js/dist/tippy.css' // Optional

const App = () => {
  const savedMacro = sessionStorage.getItem('macroId')
  const [step, _setStep] = useState<number>(savedMacro ? 1 : 0)
  const stepRef = useRef<number>(step)
  const {setShowAbout, setShowPromptData, setShowNav} = useActions()
  const {showAbout} = useShowAbout()
  const {showNav} = useShowNav()
  const {showPromptData} = useShowPromptData()

  const setStep = (step: number) => {
    _setStep(step)
    stepRef.current = step
  }

  useEffect(() => {
    document.documentElement.style.setProperty(
      '--app-height',
      `${window.innerHeight}px`
    )

    window.addEventListener('beforeunload', event => {
      if (stepRef.current === 1) {
        event.returnValue = true
      }
    })
  }, [])

  return (
    <>
      <main>
        <Hamburger
          theme={step !== 1 || showNav ? 'light' : 'dark'}
          showX={showNav || showAbout || showPromptData}
          onClick={() => {
            setShowNav(!showNav)
          }}
        />
        <SiteNav step={step} setStep={setStep} />
        {step === 0 && <Landing onLaunchButtonClick={() => setStep(1)} />}
        {step === 1 && <MainScreen />}
        {showAbout && (
          <Portal>
            <AboutScreen onClose={() => setShowAbout(false)} />
          </Portal>
        )}
        <PromptData onClose={() => setShowPromptData(false)} />
      </main>
    </>
  )
}

export default App
