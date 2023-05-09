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
import PropTypes from 'prop-types'

import Icon from '~/components/ui/icon/icon'

import Lightbulb from '~/assets/icons/lightbulb'

import styles from './tip.module.scss'

const Tip = ({text, error, onRefresh}) => {
  return (
    <div className={c(styles.tip)}>
      <div className={styles.textBox}>
        <div className={styles.icon}>
          <Lightbulb />
        </div>
        <span className={c('js-tip-text', styles.text)}>
          {!error && <strong>Tip:&nbsp;</strong>}
          {text}
        </span>
      </div>
      {!!onRefresh && !error && (
        <button
          type="button"
          className={c(styles.button, 'circleButton')}
          onClick={() => onRefresh()}
        >
          <Icon icon={'refresh'} />
        </button>
      )}
    </div>
  )
}

Tip.propTypes = {
  text: PropTypes.string.isRequired,
  error: PropTypes.bool,
  onRefresh: PropTypes.func
}

export default Tip
