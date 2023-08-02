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
import {useFilters, useMacros, useActions} from '~/store'
import {tippyOptions} from '~/constants'

import FilterList from '../filterList/filterList'
import Icon from '../icon/icon'
import Tippy from '@tippyjs/react'

import styles from './filterButton.module.scss'
import c from 'classnames'

interface IFilterButton {
  active?: boolean
}

const FilterButton = ({active, ...rest}: IFilterButton) => {
  const [open, setOpen] = useState(false)

  const {macros} = useMacros()
  const {filters} = useFilters()
  const {setFilters} = useActions()

  // Reset filters to all when "active" prop changes
  useEffect(() => {
    setFilters(macros.map(e => e.id))
  }, [active, setFilters, macros])

  return (
    <>
      <div className={styles.main}>
        <Tippy content="Filter by" {...tippyOptions}>
          <button
            className={c(styles.root, active && styles.filled)}
            onClick={() => setOpen(!open)}
            {...rest}
          >
            <Icon name="all" />
            <span>
              {filters.length !== macros.length ? `(${filters.length})` : 'All'}
            </span>
            <Icon name="arrow" />
          </button>
        </Tippy>
        <div className={c(styles.filterList, open && styles.open)}>
          <FilterList />
        </div>
      </div>
      {open && (
        <button className={styles.background} onClick={() => setOpen(false)} />
      )}
    </>
  )
}

export default FilterButton
