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

import {create} from 'zustand'
import {v4 as uuid} from 'uuid'
import * as api from '~/lib/api'
import {getErrorMessage} from '~/lib/utils'

const useStore = create(set => ({
  lists: [],
  muted: false,
  restarted: false,
  loading: false,
  error: null,
  actions: {
    setMute: muted => set(() => ({muted})),
    setError: error => set(() => ({error})),
    addList: async query => {
      set(() => ({
        loading: true
      }))

      const result = await api.getListAndTip(query)

      if (result.error || result.items.length === 0) {
        set(() => ({
          loading: false,
          error: getErrorMessage(result.error || {code: 404})
        }))
        return
      }

      result.id = uuid()
      set(({lists}) => ({
        tip: result.tip,
        lists: [...lists, result],
        loading: false
      }))
      return {
        ...result
      }
    },
    replaceList: async (listId, query) => {
      const result = await api.getListAndTip(query)
      if (result.error || result.items.length === 0) {
        set(() => ({
          loading: false,
          error: getErrorMessage(result.error || {code: 404})
        }))
        return
      }

      const newList = {
        title: query,
        id: uuid(),
        items: result.items,
        tip: result.tip
      }

      set(({lists}) => ({
        tip: result.tip,
        lists: lists.map(list => (list.id === listId ? newList : list))
      }))

      return true
    },
    restart: () => {
      set(({restarted}) => ({
        lists: [],
        tip: null,
        restarted: !restarted,
        inputValue: '',
        error: null
      }))
    },
    getTip: (title, items) => api.getTip(title, items)
  }
}))

export const useActions = () => useStore(({actions}) => actions)
export const useLists = () => useStore(({lists}) => lists)
export const useRestarted = () => useStore(({restarted}) => restarted)
export const useIsloading = () => useStore(({loading}) => loading)
export const useIsError = () => useStore(({error}) => error)
