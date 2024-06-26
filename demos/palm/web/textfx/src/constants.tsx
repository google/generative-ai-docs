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

import {ReactElement} from 'react'

import {
  runSimile,
  runExplode,
  runScene,
  runChain,
  runPOV,
  runAcronym,
  runAlliteration,
  runFuse,
  runUnexpect,
  runUnfold
} from '~/lib/macros'

import {
  SIMILE_PROMPT_COMPONENTS,
  EXPLODE_PROMPT_COMPONENTS,
  UNEXPECT_PROMPT_COMPONENTS,
  CHAIN_PROMPT_COMPONENTS,
  POV_PROMPT_COMPONENTS,
  ALLITERATION_PROMPT_COMPONENTS,
  ACRONYM_PROMPT_COMPONENTS,
  FUSE_PROMPT_COMPONENTS,
  SCENE_PROMPT_COMPONENTS,
  UNFOLD_PROMPT_COMPONENTS
} from '~/lib/priming'

import adaptPromptData from '~/lib/adaptPromptDataFormat'

declare global {
  /* eslint-disable-next-line no-unused-vars */
  interface Window {
    dataLayer: any
    webkitSpeechRecognition: any
  }
}

export interface IBreakPoints {
  medium: number
  large: number
  [x: string]: number
}

export const breakPoints: IBreakPoints = {
  medium: 680,
  large: 1180
}

export const colors = {
  dark: '#151515',
  dark_grey: '#2c2c2c',
  mid_grey: '#666666',
  light_grey: '#999999',
  tennis: '#DAEF68',
  tomato: '#e24326',
  lavender: '#C0BAF2',
  mint: '#73D29E',
  cardboard: '#BAA694',
  coral: '#FF8C67',
  sky: '#81C2EC',
  barbie: '#FA9CC6',
  marigold: '#FFCE00',
  berry: '#8F9BFF',
  water: '#91FAED'
}

export interface IWatchLupeUseItVideos {
  [x: string]: string
}

export const watchLupeUseItVideos: IWatchLupeUseItVideos = {
  simile: 'https://storage.googleapis.com/textfx-assets/WLUI_SIMILE.mp4',
  explode: 'https://storage.googleapis.com/textfx-assets/WLUI_EXPLODE.mp4',
  unexpect: 'https://storage.googleapis.com/textfx-assets/WLUI_UNEXPECT.mp4',
  chain: 'https://storage.googleapis.com/textfx-assets/WLUI_CHAIN.mp4',
  pov: 'https://storage.googleapis.com/textfx-assets/WLUI_POV.mp4',
  alliteration:
    'https://storage.googleapis.com/textfx-assets/WLUI_ALLITERATION.mp4',
  acronym: 'https://storage.googleapis.com/textfx-assets/WLUI_ACRONYM.mp4',
  fuse: 'https://storage.googleapis.com/textfx-assets/WLUI_FUSE.mp4',
  scene: 'https://storage.googleapis.com/textfx-assets/WLUI_SCENE.mp4',
  unfold: 'https://storage.googleapis.com/textfx-assets/WLUI_UNFOLD.mp4'
}

export interface IMacro {
  id: string
  name: string
  slug: string
  icon: string
  description: string
  color: string
  videoUrl: string
  lottie: string
  loadingAnimation: Function
  inputs: {
    label: string
    placeholder: string[]
    maxLength?: number | string
    allowSpaces?: boolean
    maxLengthDescription?: string
    type?: string
  }[]
  apiFunction: Function
  getCardLabel?: Function
  textLabel: string
}

