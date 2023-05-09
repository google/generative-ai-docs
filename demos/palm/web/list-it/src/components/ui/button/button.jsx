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

import styles from './button.module.scss'

const Button = ({
  children,
  disabled = false,
  onClick = null,
  icon = null,
  className = '',
  ariaLabel = ''
}) => {
  return (
    <button
      disabled={disabled}
      type="button"
      aria-label={ariaLabel}
      tabIndex="0"
      className={c(styles.button, className)}
      onClick={() => {
        if (onClick) {
          onClick()
        }
      }}
    >
      {icon && <Icon icon={icon} />}
      {children}
    </button>
  )
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  disabled: PropTypes.bool,
  onClick: PropTypes.func,
  icon: PropTypes.string,
  className: PropTypes.string,
  ariaLabel: PropTypes.string
}

export default Button
