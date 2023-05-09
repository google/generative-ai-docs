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
import c from 'classnames'
import Header from '~/components/ui/header/header'
import Spacer from '~/components/ui/spacer/spacer'
import ErrorComponent from '~/components/ui/errorComponent/errorComponent'
import List from '~/components/list/list'
import ListLoading from '~/components/listLoading/listLoading'
import ListSuggestions from '~/components/listSuggestions/listSuggestions'
import Textarea from '~/components/textarea/textarea'
import {useActions} from '~/store'

import {useIsMobile, useIsTouchDevice} from '~/lib/utils'

import {useLists, useIsloading, useIsError} from '~/store'

export default function App() {
  const {addList, restart} = useActions()
  const listsRef = useRef({})
  const lists = useLists()
  const error = useIsError()
  const isLoading = useIsloading()
  const isMobile = useIsMobile()
  const isTouch = useIsTouchDevice()

  return (
    <>
      <Header />
      <main className={c(isTouch && 'isTouch')}>
        <Textarea
          prefix="I want to"
          onSubmit={({query}) => {
            addList(query)
          }}
          onRestart={() => restart()}
          showRestart={!!lists.length}
        />

        {!isLoading && !lists.length && <ListSuggestions />}

        {isLoading && lists.length === 0 && <ListLoading />}

        {!error ? (
          <section className="space-m">
            <ul>
              {lists.map((list, i) => (
                <li
                  key={list.id}
                  ref={ref => {
                    listsRef.current[list.id] = ref
                    return ref
                  }}
                >
                  <List
                    id={list.id}
                    title={list.title}
                    items={list.items}
                    tip={list.tip}
                    index={i}
                    onScrollToList={listId => {
                      listsRef.current[listId].scrollIntoView({
                        behavior: 'smooth',
                        inline: 'nearest'
                      })
                    }}
                  />
                  {lists.length - 1 !== i && isMobile && <Spacer />}
                </li>
              ))}
            </ul>
          </section>
        ) : (
          <ErrorComponent error={error} query={'test'} />
        )}
      </main>
    </>
  )
}
