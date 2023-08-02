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

import {useEffect, useState} from 'react'

import styles from './viewAllToggle.module.scss'
import c from 'classnames'

interface IViewAllToggle {
  onClick: (e: boolean) => void
  defaultChecked?: boolean
  selected?: boolean
}

const ViewAllToggle = ({
  onClick,
  defaultChecked = false,
  selected = false
}: IViewAllToggle) => {
  const [checked, setChecked] = useState(defaultChecked)

  const handleBtnClick = () => {
    const val = !checked
    setChecked(val)
    onClick(val)
  }

  useEffect(() => {
    setChecked(selected)
  }, [selected])

  return (
    <button
      className={c(styles.root, checked && styles.checked)}
      onClick={handleBtnClick}
    >
      {checked ? 'VIEW 1 AT A TIME' : 'VIEW ALL'}
    </button>
  )
}

export default ViewAllToggle
