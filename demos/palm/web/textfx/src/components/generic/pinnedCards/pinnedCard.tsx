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

import {useRef} from 'react'
import {useActions} from '~/store'
import type {Identifier, XYCoord} from 'dnd-core'
import {useDrag, useDrop} from 'react-dnd'
import {tippyOptions, IPin, IMacro} from '~/constants'

import Tippy from '@tippyjs/react'
import Icon from '~/components/generic/icon/icon'

import styles from './pinnedCards.module.scss'
import c from 'classnames'

const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
  } catch (err) {
    console.error('Failed to copy: ', err)
  }
}

interface IPinnedCard {
  pin: IPin
  pins: IPin[]
  macro?: IMacro
  setCopiedIndex: (index: number) => void
  index: number
  movePin: (dragIndex: number, hoverIndex: number) => void
}

interface IDragItem {
  index: number
  id: string
  type: string
}

const PinnedCard = ({
  pin,
  pins,
  macro,
  setCopiedIndex,
  index,
  movePin
}: IPinnedCard) => {
  const {pinOutput} = useActions()
  const ref = useRef<HTMLDivElement>(null)

  const [{handlerId}, drop] = useDrop<
    IDragItem,
    void,
    {handlerId: Identifier | null}
  >({
    accept: 'card',
    collect(monitor) {
      return {
        handlerId: monitor.getHandlerId()
      }
    },
    hover(item, monitor) {
      if (!ref.current) {
        return
      }
      const dragIndex = item.index
      const hoverIndex = index

      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return
      }

      // Determine rectangle on screen
      const hoverBoundingRect = ref.current?.getBoundingClientRect()

      // Get vertical middle
      const hoverMiddleY =
        (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2

      // Determine mouse position
      const clientOffset = monitor.getClientOffset()

      // Get pixels to the top
      const hoverClientY = (clientOffset as XYCoord).y - hoverBoundingRect.top

      // Only perform the move when the mouse has crossed half of the items height
      // When dragging downwards, only move when the cursor is below 50%
      // When dragging upwards, only move when the cursor is above 50%

      // Dragging downwards
      if (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) {
        return
      }

      // Dragging upwards
      if (dragIndex > hoverIndex && hoverClientY > hoverMiddleY) {
        return
      }

      movePin(dragIndex, hoverIndex)
      item.index = hoverIndex
    }
  })

  const [{isDragging}, drag, preview] = useDrag({
    type: 'card',
    item: () => {
      return {id: pin.id, index}
    },
    collect: monitor => ({
      isDragging: monitor.isDragging()
    })
  })

  const opacity = isDragging ? 0 : 1
  drag(drop(ref))

  const pinnedTextDisplay = (text: string) => {
    if (!macro) return text

    if (macro.slug !== 'unfold') return text

    return text.replaceAll('\n', ', ')
  }

  return (
    <div ref={ref} className={styles.pinnedCard} data-handler-id={handlerId}>
      <div ref={preview} style={{opacity}}>
        <div className={c(styles.pinHeader)}>
          <span className={styles.title}>
            <Tippy
              content={macro?.name}
              placement="top-start"
              {...tippyOptions}
              className={macro?.id}
            >
              <span className={styles.iconLine}>
                <Icon name={macro?.icon as any} />
                <span>{pin.input}</span>
              </span>
            </Tippy>
          </span>
        </div>
        <div className={styles.pinBody}>
          <p>{pinnedTextDisplay(pin.text)}</p>
          <div className={c(styles.pinActions)}>
            <Tippy
              content="Copy"
              placement="top-end"
              offset={[10, 10]}
              className={pin.id}
              {...tippyOptions}
            >
              <button
                type="button"
                aria-label="Copy"
                onClick={() => {
                  setCopiedIndex(index)
                  setTimeout(() => {
                    setCopiedIndex(-1)
                  }, 1000)
                  copyText(pin.text)
                }}
              >
                <Icon name="copy" />
              </button>
            </Tippy>
            <Tippy
              content="Unpin"
              placement="top-end"
              offset={[10, 10]}
              className={pin.id}
              {...tippyOptions}
            >
              <button
                className={c(
                  styles.pinButton,
                  pins.map(pin => pin.index).includes(index) && styles.pinned
                )}
                type="button"
                aria-label="Unpin"
                onClick={() => {
                  pinOutput(pin.id, pin.index)
                }}
              >
                <Icon name="pinSolid" />
              </button>
            </Tippy>
            <Tippy content="Drag" placement="top-end" {...tippyOptions}>
              <button
                ref={drag}
                className={c(styles.dragButton)}
                type="button"
                aria-label="Drag"
                onClick={() => {}}
              >
                <Icon name="drag" />
              </button>
            </Tippy>
          </div>
          <span className={c(styles.copied)}>Copied!</span>
        </div>
      </div>
    </div>
  )
}

export default PinnedCard
