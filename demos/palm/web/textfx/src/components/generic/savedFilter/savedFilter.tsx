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

import {tippyOptions} from '~/constants'

import Tippy from '@tippyjs/react'
import Icon from '../icon/icon'

import styles from './savedFilter.module.scss'
import c from 'classnames'

interface ISavedFilter {
  onClick: () => void
  active?: boolean
}

const SavedFilter = ({onClick, active, ...rest}: ISavedFilter) => {
  return (
    <Tippy content="Show Saved" {...tippyOptions}>
      <button
        className={c(styles.root, active && styles.filled)}
        onClick={onClick}
        {...rest}
      >
        {active ? <Icon name="saved" /> : <Icon name="save" />}
        <span>Saved</span>
      </button>
    </Tippy>
  )
}

export default SavedFilter
