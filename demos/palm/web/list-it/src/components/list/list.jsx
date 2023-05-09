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

import {useState, useEffect, useRef} from 'react'
import c from 'classnames'
import PropTypes from 'prop-types'

import Tip from '~/components/tip/tip'
import Button from '~/components/ui/button/button'
import Icon from '~/components/ui/icon/icon'
import Lightbulb from '~/assets/icons/lightbulb'

import {useIsloading, useActions} from '~/store'
import {capitalize} from '~/lib/utils'

import styles from './list.module.scss'

const List = ({id, title, items, tip, index, onScrollToList}) => {
  const [showTip, setShowTip] = useState(false)
  const [childList, setChildList] = useState([])
  const [animated, setAnimated] = useState(false)
  const [showLoadingButton, setShowLoadingButton] = useState(-1)
  const listRef = useRef(null)
  const isLoading = useIsloading()
  const {addList, replaceList} = useActions()
  const [isRegenerating, setIsRegenerating] = useState(false)

  const onAddListClick = async (query, index) => {
    setShowLoadingButton(index)

    const {id} = await addList(query)
    // react state needs a new array
    const newChildList = [...childList]
    newChildList[index] = id
    setChildList(newChildList)
  }

  useEffect(() => {
    // On Mount: scroll to the new list
    listRef.current.scrollIntoView({
      behavior: 'smooth',
      inline: 'nearest'
    })
    setAnimated(true)
  }, [])

  // reset button state after loading is complete
  useEffect(() => {
    if (!isLoading) {
      setShowLoadingButton(-1)
    }
  }, [isLoading])

  return (
    <div
      key={title}
      ref={listRef}
      className={c(
        styles.listBox,
        index === 0 && styles.isFirst && isLoading && styles.isLoading,
        animated && styles.animateIn
      )}
      data-list-id={id}
    >
      <div className={styles.animationContainer}>
        <div className={styles.listHead}>
          <h1 className="heading">{capitalize(title)}</h1>
        </div>
        <ul className={styles.list}>
          {items.map((item, index) => (
            <li key={item} className={c(styles.listItem, 'container')}>
              <span className={styles.listItemTitle}>{item}</span>
              {showLoadingButton === index ? ( // fetching list  show loading
                <button
                  disabled
                  aria-label="loading"
                  type="button"
                  className="circleButton"
                >
                  <div className={c(styles.spinner, 'spinner')} />
                </button>
              ) : childList[index] ? ( // has a child list
                <button
                  type="button"
                  aria-label={`Scroll to ${item} list`}
                  className="circleButton"
                  onClick={() => onScrollToList(childList[index])}
                >
                  <Icon icon="arrow_downward" />
                </button>
              ) : (
                // default state
                <button
                  type="button"
                  aria-label={`Add new list for ${item}`}
                  className="circleButton"
                  onClick={() => onAddListClick(item, index)}
                >
                  <Icon icon="playlist_add" />
                </button>
              )}
            </li>
          ))}
        </ul>
        {showTip && tip && (
          <div className={c('js-tip-box', styles.listTipBox)} data-list-id={id}>
            <Tip text={tip} error={tip.error} />
          </div>
        )}

        <div className={c(styles.listActions)}>
          {!showTip && (
            <Button
              ariaLabel={`Get a tip for ${title}`}
              onClick={() => setShowTip(true)}
            >
              <Lightbulb />
              <span>get a tip!</span>
            </Button>
          )}
          <Button
            disabled={isRegenerating}
            ariaLabel={`Regenerate ${title} list`}
            onClick={() => {
              setIsRegenerating(true)
              replaceList(id, title)
            }}
          >
            <span>regenerate list</span>
          </Button>
        </div>
      </div>
    </div>
  )
}

List.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  tip: PropTypes.string.isRequired,
  items: PropTypes.arrayOf(PropTypes.string).isRequired,
  index: PropTypes.number.isRequired,
  onScrollToList: PropTypes.func.isRequired
}

export default List
