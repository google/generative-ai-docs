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

import {useEffect, useRef, useState, Fragment} from 'react'
import {useMacros, useActions} from '~/store'
import {IMacro, colors} from '~/constants'
import {find} from '~/lib/utils'
import Icon, {IIcon} from '~/components/generic/icon/icon'

import useIsMobile from '~/hooks/useIsMobile'
import useAnimationFrame from '~/hooks/useAnimationFrame'

import styles from './macroButtons.module.scss'
import c from 'classnames'

const KEYS = {
  arrow_left: 'ArrowLeft',
  arrow_up: 'ArrowUp',
  arrow_right: 'ArrowRight',
  arrow_down: 'ArrowDown',
  option: 'Alt'
}

const findNextMacro = (id: string, macros: IMacro[]) => {
  for (let i = 0; i < macros.length; i += 1) {
    if (id === macros[i].id) {
      return macros[i + 1] ? macros[i + 1] : macros[0]
    }
  }
  return null
}

const findPrevMacro = (id: string, macros: IMacro[]) => {
  for (let i = 0; i < macros.length; i += 1) {
    if (id === macros[i].id) {
      return macros[i - 1] ? macros[i - 1] : macros[macros.length - 1]
    }
  }
  return null
}

const MacroButtons = () => {
  const {macros, activeMacro} = useMacros()
  const {setMacro} = useActions()
  const activeMacroRef = useRef<IMacro | null>(activeMacro)
  const [activeMacroIndex, setActiveMacroIndex] = useState<number>(
    Math.floor(Math.random() * macros.length)
  )
  const [animationComplete, setAnimationComplete] = useState<boolean>(false)
  const controlDown = useRef<boolean>(false)
  const horizontalScrollWrapperRef = useRef<HTMLDivElement | null>(null)
  const isDesktop = useIsMobile(null, 'large')
  const isMobile = useIsMobile()
  const shuffleAnimation = useAnimationFrame()

  const animationCallback = () => {
    let velocity = 0.3
    let friction = 0.004
    let fps = 60
    let msPerFrame = (1 / fps) * 1000
    let currentPosition = activeMacroIndex

    return (dt: number) => {
      velocity = Math.max(0, velocity - (dt / msPerFrame) * friction)
      currentPosition += velocity

      setActiveMacroIndex(
        Math.max(0, Math.floor(currentPosition % macros.length))
      )

      if (velocity === 0) {
        setAnimationComplete(true)
      }
    }
  }

  useEffect(() => {
    if (animationComplete) {
      setMacro(macros[activeMacroIndex].id)
      shuffleAnimation.stop()
    }
  }, [animationComplete])

  useEffect(() => {
    const handleKeydown = (event: KeyboardEvent) => {
      if (!activeMacroRef.current) return

      if (event.key === KEYS.option) {
        controlDown.current = true
        return
      }

      if (!controlDown.current) return

      let newMacro: IMacro | null = null
      switch (event.key) {
        case KEYS.arrow_left:
        case KEYS.arrow_down:
          newMacro = findPrevMacro(activeMacroRef.current.id, macros)
          break
        case KEYS.arrow_up:
        case KEYS.arrow_right:
          newMacro = findNextMacro(activeMacroRef.current.id, macros)
          break
        default:
          break
      }

      if (!newMacro) return

      setMacro(newMacro.id)
    }

    const handleKeyup = (event: KeyboardEvent) => {
      if (event.key === KEYS.option) {
        controlDown.current = false
      }
    }

    document.addEventListener('keydown', handleKeydown)
    document.addEventListener('keyup', handleKeyup)

    if (isMobile) {
      setMacro(macros[Math.floor(Math.random() * macros.length)].id)
    } else {
      shuffleAnimation.start(animationCallback())
    }

    return () => {
      document.removeEventListener('keydown', handleKeydown)
      document.removeEventListener('keyup', handleKeyup)
    }
  }, [isMobile])

  useEffect(() => {
    if (!activeMacro) return

    shuffleAnimation.stop()
    activeMacroRef.current = activeMacro

    if (isDesktop === null || !isDesktop) return

    const activeMacroButton = find(`.js-macro-${activeMacro.name}`)[0]

    horizontalScrollWrapperRef?.current?.scrollTo({
      top: 0,
      left: activeMacroButton.offsetLeft - 20, // Padding
      behavior: 'smooth'
    })
  }, [activeMacro, isDesktop])

  return (
    <div
      ref={horizontalScrollWrapperRef}
      className={styles.horizontalScrollWrapper}
    >
      <ul
        className={c(
          styles.macroButtons,
          'container',
          activeMacro && styles.active
        )}
        style={{color: activeMacro ? activeMacro.color : colors.mid_grey}}
      >
        {macros?.map((macro: IMacro, i: number, macros: IMacro[]) => {
          const isActive = activeMacro
            ? activeMacro.id === macro.id
            : activeMacroIndex === i
          const isLast = i + 1 === macros.length

          return (
            <Fragment key={macro.id}>
              <li className={`js-macro-${macro.name}`}>
                <button
                  type="button"
                  aria-label={macro.name}
                  className={c(styles.macroButton, isActive && styles.isActive)}
                  tabIndex={0}
                  onClick={() => {
                    setMacro(macro.id)
                  }}
                >
                  <Icon
                    name={macro.icon as IIcon['name']}
                    className={styles.icon}
                  />
                  <span className={styles.text}>{macro.name}</span>
                </button>
              </li>
              {isLast && <li aria-hidden="true" className={styles.spacer} />}
            </Fragment>
          )
        })}
      </ul>
    </div>
  )
}

export default MacroButtons
