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

import {useState} from 'react'
import {useOutputs, useFilters, useActions, useOutputPins} from '~/store'
import {IMacroOutput, tippyOptions} from '~/constants'

import Tippy from '@tippyjs/react'
import OutputCard from '../outputCard/outputCard'
import Icon from '~/components/generic/icon/icon'
import Popup from '../popup/popup'
import FilterButton from '../filterButton/filterButton'
import PinnedCards from '../pinnedCards/pinnedCards'
import useIsMobile from '~/hooks/useIsMobile'
import Portal from '../portal/portal'
import formatDownload from '~/lib/formatDownload'

import styles from './outputSection.module.scss'
import c from 'classnames'

const OutputSection = () => {
  const {outputs} = useOutputs()
  const pins = useOutputPins()
  const {deleteOutputs} = useActions()
  const [showPopup, setShowPopup] = useState<boolean>(false)
  const {filters} = useFilters()
  const isMobile = useIsMobile(null)

  const deleteAllOutputs = () => {
    deleteOutputs(outputs)
    setShowPopup(false)
  }

  const getDownload = (outputs: IMacroOutput[]) => {
    return `data:text/plain;charset=utf-8,${encodeURIComponent(
      formatDownload(outputs, pins)
    )}`
  }

  return (
    <section className={c(styles.outputSection, isMobile && styles.mobile)}>
      <header className={c('container')}>
        <div className={styles.heading}>
          <h2>OUTPUTS</h2>
          <span className={styles.disclaimer}>
            (may contain inaccurate or offensive information that does not
            represent Google&apos;s views)
          </span>
        </div>
        <div className={styles.headActions}>
          <div className={c(styles.filters)}>
            <FilterButton active={false} />
          </div>
          <div className={c(styles.actions)}>
            <Tippy content="Download all" {...tippyOptions}>
              <a
                title="Download all"
                href={getDownload(outputs)}
                download="outputs.txt"
              >
                <Icon name="download" />
              </a>
            </Tippy>

            <Tippy content="Delete all" {...tippyOptions}>
              <button
                title="Delete all"
                type="button"
                aria-label="Delete"
                onClick={() => setShowPopup(true)}
              >
                <Icon name="delete" />
              </button>
            </Tippy>
          </div>

          {showPopup && (
            <Popup
              onEscape={() => setShowPopup(false)}
              onOutsideClick={() => setShowPopup(false)}
              actions={[
                {
                  label: 'Yes',
                  onClick: () => deleteAllOutputs()
                },
                {
                  label: 'No',
                  onClick: () => setShowPopup(false)
                }
              ]}
              headline={'Delete Outputs'}
              label={'Are you sure you want to delete all outputs?'}
            />
          )}
        </div>
      </header>
      <div className={c('container', styles.outputsWrapper)}>
        <div className={styles.col}>
          {outputs
            .filter(
              (output: IMacroOutput) =>
                filters.findIndex(f => f === output.macro) > -1
            )
            .map((output: IMacroOutput) => (
              <OutputCard key={output.id} output={output} />
            ))}
        </div>
        <div className={c(styles.col, styles.stickyCol)}>
          {isMobile ? <Portal>{<PinnedCards />}</Portal> : <PinnedCards />}
        </div>
      </div>
    </section>
  )
}

export default OutputSection
