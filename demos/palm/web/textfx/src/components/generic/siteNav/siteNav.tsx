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

import {useState, useEffect} from 'react'
import {useShowNav, useShowAbout, useActions} from '~/store'

import GoogleLogo from '~/components/layouts/landing/googleLogo'

import styles from './siteNav.module.scss'
import c from 'classnames'

interface ISiteNav {
  step: number
  setStep: (step: number) => void
}

const SiteNav = ({step, setStep}: ISiteNav) => {
  const [mounted, setMounted] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const {showNav} = useShowNav()
  const {showAbout} = useShowAbout()

  const {setShowAbout, setShowNav} = useActions()

  const onClick = (evt: any, target: string) => {
    switch (target) {
      case 'home':
        sessionStorage.removeItem('macroId')
        break
      case 'tools':
        evt.preventDefault()
        setStep(1)
        break
      case 'about':
        evt.preventDefault()
        setShowAbout(true)
        break
      default:
        break
    }
    setShowNav(false)
  }

  useEffect(() => {
    if (showNav) {
      setMounted(true)
      setTimeout(() => {
        setIsOpen(true)
      }, 10)
    } else {
      setIsOpen(false)
      setTimeout(() => {
        setMounted(false)
      }, 600)
    }
  }, [showNav])

  return mounted ? (
    <div
      className={c(styles.nav, {
        [styles.isOpen]: isOpen
      })}
    >
      <ul className={styles.mainLinks}>
        <li>
          <a
            tabIndex={0}
            className={c(step === 0 && styles.active)}
            href="/"
            onClick={evt => onClick(evt, 'home')}
          >
            Home
          </a>
        </li>
        <li>
          <a
            tabIndex={0}
            href="/"
            className={c(step === 1 && styles.active)}
            onClick={evt => onClick(evt, 'tools')}
          >
            The Tools
          </a>
        </li>
        <li>
          <a
            tabIndex={0}
            href="/"
            className={c(showAbout && styles.active)}
            onClick={evt => onClick(evt, 'about')}
          >
            About
          </a>
        </li>
      </ul>
      <div>
        <GoogleLogo className={styles.logo} />
      </div>
    </div>
  ) : null
}

export default SiteNav
