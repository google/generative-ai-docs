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

import {useState, useRef, useEffect} from 'react'
import {useActions, useOutputPins} from '~/store'
import {DndProvider} from 'react-dnd'
import {HTML5Backend} from 'react-dnd-html5-backend'
import {TouchBackend} from 'react-dnd-touch-backend'
import {Preview} from 'react-dnd-preview'
import {macros} from '~/constants'

import Icon from '~/components/generic/icon/icon'
import PinnedCard from './pinnedCard'
import useIsMobile from '~/hooks/useIsMobile'
import useOnClickOutside from '~/hooks/useOnClickOutside'

import styles from './pinnedCards.module.scss'
import c from 'classnames'

const PinnedCards = () => {
  const rootRef = useRef<HTMLDivElement>(null)
  const cardSizerRef = useRef<HTMLDivElement>(null)
  const pins = useOutputPins()
  const [collapsed, setCollapsed] = useState<boolean | null>(null)
  const [copiedIndex, setCopiedIndex] = useState(-1)
  const {setPins} = useActions()
  const [cardHeight, setCardHeight] = useState('0px')
  const isMobile = useIsMobile()

  useOnClickOutside(rootRef, () => {
    if (!isMobile || collapsed) return

    setCollapsed(true)
  })

  useEffect(() => {
    setCardHeight(`${cardSizerRef.current?.offsetHeight}px`)
  }, [collapsed, pins])

  useEffect(() => {
    if (rootRef.current && cardHeight !== '0px') {
      rootRef.current.style.height = cardHeight
    }
  }, [cardHeight])

  const swap = (array: any, index1: number, index2: number) => {
    array[index1] = array.splice(index2, 1, array[index1])[0]
    return array
  }

  const movePin = (dragIndex: number, hoverIndex: number) => {
    setPins(swap(pins, dragIndex, hoverIndex))
  }

  useEffect(() => {
    if (isMobile === null) return

    setCollapsed(isMobile)
  }, [isMobile])

  const generatePreview = ({style}: {style: any}) => {
    return (
      <div className={styles.preview} style={style}>
        <PinnedCard
          pin={pins[0]}
          pins={pins}
          macro={macros[0]}
          setCopiedIndex={setCopiedIndex}
          index={0}
          movePin={movePin}
        />
      </div>
    )
  }

  return (
    <div
      ref={rootRef}
      className={c(
        styles.pinnedCards,
        collapsed && styles.collapsed,
        isMobile && styles.mobile
      )}
    >
      <div ref={cardSizerRef} className={c(styles.cardSizer)}>
        <button
          className={styles.cardHeader}
          onClick={() => setCollapsed(!collapsed)}
        >
          <h3>
            <Icon name="pin" />
            {`PINNED (${pins.length})`}
          </h3>
          <Icon className={c(styles.arrow)} name="collapseArrow" />
        </button>
        {isMobile !== null && (
          <DndProvider backend={!isMobile ? HTML5Backend : TouchBackend}>
            <ul className={c(styles.pins)}>
              {pins.length > 0 ? (
                pins.map((pin, i) => {
                  const macro = macros.find(macro => macro.slug === pin.macro)
                  return (
                    <li
                      key={`${pin.id}_${pin.index}`}
                      className={c(
                        copiedIndex === i && styles.copied,
                        styles.pin
                      )}
                    >
                      <PinnedCard
                        pin={pin}
                        pins={pins}
                        macro={macro}
                        setCopiedIndex={setCopiedIndex}
                        index={i}
                        movePin={movePin}
                      />
                    </li>
                  )
                })
              ) : (
                <li className={c(styles.pin, styles.noPins)}>
                  <p>You haven&apos;t pinned anything yet.</p>
                </li>
              )}
            </ul>
            {isMobile && <Preview generator={generatePreview} />}
          </DndProvider>
        )}
      </div>
    </div>
  )
}

export default PinnedCards
