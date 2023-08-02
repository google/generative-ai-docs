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

import {useState, ReactNode} from 'react'

import styles from './numberToggle.module.scss'
import c from 'classnames'

interface INumberToggle {
  onClick: (e: number) => void
  count: number
  checked?: boolean
  children?: ReactNode
}

const NumberToggle = ({
  count,
  onClick,
  checked = false,
  children
}: INumberToggle) => {
  const [activeIndex, setActiveIndex] = useState(0)

  const handleNextOrPreviousClick = (isNext: boolean) => {
    const val = isNext ? activeIndex + 1 : activeIndex - 1
    if (val < 0) return
    if (val > count - 1) return

    setActiveIndex(val)
    onClick(val + 1)
  }

  return (
    <>
      <button
        className={c(styles.prevNextButton, !checked && styles.hide)}
        onClick={() => handleNextOrPreviousClick(false)}
      >
        <svg
          width="5"
          height="9"
          viewBox="0 0 5 9"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M4.125 0.749999L5 1.625L2.125 4.5L5 7.375L4.125 8.25L0.374999 4.5L4.125 0.749999Z"
            fill={'currentColor'}
          />
        </svg>
      </button>
      {children}
      <button
        className={c(styles.prevNextButton, !checked && styles.hide)}
        onClick={() => handleNextOrPreviousClick(true)}
      >
        <svg
          width="5"
          height="9"
          viewBox="0 0 5 9"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M0.875 8.25L0 7.375L2.875 4.5L0 1.625L0.875 0.75L4.625 4.5L0.875 8.25Z"
            fill={'currentColor'}
          />
        </svg>
      </button>
    </>
  )
}

export default NumberToggle
