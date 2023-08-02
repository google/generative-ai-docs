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

import {useEffect, useState} from 'react'
import {useActions, useMacros, useShowPromptData} from '~/store'
import {promptData, IPromptDataItemData, IPromptData} from '~/constants'

import Hamburger from '~/components/generic/hamburger/hamburger'

import styles from './promptData.module.scss'
import c from 'classnames'

interface IPromptDataScreen {
  onClose: () => void
}

const PromptData = ({onClose = () => {}}: IPromptDataScreen) => {
  const [mounted, setMounted] = useState<boolean>(false)
  const [show, setShow] = useState<boolean>(false)
  const {activeMacro} = useMacros()
  const {showPromptData} = useShowPromptData()
  const {setShowPromptData} = useActions()

  useEffect(() => {
    if (showPromptData) {
      setShow(true)
      setTimeout(() => {
        setMounted(true)
      }, 100)
    } else {
      setMounted(false)
      setTimeout(() => {
        setShow(false)
        onClose()
      }, 500)
    }
  }, [showPromptData])

  if (!activeMacro?.id) {
    return null
  }

  const {data, description} = promptData[activeMacro.id as keyof IPromptData]
  return show ? (
    <div className={c(styles.promptDataScreen, mounted && styles.fadeIn)}>
      <Hamburger
        theme="light"
        showX={true}
        onClick={() => {
          setShowPromptData(false)
        }}
      />
      <div className="container">
        <div className={styles.content}>
          <h1>{activeMacro.name}</h1>
          <div className={styles.intro}>{description}</div>
          <ul className={styles.items}>
            {data.map((item: IPromptDataItemData) => {
              return (
                <li key={item.title} className={styles.item}>
                  <div className={styles.rowTitle}>{item.title}</div>
                  <div className={styles.table}>
                    {item.rows.map((row: any, i) => {
                      return (
                        <div
                          key={`${item.title}-row-${i}`}
                          className={c(
                            styles.tableRow,
                            i > 0 && styles.tableRowBorder
                          )}
                        >
                          {row.cols.map((col: any) => {
                            return (
                              <div
                                key={col.text}
                                className={c(
                                  styles.tableCol,
                                  col.background && styles[col.background],
                                  col.style && styles[col.style]
                                )}
                              >
                                {col.title && (
                                  <span className={styles.colTitle}>
                                    {col.title}
                                  </span>
                                )}
                                <div
                                  dangerouslySetInnerHTML={{
                                    __html: col.text.replaceAll('\n', '<br />')
                                  }}
                                />
                              </div>
                            )
                          })}
                        </div>
                      )
                    })}
                  </div>
                </li>
              )
            })}
          </ul>
        </div>
      </div>
    </div>
  ) : null
}

export default PromptData