export const macros: IMacro[] = [
  {
    id: 'simile',
    name: 'Simile',
    slug: 'simile',
    icon: 'simile',
    textLabel: '============= SIMILE =============',
    description: 'Create a simile about a thing or concept.',
    color: colors.tennis,
    videoUrl: watchLupeUseItVideos.simile,
    lottie: 'simile_hero_animation_lottie',
    /**
     * SIMILE ANIMATION
     * Replace the letters of the input with = until the output is loaded.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = 0
      let modifiedText = ''
      let complete = false

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          iteration++
          lastTime = now
          const arr = text.split('')

          const i = Math.abs(
            (iteration % (text.length * 2)) - Math.floor(text.length)
          )

          modifiedText = arr
            .map(letter => (Math.random() > i / text.length ? '=' : letter))
            .join('')
          if (loaded && i === 0) complete = true
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a thing or concept:',
        placeholder: [
          'waiting',
          'a dilemma',
          'keeping a secret',
          'an epiphany',
          'starting over',
          'a process'
        ],
        maxLength: 25
      }
    ],
    apiFunction: runSimile
  },
  {
    id: 'explode',
    name: 'Explode',
    slug: 'explode',
    icon: 'explode',
    textLabel: '/-A-\\ /-A-\\ / EXPLODE \\ /-A-\\ /-A-\\',
    description: 'Break a word into similar-sounding phrases.',
    color: colors.lavender,
    videoUrl: watchLupeUseItVideos.explode,
    lottie: 'explode_hero_animation_lottie',
    /**
     * EXPLODE ANIMATION
     * Put /\• between the letters of the input until the output is loaded.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = text.length || 0
      let modifiedText = ''
      let complete = false
      let chars = ['/', '\\']

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          iteration++
          lastTime = now
          const arr = text.split('')

          const i = Math.abs(
            (iteration % (text.length * 2)) - Math.floor(text.length)
          )

          if (i > text.length - 1) {
            arr.unshift(...arr.splice(0, i).join('•'))
          } else {
            arr.unshift(
              ...arr
                .splice(0, i)
                .map((letter, i) => `${letter}${chars[i % 2]}`)
                .join('')
            )
          }

          modifiedText = arr.join('')
          if (loaded && i === 0) complete = true
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a word:',
        placeholder: [
          'viability',
          'helicopter',
          'clarify',
          'serendipity',
          'organize',
          'planetarium'
        ],
        maxLength: 15,
        allowSpaces: false
      }
    ],
    apiFunction: runExplode
  },
  {
    id: 'unexpect',
    name: 'Unexpect',
    slug: 'unexpect',
    icon: 'unexpect',
    textLabel: '?????????????? UNEXPECT ???????????',
    description: 'Make a scene more unexpected and imaginative.',
    color: colors.mint,
    videoUrl: watchLupeUseItVideos.unexpect,
    lottie: 'unexpect_hero_animation_lottie',
    /**
     * UNEXPECT ANIMATION
     * Replace each letter in the input with a _ in sequence; include a /// spinner that turns into ??? when the output is loaded.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = 0
      let modifiedText = ''
      let complete = false
      let countdown = 5
      const spinner_chars = ['/', '—', '\\', '|']

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          iteration++
          lastTime = now
          const arr = text.split('')
          const i = Math.floor(Math.random() * text.length)
          arr.splice(i, 1, '_')
          if (loaded) countdown--
          const spinner1 = loaded
            ? countdown > 2
              ? '?'
              : ' '
            : spinner_chars[iteration % 4]
          const spinner2 = loaded
            ? countdown > 1
              ? '?'
              : ' '
            : spinner_chars[iteration % 4]
          const spinner3 = loaded
            ? countdown > 0
              ? '?'
              : ' '
            : spinner_chars[iteration % 4]
          modifiedText = `${arr.join('')} ${spinner1}${spinner2}${spinner3}`
          if (loaded && countdown === 0) complete = true
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a scene:',
        placeholder: [
          'a glass of water',
          'making a sandwich',
          'a key',
          'changing a lightbulb',
          'a game of chess',
          'paragliding'
        ],
        maxLength: 25
      }
    ],
    apiFunction: runUnexpect
  },
  {
    id: 'chain',
    name: 'Chain',
    slug: 'chain',
    icon: 'chain',
    textLabel: 'o-o-o-o-o-o-o CHAIN o-o-o-o-o-o-o-o',
    description: 'Build a chain of semantically related items.',
    color: colors.cardboard,
    videoUrl: watchLupeUseItVideos.chain,
    lottie: 'chain_hero_animation_lottie',
    /**
     * CHAIN ANIMATION
     * Loop with an arrow until the output is loaded.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = 0
      let modifiedText = ''
      let complete = false

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          iteration--
          lastTime = now
          const arr = `»${text}`.split('')
          const i = iteration % (text.length + 1)
          arr.unshift(...arr.splice(i))
          modifiedText = arr.join('')
          if (loaded && i === 0) complete = true
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a word:',
        placeholder: ['picture', 'ball', 'layer', 'soil', 'glass', 'coin'],
        maxLength: 15
      }
    ],
    apiFunction: runChain
  },
  {
    id: 'pov',
    name: 'POV',
    slug: 'pov',
    icon: 'pov',
    textLabel: '^ ⦿ ⌄ ^ ⦿ ⌄   P.O.V.   ^ ⦿ ⌄ ^ ⦿ ⌄',
    description: 'Evaluate a topic through different points of view.',
    color: colors.coral,
    videoUrl: watchLupeUseItVideos.pov,
    lottie: 'pov_hero_animation_lottie',
    /**
     * POV ANIMATION
     * Shuffle the letters of the input until the output is loaded, then unshufle from the beginning.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = 0
      let modifiedText = ''
      let complete = false

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          if (loaded) iteration++
          lastTime = now
          const arr = text.split('')

          const i = iteration % text.length

          modifiedText = arr
            .concat(arr.splice(i).sort(() => Math.random() - 0.5))
            .join('')
          if (loaded && i === 0) complete = true
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a topic:',
        placeholder: [
          'analog clocks',
          'succulents',
          'minivans',
          'turtlenecks',
          'vegan desserts',
          'Sundays'
        ],
        maxLength: 25
      }
    ],
    apiFunction: runPOV
  },
  {
    id: 'alliteration',
    name: 'Alliteration',
    slug: 'alliteration',
    icon: 'alliteration',
    textLabel: 'A_A_ A_A_  ALLITERATION  A_A_ A_A_ ',
    description: 'Curate topic-specific words that start with a chosen letter.',
    color: colors.sky,
    videoUrl: watchLupeUseItVideos.alliteration,
    lottie: 'alliteration_hero_animation_lottie',
    /**
     * ALLITERATION ANIMATION
     * Shuffle the letters of the input until the output is loaded, then unshufle from the beginning.
     */
    loadingAnimation: (text: string) => {
      let fps = 10
      let interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = 0
      let modifiedText = ''
      let complete = false
      let j = 0

      const [inputText, letter] = text.split(/\sstarting with\s/)

      const startingWithText = ` starting with ${letter}`

      return (dt: number, loaded: boolean) => {
        now += dt
        interval = 1000 / fps
        if (now - lastTime > interval) {
          if (loaded) iteration++
          lastTime = now
          const arr = inputText.split('')
          const i = j > 0 ? inputText.length - 1 : iteration % inputText.length

          modifiedText = arr
            .concat(arr.splice(i).sort(() => Math.random() - 0.5))
            .join('')
          if (loaded && i === inputText.length - 1) {
            fps = 60
            j += 2
            modifiedText = `${modifiedText}${startingWithText.substring(0, j)}`
            if (j >= startingWithText.length - 1) {
              complete = true
            }
          }
        }

        if (complete) return false
        return modifiedText
      }
    },
    getCardLabel: (inputs: string[]) => {
      return `${inputs[0]} starting with ${inputs[1].toUpperCase()}`
    },
    inputs: [
      {
        label: 'Enter a topic:',
        placeholder: [
          'animals',
          'historical figures',
          'musical instruments',
          'things related to technology',
          'things that can fit in your pocket',
          'adjectives for describing food'
        ],
        maxLength: 50
      },
      {
        label: 'Words starting with:',
        placeholder: [],
        type: 'dropdown'
      }
    ],
    apiFunction: runAlliteration
  },
  {
    id: 'acronym',
    name: 'Acronym',
    slug: 'acronym',
    icon: 'acronym',
    textLabel: 'R.A.P. R.A.P. ACRONYM  R.A.P. R.A.P.',
    description: 'Create an acronym using the letters of a word.',
    color: colors.barbie,
    videoUrl: watchLupeUseItVideos.acronym,
    lottie: 'acronym_hero_animation_lottie',
    /**
     * ACRONYM ANIMATION
     * Add dots between the letters of the input.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = text?.length || 0
      let modifiedText = ''
      let complete = false

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          iteration++
          lastTime = now
          const arr = text.split('')

          const i = Math.abs(
            (iteration % (text.length * 2)) - Math.floor(text.length)
          )

          arr.unshift(...arr.splice(0, i).join('.'))
          modifiedText = arr.join('')
          if (loaded && i === 0) complete = true
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a word:',
        placeholder: ['metro', 'word', 'rap', 'flare', 'name', 'space'],
        maxLength: 15
      }
    ],
    apiFunction: runAcronym
  },
  {
    id: 'fuse',
    name: 'Fuse',
    slug: 'fuse',
    icon: 'fuse',
    textLabel: 'OO OO OO OO OO FUSE OO OO OO OO OO',
    description: 'Find intersections between two things.',
    color: colors.marigold,
    videoUrl: watchLupeUseItVideos.fuse,
    lottie: 'fuse_hero_animation_lottie',
    /**
     * FUSE ANIMATION
     * Shuffle the two words together until output is loaded, then unshuffle words with an ≈ in the middle.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = 0
      let modifiedText = ''
      let complete = false

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          if (loaded) iteration++
          lastTime = now
          const arr = text.split('')

          const i = iteration % text.length

          modifiedText = arr
            .concat(arr.splice(i).sort(() => Math.random() - 0.5))
            .join('')

          if (iteration === 0) modifiedText = modifiedText.replace(/[\s]/g, '')
          if (iteration === 1) modifiedText = text.replace(/[\s]/g, '')
          if (iteration > 1) modifiedText = text
          if (loaded && iteration >= 2) complete = true
        }

        if (complete) return false
        return modifiedText
      }
    },
    getCardLabel: (inputs: string[]) => {
      return `${inputs[0]} ≈ ${inputs[1]}`
    },
    inputs: [
      {
        label: 'Enter a thing:',
        placeholder: [
          'library',
          'coding',
          'mango',
          'romance',
          'parrot',
          'compliment'
        ],
        maxLength: 15
      },
      {
        label: 'Enter another one:',
        placeholder: [
          'graveyard',
          'poetry',
          'picture frame',
          'democracy',
          'octopus',
          'insult'
        ],
        maxLength: 15
      }
    ],
    apiFunction: runFuse
  },
  {
    id: 'scene',
    name: 'Scene',
    slug: 'scene',
    icon: 'scene',
    textLabel: '•_-_-_ •_-_-_  SCENE •_-_-_ •_-_-_',
    description: 'Generate sensory details about a scene.',
    color: colors.berry,
    videoUrl: watchLupeUseItVideos.scene,
    lottie: 'scene_hero_animation_lottie',
    /**
     * SCENE ANIMATION
     * Replace the letters of the input with a pattern of dots and dashes.
     */
    loadingAnimation: (text: string) => {
      const fps = 10 + Math.ceil(text.length / 10) // Adapt speed to text length
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = 0
      let modifiedText = ''
      let complete = false
      const pattern = '__…-…___…__……___…-…__…-…__…__…-…___…__…-…___…-…__…-…_…'
      const start = Math.random() * (pattern.length - text.length)
      const replacement = pattern.substring(start, start + text.length)

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          iteration++
          lastTime = now
          const replacement_arr = replacement.split('')

          const i = iteration % (text.length * 2)

          if (i > text.length) {
            const j = i - text.length
            modifiedText = `${text.substring(
              0,
              Math.max(0, j - 1)
            )}/${replacement_arr.splice(j).join('')}`
          } else {
            modifiedText = `${replacement_arr
              .slice(0, i)
              .join('')}/${text.substring(i + 1)}`
          }

          if (loaded && i === 0) {
            complete = true
          }
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a scene:',
        placeholder: [
          'checking in to a hotel',
          'reheated takeout',
          'a first date',
          'an auto repair shop',
          'a music festival',
          'going to the dentist'
        ],
        maxLength: 25
      }
    ],
    apiFunction: runScene
  },
  {
    id: 'unfold',
    name: 'Unfold',
    slug: 'unfold',
    icon: 'unfold',
    textLabel: '<-> <-> <-> < UNFOLD > <-> <-> <->',
    description: 'Slot a word into other words or phrases.',
    color: colors.water,
    videoUrl: watchLupeUseItVideos.unfold,
    lottie: 'unfold_hero_animation_lottie',
    /**
     * UNFOLD ANIMATION
     * Bounce from side to side using the _ character.
     */
    loadingAnimation: (text: string) => {
      const fps = 10
      const interval = 1000 / fps

      let now = interval
      let lastTime = 0
      let iteration = text.length || 0
      let modifiedText = ''
      let complete = false
      let underscores = '____'
      let countingDown = false

      return (dt: number, loaded: boolean) => {
        now += dt
        if (now - lastTime > interval) {
          iteration++
          lastTime = now

          const i = Math.abs(
            (iteration % (underscores.length * 2)) -
              Math.floor(underscores.length)
          )

          if (loaded && i === 0) countingDown = true
          if (countingDown) {
            if (underscores.length === 0) complete = true
            underscores = underscores.substring(0, underscores.length - 1)
            modifiedText = `${text}${underscores}`
          } else {
            const before = underscores.split('')
            const after = before.splice(i)
            modifiedText = `${before.join('')}${text}${after.join('')}`
          }
        }

        if (complete) return false
        return modifiedText
      }
    },
    inputs: [
      {
        label: 'Enter a word:',
        placeholder: ['control', 'star', 'roof', 'hand', 'pin', 'blue'],
        maxLength: 10,
        allowSpaces: false
      }
    ],
    apiFunction: runUnfold
  }
]

