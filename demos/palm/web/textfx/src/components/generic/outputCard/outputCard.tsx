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
import {IMacroOutput} from '~/constants'
import {macros, tippyOptions} from '~/constants'
import {useActions, useOutputPins} from '~/store'
import {scrollIntoViewWithOffset} from '~/lib/utils'
import useWindowSize from '~/hooks/useWindowSize'
import {Swiper, SwiperSlide, SwiperRef} from 'swiper/react'
import {Pagination, Navigation} from 'swiper'

import Tippy from '@tippyjs/react'
import ViewAllToggle from '../viewAllToggle/viewAllToggle'
import Icon from '~/components/generic/icon/icon'
import useAnimationFrame from '~/hooks/useAnimationFrame'

import styles from './outputCard.module.scss'
import c from 'classnames'

const copyText = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
  } catch (err) {
    console.error('Failed to copy: ', err)
  }
}

const OutputCard = ({output}: {output: IMacroOutput}) => {
  const rootRef = useRef<HTMLDivElement>(null)
  const pins = useOutputPins(output.id)
  const drawInTextRef = useRef<HTMLDivElement>(null)
  const cardSizerRef = useRef<HTMLDivElement>(null)
  const size = useWindowSize()
  const macro = macros.find(macro => macro.slug === output.macro)
  const {color, icon, loadingAnimation} = macro || {}
  const [index, setIndex] = useState<number>(0)
  const [copiedIndex, setCopiedIndex] = useState<number>(-1)
  const [viewAll, setViewAll] = useState<boolean>(false)
  const [cardHeight, setCardHeight] = useState<string>('0px')
  const [loadingAnimationComplete, setLoadingAnimationComplete] = useState(
    () => {
      // TODO: Check why this is re-mounting when you click run twice
      return output.outputs.length > 0
    }
  )
  const [drawingText, setDrawingText] = useState(false)
  const loadedRef = useRef(false)
  const {deleteOutputs, pinOutput, reRunOutput} = useActions()

  const swiperRef = useRef<SwiperRef | null>(null)
  const nextRef = useRef<HTMLButtonElement | null>(null)
  const prevRef = useRef<HTMLButtonElement | null>(null)
  const dotsRef = useRef<HTMLDivElement | null>(null)
  const MAX_BULLETS = 20

  const animation = useAnimationFrame()

  const handleNumberToggleClick = () => {
    if (viewAll) {
      setViewAll(false)
      setIndex(0)
    }
  }

  const {inputs} = output
  const text =
    typeof macro === 'undefined'
      ? ''
      : macro.getCardLabel
      ? macro.getCardLabel(inputs)
      : inputs.join(' ')

  const [labelText, setLabelText] = useState<string>(text)

  const animationCallback = (text: string) => {
    if (loadedRef.current) {
      const characterPerSecond = 250
      // Total duration is capped at 250ms so long text doesn't take forever to draw in
      const duration = Math.min(250, 1000 * (text.length / characterPerSecond))
      let now = 0

      return (dt: number) => {
        if (now > duration) {
          setDrawingText(false)
          return
        }
        now += dt
        if (drawInTextRef.current)
          drawInTextRef.current.innerHTML = text
            .substring(0, Math.floor(text.length * (now / duration)))
            .split('\n')
            .join('<br />')
      }
    }

    if (!loadingAnimation || !text) return

    const getText = loadingAnimation(text)

    return (dt: number) => {
      const modifiedText = getText(Math.max(4, dt), loadedRef.current)

      if (modifiedText) {
        setLabelText(modifiedText)
      } else {
        setLoadingAnimationComplete(true)
      }
    }
  }

  useEffect(() => {
    animation.stop()
    setLabelText(text)

    if (cardSizerRef.current) {
      setCardHeight(`${cardSizerRef.current?.offsetHeight}px`)
    }

    if (loadingAnimationComplete) {
      setDrawingText(true)
    }
  }, [loadingAnimationComplete])

  // Catch line breaks that happens during the animation
  useEffect(() => {
    if (cardSizerRef.current) {
      setCardHeight(`${cardSizerRef.current?.offsetHeight}px`)
    }
  }, [labelText])

  useEffect(() => {
    if (drawingText) {
      animation.start(animationCallback(output.outputs[0] || ''))
    } else {
      animation.stop()
    }
  }, [drawingText])

  useEffect(() => {
    setCardHeight(`${cardSizerRef.current?.offsetHeight}px`)
  }, [viewAll, size])

  useEffect(() => {
    if (viewAll) return

    scrollIntoViewWithOffset(rootRef, 58 + 13) // header + output card margin bottom
  }, [viewAll])

  useEffect(() => {
    if (!macro || !loadingAnimation) return

    const {inputs} = output
    const text = macro.getCardLabel
      ? macro.getCardLabel(inputs)
      : inputs.join(' ')

    if (output.outputs.length === 0) {
      animation.start(animationCallback(text || ''))
    } else {
      loadedRef.current = true
    }
  }, [output.outputs])

  useEffect(() => {
    if (rootRef.current && cardHeight !== '0px') {
      rootRef.current.style.height = cardHeight
    }
  }, [cardHeight])

  const cardBody = ({
    idx,
    isPinned,
    outputText,
    numbers
  }: {
    idx: number
    isPinned: boolean
    outputText: string
    numbers: boolean
  }) => {
    return (
      <>
        {numbers && <span className={c(styles.numbers)}>{idx + 1}</span>}
        {index === idx && drawingText ? (
          <p className={c(styles.drawInText)}>
            <span ref={drawInTextRef}></span>
            <span
              dangerouslySetInnerHTML={{
                __html: outputText.split('\n').join('<br>')
              }}
            />
          </p>
        ) : (
          <p
            dangerouslySetInnerHTML={{
              __html: `${outputText.split('\n').join('<br>')}`
            }}
          />
        )}
        <div className={c(styles.outputActions)}>
          <Tippy
            content="Copy"
            placement="top-end"
            offset={[10, 10]}
            {...tippyOptions}
          >
            <button
              type="button"
              aria-label="Copy"
              className={styles.copyButton}
              onClick={() => {
                setCopiedIndex(idx)
                setTimeout(() => {
                  setCopiedIndex(-1)
                }, 1000)
                copyText(outputText)
              }}
            >
              <Icon name="copy" />
            </button>
          </Tippy>
          <Tippy
            content="Pin"
            placement="top-end"
            offset={[10, 10]}
            className={macro?.id}
            {...tippyOptions}
          >
            <button
              className={c(styles.pinButton, isPinned && styles.pinned)}
              type="button"
              aria-label="Pin"
              onClick={() => {
                pinOutput(output.id, idx, labelText)
              }}
            >
              <Icon name={isPinned ? 'pinSolid' : 'pin'} />
            </button>
          </Tippy>

          <span className={c(styles.copied)}>Copied!</span>
        </div>
      </>
    )
  }

  return (
    <div
      key={`card-${output.id}`}
      ref={rootRef}
      className={c(
        styles.outputCard,
        output.outputs.length > 0 && styles.loaded,
        !viewAll ? styles.collapsed : styles.expanded,
        // output.outputs.length === 1 && styles.error,
        output.outputs.length === 1 && styles.isSingleOutput,
        styles[output.macro]
      )}
    >
      <div ref={cardSizerRef} className={c(styles.cardSizer)}>
        <div className={c(styles.cardHeader)}>
          <span className={styles.title} style={{color}}>
            <Tippy
              content={macro?.name}
              placement="top-start"
              {...tippyOptions}
              className={macro?.id}
            >
              <span className={styles.iconLine}>
                <Icon name={icon as any} />
                <span>{macro?.name}</span>
              </span>
            </Tippy>

            <span className={styles.temp}>Temp {output.randomness}</span>
          </span>
          <h3
            style={{color}}
            className={c(loadingAnimationComplete && styles.animationComplete)}
          >
            {labelText}
          </h3>
          <div className={styles.actions}>
            <Tippy content="Re-run" {...tippyOptions} className={macro?.id}>
              <button
                type="button"
                aria-label="Re-run"
                onClick={() => {
                  reRunOutput(output.id)
                }}
              >
                <Icon name="refresh" />
              </button>
            </Tippy>
            <Tippy content="Delete" {...tippyOptions} className={macro?.id}>
              <button
                type="button"
                aria-label="Delete"
                onClick={() => {
                  deleteOutputs([output])
                }}
              >
                <Icon name="delete" />
              </button>
            </Tippy>
          </div>
        </div>
        {output.outputs.length > 0 && loadingAnimationComplete && (
          <>
            <div
              className={c(
                styles.outputs,
                viewAll && styles.viewAll,
                loadingAnimationComplete && styles.animationComplete
              )}
            >
              {viewAll ? (
                output.outputs.map((outputText, i) => {
                  const isPinned = pins.map(pin => pin.index).includes(i)

                  return (
                    <div
                      key={`outputText-${outputText}-${i}`}
                      className={c(
                        styles.output,
                        index === i && styles.current,
                        copiedIndex === i && styles.copied,
                        styles[output.macro]
                      )}
                    >
                      {cardBody({
                        idx: i,
                        isPinned,
                        outputText,
                        numbers: true
                      })}
                    </div>
                  )
                })
              ) : (
                <>
                  <div className={styles.swiperBox}>
                    <button
                      ref={prevRef}
                      className={c(styles.prevButton)}
                      // onClick={() => handleNextOrPreviousClick(false)}
                    >
                      <svg
                        width="5"
                        height="9"
                        viewBox="0 0 5 9"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          d="M4.125 0.749999L5 1.625L2.125 4.5L5 7.375L4.125 8.25L0.374999 4.5L4.125 0.749999Z"
                          fill={'currentColor'}
                        />
                      </svg>
                    </button>
                    <button
                      ref={nextRef}
                      className={c(styles.nextButton)}
                      // onClick={() => handleNextOrPreviousClick(false)}
                    >
                      <svg
                        width="5"
                        height="9"
                        viewBox="0 0 5 9"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          d="M4.125 0.749999L5 1.625L2.125 4.5L5 7.375L4.125 8.25L0.374999 4.5L4.125 0.749999Z"
                          fill={'currentColor'}
                        />
                      </svg>
                    </button>
                    <Swiper
                      ref={swiperRef}
                      slidesPerView={1}
                      loop
                      simulateTouch={false}
                      autoHeight
                      onBeforeSlideChangeStart={() => {
                        if (cardHeight === 'auto') return

                        setCardHeight('auto')
                      }}
                      pagination={{
                        el: dotsRef.current,
                        dynamicBullets: output.outputs.length >= MAX_BULLETS,
                        dynamicMainBullets: MAX_BULLETS,
                        clickable: true
                      }}
                      navigation={{
                        prevEl: prevRef.current,
                        nextEl: nextRef.current
                      }}
                      modules={[Pagination, Navigation]}
                      // speed={0}
                    >
                      {output.outputs.map((outputText, i) => {
                        const isPinned = pins.map(pin => pin.index).includes(i)
                        return (
                          <SwiperSlide key={i}>
                            <div
                              key={`outputText-${outputText}-${i}`}
                              className={c(
                                styles.output,
                                index === i && styles.current,
                                copiedIndex === i && styles.copied
                              )}
                            >
                              {cardBody({
                                idx: i,
                                isPinned,
                                outputText,
                                numbers: false
                              })}
                            </div>
                          </SwiperSlide>
                        )
                      })}
                    </Swiper>
                  </div>
                </>
              )}
            </div>
            <div
              role="none"
              onClick={handleNumberToggleClick}
              className={styles.displayButtons}
            >
              {!viewAll && (
                <div className={styles.dotsBox}>
                  <div
                    ref={dotsRef}
                    className={c(
                      styles.dots,
                      output.outputs.length >= 20 && styles.dynamicBullets
                    )}
                  />
                </div>
              )}
              {output.outputs.length > 1 && (
                <ViewAllToggle
                  selected={viewAll}
                  onClick={e => {
                    if (cardHeight === 'auto') {
                      // Change it back from auto befor animating
                      setCardHeight(`${cardSizerRef.current?.offsetHeight}px`)
                    }
                    setViewAll(e)
                  }}
                />
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default OutputCard
