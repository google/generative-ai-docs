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

import {useActions, useFilters} from '~/store'
import {macros} from '~/constants'

import Checkbox from '../checkbox/checkbox'
import Icon from '../icon/icon'

import styles from './filterList.module.scss'
import c from 'classnames'

const FilterList = () => {
  // const [filters, setFilters] = useState<string[]>(macros.map(e => e.id))
  const {filters} = useFilters()
  const {setFilters} = useActions()

  const handleFilterChangeById = (id: string) => {
    if (filters.findIndex((e: string) => e === id) > -1) {
      setFilters([...new Set(filters.filter((e: string) => e !== id))])
    } else {
      setFilters([...new Set([...filters, id])])
    }
  }

  const handleAllSelect = () => {
    if (filters.length === macros.length) {
      setFilters([])
    } else {
      setFilters([...macros.map(e => e.id)])
    }
  }

  return (
    <div className={c(styles.root)}>
      <ul>
        <li
          className={c(
            styles.macro,
            filters.length === macros.length && styles.active
          )}
        >
          <button onClick={handleAllSelect} className={styles.macroItem}>
            <Icon name="all" />
            <span>All</span>
          </button>
          <Checkbox
            checked={filters.length === macros.length}
            onChange={handleAllSelect}
          />
        </li>
        {macros.map(macro => {
          const inFilters =
            filters.findIndex((e: string) => e === macro.id) > -1
          return (
            <li
              key={macro.id}
              className={c(styles.macro, inFilters && styles.active)}
            >
              <button
                onClick={() => handleFilterChangeById(macro.id)}
                className={styles.macroItem}
              >
                <Icon name={macro.icon as any} />
                <span>{macro.name}</span>
              </button>
              <Checkbox
                checked={inFilters}
                onChange={() => handleFilterChangeById(macro.id)}
              />
            </li>
          )
        })}
      </ul>
    </div>
  )
}

export default FilterList
