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
import Loading from '~/components/ui/loading/loading'

import styles from './listLoading.module.scss'

const ListLoading = () => {
  return (
    <section className={c(styles.listLoading, 'container space-m')}>
      <Loading text="Loading..." className={styles.spinner} />
    </section>
  )
}

export default ListLoading
