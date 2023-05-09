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
import c from 'classnames'
import Icon from '~/components/ui/icon/icon'
import {useLists} from '~/store'

import {copyLists} from '~/lib/utils'

import styles from './header.module.scss'

export default function Header() {
  const lists = useLists()

  const [showCopied, setShowCopied] = useState(false)

  useEffect(() => {
    let tid = -1

    if (showCopied) {
      tid = setTimeout(() => {
        setShowCopied(false)
      }, 2000)
    }
    return () => {
      clearTimeout(tid)
    }
  }, [showCopied])

  return (
    <header className={styles.header}>
      <h1 className={styles.logo}>List It</h1>
      <nav>
        <ul className={styles.navList}>
          <li className={styles.navItem}>
            <span className={c(styles.copied, showCopied && styles.show)}>
              Copied!
            </span>
            <button
              type="button"
              name="copy-transcript"
              aria-label="Copy Transcript"
              tabIndex={0}
              onClick={() => {
                copyLists(lists)
                setShowCopied(true)
              }}
            >
              <Icon icon="copy_all" />
            </button>
          </li>
        </ul>
      </nav>
    </header>
  )
}