export interface IPromptDataItemRow {
  cols: {
    text: string
    title?: string
    background?: string
    style?: string
  }
}
export interface IPromptDataItemData {
  title: string
  rows: IPromptDataItemRow[]
}

export interface IPromptDataItem {
  description: ReactElement
  data: IPromptDataItemData[]
}

export interface IPromptData {
  simile: IPromptDataItem
  explode: IPromptDataItem
  unexpect: IPromptDataItem
  chain: IPromptDataItem
  pov: IPromptDataItem
  alliteration: IPromptDataItem
  acronym: IPromptDataItem
  fuse: IPromptDataItem
  scene: IPromptDataItem
  unfold: IPromptDataItem
}

const constructMacroExplainer = (taskDescription: string) => {
  return (
    <>
      <p>
        We can prime a large language model (LLM) to behave in a certain way
        using a <strong>prompt</strong>. A prompt is a string of text that
        contains examples of inputs and outputs for the desired task, and it
        helps the model recognize how it should respond to novel inputs.
        <br></br>
        <br></br>
        The table below shows how we primed the LLM to {taskDescription}. The
        format of this table is adapted from MakerSuite, which is a platform
        that makes it easy to build and experiment with LLM prompts. To learn
        more about MakerSuite, head{' '}
        <a
          href="https://developers.generativeai.google/products/makersuite"
          target="_blank"
          rel="noopener noreferrer"
        >
          here
        </a>
        .
      </p>
    </>
  )
}

