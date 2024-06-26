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

import styles from './hamburger.module.scss'
import c from 'classnames'

interface IHamburger {
  theme: string
  onClick: () => void
  showX: boolean
}

const Hamburger = ({theme, onClick, showX}: IHamburger) => {
  return (
    <button
      aria-label="openand close menu"
      type="button"
      tabIndex={0}
      className={c(
        styles.burgerContainer,
        {
          [styles.isOpen]: showX
        },
        styles[theme]
      )}
      onClick={onClick}
    >
      <span className={styles.burger}>
        <span className={c(styles.burgerLine, styles.burgerLine__top)} />
        <span className={c(styles.burgerLine, styles.burgerLine__middle)} />
        <span className={c(styles.burgerLine, styles.burgerLine__bottom)} />
      </span>
    </button>
  )
}

export default Hamburger
