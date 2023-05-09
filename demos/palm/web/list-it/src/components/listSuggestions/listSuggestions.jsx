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

import c from 'classnames'
import Button from '~/components/ui/button/button'
import {useActions} from '~/store'
import styles from './listSuggestions.module.scss'

const ListSuggestions = () => {
  const {addList} = useActions()

  return (
    <section className={c(styles.listSuggestions, 'container space-m')}>
      <span className={styles.label}>Think about big life events like...</span>
      <Button
        className={styles.button}
        onClick={() => {
          addList('move to a new city')
        }}
      >
        move to a new city
      </Button>
      <span className={styles.label}>or complex goals like...</span>
      <Button
        className={styles.button}
        onClick={() => {
          addList('write a memoir')
        }}
      >
        write a memoir
      </Button>
    </section>
  )
}

export default ListSuggestions
