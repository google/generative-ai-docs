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

import {macros, IMacro, IMacroOutput, IPin} from '~/constants'

/* eslint-disable */
const intro = `..........................................................................
..........................................................................
..................*..................................................*....
..*....................................*..................................
.......     .................................   .....          ...........
......   |  ......·········.·····...······..  |  ··  ___----        ......
...   __/|_____    ___--__   ____  . ____  __/|_____  |       \\  /  ......
.....   ||        //     \\\\   \\\\  .   /      ||      _|_----   \\/     ....
......  ||  ...  ||       ||   \\\\    /  ...  ||  ...  |        /\\__-  ....
......  ||  ...  ||_______|| .  \\\\  /  ....  ||  ...  |  ...  /      .....
......  ||  ...  ||          ..  \\\\/  .....  ||  ...     ..  /  ..........
......  ||  ...  ||  ..........  /\\\\  .....  ||  ...........   ...........
......  ||  ...  ||  .........  /  \\\\  ....  ||  .....................*...
......  ||       ||   ..       /    \\\\  ...  ||        ...................
.......  \\=___/   \\=______/  _/_  . _\\\\_  ..  \\=____/  ...................
........        .                 .         .         ....................
...........................·..............................................
....*.........................................................*...........
...................................*......................................
...····································································...
...................GOOGLE LAB SESSION: LUPE FIASCO........................
..........................................................................
..........................................................................
..······································································..                                                
.. A=B   /-A-\\   ???   o-o   ^ ⦿ ⌄   A_A_   R.A.P.   OO   •_-_-   <-A-> ..
..........................................................................
..........................................................................
 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 
 .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . 
.    .    .    .    .    .    .    .    .    .    .    .    .    .    .    
  .      .      .      .      .      .      .      .      .      .      .
      .             .             .             .             .          .`

const allOutputs = `<>-<>-<>-<>-<>-<>-<>-<>-<> A L L  O U T P U T S <>-<>-<>-<>-<>-<>-<>-<>-<>`

const formatBullet = (text: string) => {
  return text
  // const regexp = new RegExp(`.{1,${allOutputs.length - 2}}`, 'g')
  // return `${text.match(regexp)?.join('\n  ')}`
}

/* eslint-disable */
const formatDownload = (outputs: IMacroOutput[], pins: IPin[]) => {
  let pinnedText = ''
  if (pins.length > 0) {
    let pinnedHeader = ''
    pinnedHeader = `P I N N E D (${pins.length}) `
    pinnedHeader = `${pinnedHeader}${'_'.repeat(
      allOutputs.length - pinnedHeader.length
    )}`
    pinnedText = `${pinnedHeader}\n\n\n${pins
      .map(pin => {
        const output = outputs.find(output => output.id === pin.id)
        if (!output) return ''

        const macro = macros.find(
          (macro: IMacro) => macro.slug === output.macro
        )
        if (!macro) return ''

        const inputs = macro.getCardLabel
          ? macro.getCardLabel(output.inputs)
          : output.inputs.join(' ')

        return `${macro.name}: ${inputs}\n${pin.text}`
      })
      .join('\n\n')}\n`
  }

  const outputsText = outputs.reduce((acc, output) => {
    const macro = macros.find((macro: IMacro) => macro.slug === output.macro)

    if (!macro) return acc

    const inputs = macro.getCardLabel
      ? macro.getCardLabel(output.inputs)
      : output.inputs.join(' ')

    const divider = '\n\n___________________________________\n\n'

    return `${acc}${
      macro.textLabel
    }\n\nINPUT:\n${inputs}\n\nOUTPUTS:\n• ${output.outputs
      .map(txt => formatBullet(txt))
      .join('\n\n• ')}${divider}`
  }, '')

  return `${intro}\n\n${pinnedText}\n\n${allOutputs}\n\n\n${outputsText}`
}

export default formatDownload
