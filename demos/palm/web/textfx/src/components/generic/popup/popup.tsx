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

import {useEffect, useRef} from 'react'

import Button from '../button/button'
import Portal from '../portal/portal'
import useOnClickOutside from '~/hooks/useOnClickOutside'

import styles from './popup.module.scss'
import c from 'classnames'

interface IPopup {
  headline: string
  label: string
  actions: {label: string; onClick: () => void}[]
  onEscape: () => void
  onOutsideClick: () => void
}

const Popup = ({
  headline,
  label,
  actions,
  onEscape,
  onOutsideClick
}: IPopup) => {
  const popupRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Add escape key listener
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onEscape()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('keydown', handleEscape)
    }
  })
  useOnClickOutside(popupRef, () => onOutsideClick && onOutsideClick())

  return (
    <Portal>
      <div className={c(styles.popupRoot)}>
        <div ref={popupRef} className={styles.popup}>
          <h2>{headline}</h2>
          <span>{label}</span>
          <div className={styles.actions}>
            {actions.map(({label, onClick}, index) => (
              <Button
                variant={index === 0 ? 'white' : 'transparent'}
                key={label}
                onClick={onClick}
                label={label}
                size="reduced"
              />
            ))}
          </div>
        </div>
      </div>
    </Portal>
  )
}

export default Popup
