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

import {macros, IMacro, IMacroOutput, IPin} from '~/constants'

interface AppState {
  macros: IMacro[]
  outputs: IMacroOutput[]
  pins: IPin[]
  filters: string[]
  activeMacro: IMacro | null
  showAbout: boolean
  showPromptData: boolean
  showNav: boolean
  actions: {
    setShowAbout: (showAbout: boolean) => void
    setShowPromptData: (showPromptData: boolean) => void
    setShowNav: (showNav: boolean) => void
    setPins: (pins: IPin[]) => void
    setMacro: (macroId: string) => void
    addOutput: (inputs: string[], randomness: number) => void
    reRunOutput: (macroId: string) => void
    setFilters: (filters?: string[]) => void
    deleteOutputs: (outputs: IMacroOutput[]) => void
    pinOutput: (outputId: string, index: number, input?: string) => void
  }
}

const useStore = create<AppState>((set, get) => ({
  macros,
  outputs: [],
  pins: [],
  filters: macros.map(macro => macro.id),
  activeMacro: null,
  showAbout: false,
  showPromptData: false,
  showNav: false,
  actions: {
    setShowAbout: (showAbout: boolean) => {
      set({
        showAbout
      })
    },
    setShowPromptData: (showPromptData: boolean) => {
      set({
        showPromptData
      })
    },
    setShowNav: (showNav: boolean) => {
      set({
        showNav
      })
    },
    setMacro: (macroId: string) => {
      const activeMacro = macros.find(macro => macro.id === macroId)
      document.documentElement.style.setProperty(
        '--color-highlight',
        activeMacro?.color || null
      )

      sessionStorage.setItem('macroId', macroId)
      set({
        activeMacro
      })
    },
    setPins: (pins: IPin[]) => {
      set({
        pins
      })
    },
    /**
     * Adds a new output card, passes data to the api, then updates the output
     * card when the api call returns the results
     *
     * @param {String[]} inputs An array of values to pass to the api function
     * @param {Number} randomness A number from 0 to 1
     */
    addOutput: async (inputs: string[], randomness: number) => {
      const {activeMacro} = get()
      if (!activeMacro) return

      const id = uuid()
      const new_output = {
        id,
        inputs,
        macro: activeMacro.id,
        outputs: [],
        pins: [],
        randomness
      }

      set({
        outputs: [new_output, ...get().outputs]
      })

      const apiOutputs = await activeMacro.apiFunction(...inputs, randomness)

      // update outputs when api call is done
      const {outputs} = get()

      const outputIndex = outputs.findIndex(output => output.id === id)
      outputs.splice(
        outputIndex,
        1,
        Object.assign(new_output, {outputs: apiOutputs})
      )

      set({
        outputs
      })
    },
    reRunOutput: async (outputId: string) => {
      const {outputs, macros} = get()

      const output = outputs.find(o => o.id === outputId)
      if (!output) return

      const macro = macros.find(macro => macro.slug === output.macro)
      if (!macro) return

      const id = uuid()
      const new_output = {
        id,
        inputs: output.inputs,
        macro: macro.id,
        outputs: [],
        pins: [],
        randomness: output.randomness
      }

      set({
        outputs: [new_output, ...outputs]
      })

      const apiOutputs = await macro.apiFunction(
        ...output.inputs,
        output.randomness
      )

      set({
        outputs: [Object.assign(new_output, {outputs: apiOutputs}), ...outputs]
      })
    },
    pinOutput: (outputId: string, index: number, input?: string) => {
      const {pins} = get()

      const pin = pins.findIndex(p => p.id === outputId && p.index === index)
      if (pin !== -1) {
        pins.splice(pin, 1)
        set({
          pins: [...pins]
        })
        return
      }

      const {outputs} = get()
      const output = outputs.find(o => o.id === outputId)

      if (!output) return

      set({
        pins: [
          {
            id: outputId,
            index,
            text: output.outputs[index],
            macro: output.macro,
            input
          },
          ...pins
        ]
      })
    },
    deleteOutputs: (outputs: IMacroOutput[]) => {
      const {outputs: currentOutputs, macros} = get()
      const newOutputs = currentOutputs.filter(
        output => outputs.findIndex(o => o.id === output.id) === -1
      )
      set({
        outputs: newOutputs,
        filters: macros.map(macro => macro.id)
      })
    },
    setFilters: (filters = []) => {
      set({
        filters
      })
    }
  }
}))

export const useActions = () => useStore(({actions}) => actions)
export const useMacros = () =>
  useStore(({macros, activeMacro}) => {
    return {
      macros,
      activeMacro
    }
  })
export const useOutputs = () =>
  useStore(({outputs}) => {
    return {
      outputs
    }
  })
export const useOutputPins = (id?: string) =>
  useStore(({pins}) => {
    if (id) return pins.filter(pin => pin.id === id)
    return pins
  })
export const useFilters = () =>
  useStore(({filters}) => {
    return {
      filters
    }
  })
export const useShowAbout = () =>
  useStore(({showAbout}) => {
    return {
      showAbout
    }
  })

export const useShowPromptData = () =>
  useStore(({showPromptData}) => {
    return {
      showPromptData
    }
  })

export const useShowNav = () =>
  useStore(({showNav}) => {
    return {
      showNav
    }
  })
