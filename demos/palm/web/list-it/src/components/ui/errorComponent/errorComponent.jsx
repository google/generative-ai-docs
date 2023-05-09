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

import {useRef, useEffect} from 'react'
import c from 'classnames'
import PropTypes from 'prop-types'
import Button from '~/components/ui/button/button'
import {useActions} from '~/store'
import {capitalize} from '~/lib/utils'

import styles from './errorComponent.module.scss'

const ErrorComponent = ({error}) => {
  const errorRef = useRef(null)
  const {addList, restart, setError} = useActions()

  const onButtonClick = () => {
    if (error.type === 'technical') {
      setError(null)
      addList(error.query)
    } else {
      restart()
    }
  }

  useEffect(() => {
    // Timeout needed otherwise the animation will not be triggered
    setTimeout(() => {
      errorRef.current.classList.add(styles.animateIn)
    }, 100)
  }, [])

  return (
    <div ref={errorRef} className={c(styles.error, 'container')}>
      <h1 className={styles.heading}>{capitalize(error.query)}</h1>
      <div className={styles.errorBox}>
        <p className={styles.message}>{error.message}</p>
        <Button onClick={() => onButtonClick()}>
          <span>{error.type === 'technical' ? 'retry' : 'restart demo'}</span>
        </Button>
      </div>
    </div>
  )
}

ErrorComponent.propTypes = {
  error: PropTypes.shape({
    type: PropTypes.string.isRequired,
    message: PropTypes.string.isRequired,
    query: PropTypes.string
  }).isRequired
}

export default ErrorComponent
