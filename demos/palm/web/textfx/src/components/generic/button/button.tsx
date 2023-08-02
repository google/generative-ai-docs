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

import Icon, {Icons} from '../icon/icon'
import styles from './button.module.scss'
import c from 'classnames'

interface IButton {
  label: string
  variant:
    | 'dark'
    | 'dark_grey'
    | 'light_grey'
    | 'tennis'
    | 'white'
    | 'tomato'
    | 'lavender'
    | 'mint'
    | 'cardboard'
    | 'coral'
    | 'sky'
    | 'barbie'
    | 'marigold'
    | 'berry'
    | 'transparent'
    | string
  onClick: () => void
  size?: 'default' | 'reduced'
  disabled?: boolean
  uppercase?: boolean
  icon?: keyof typeof Icons
  className?: string
}

const Button = ({
  label,
  variant,
  onClick,
  size = 'default',
  disabled,
  uppercase,
  icon,
  className,
  ...rest
}: IButton) => {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={c(
        styles.root,
        styles[variant],
        size && styles[size],
        uppercase && styles.uppercase,
        disabled && styles.disabled,
        className
      )}
      {...rest}
    >
      {icon && <Icon name={icon as any} />}
      {label}
    </button>
  )
}

export default Button