export const promptData: IPromptData = {
  simile: {
    description: constructMacroExplainer(
      'generate a simile from a thing or concept'
    ),
    data: adaptPromptData(SIMILE_PROMPT_COMPONENTS)
  },
  explode: {
    description: constructMacroExplainer(
      'generate a similar-sounding phrase from a word or phrase'
    ),
    data: adaptPromptData(EXPLODE_PROMPT_COMPONENTS)
  },
  unexpect: {
    description: constructMacroExplainer(
      'generate an unexpected plot twist from a short description of a scene'
    ),
    data: adaptPromptData(UNEXPECT_PROMPT_COMPONENTS)
  },
  chain: {
    description: constructMacroExplainer(
      'generate a chain of semantically related words from a given starting word'
    ),
    data: adaptPromptData(CHAIN_PROMPT_COMPONENTS)
  },
  pov: {
    description: constructMacroExplainer(
      'generate different perspectives on a given topic'
    ),
    data: adaptPromptData(POV_PROMPT_COMPONENTS)
  },
  alliteration: {
    description: constructMacroExplainer(
      'generate words that begin with a given letter and also pertain to a given topic or domain'
    ),
    data: adaptPromptData(ALLITERATION_PROMPT_COMPONENTS)
  },
  acronym: {
    description: constructMacroExplainer(
      'generate an acronym using the letters of a given word'
    ),
    data: adaptPromptData(ACRONYM_PROMPT_COMPONENTS)
  },
  fuse: {
    description: constructMacroExplainer(
      'generate commonalities between two given topics'
    ),
    data: adaptPromptData(FUSE_PROMPT_COMPONENTS)
  },
  scene: {
    description: constructMacroExplainer(
      'generate sensory details about a given person, place, or thing'
    ),
    data: adaptPromptData(SCENE_PROMPT_COMPONENTS)
  },
  unfold: {
    description: constructMacroExplainer(
      'generate different ways a given word can appear in other existing words or phrases'
    ),
    data: adaptPromptData(UNFOLD_PROMPT_COMPONENTS)
  }
}

export interface IMacroOutput {
  id: string
  macro: string
  outputs: string[]
  inputs: string[]
  pins?: number[]
  randomness: number
}

export interface IPin {
  id: string
  index: number
  text: string
  macro: string
  input?: string
}

export const tippyOptions = {
  arrow: false,
  ignoreAttributes: true
}

export const ERROR_MESSAGE = 'Internal error. Please try again.'
export const NO_RESULTS_MESSAGE = 'No results generated. Please try again.'
