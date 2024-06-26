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

import Simile from './icon-set/simile'
import Unfold from './icon-set/unfold'
import Explode from './icon-set/explode'
import Unexpect from './icon-set/unexpect'
import Chain from './icon-set/chain'
import POV from './icon-set/pov'
import Alliteration from './icon-set/alliteration'
import Acronym from './icon-set/acronym'
import Fuse from './icon-set/fuse'
import Scene from './icon-set/scene'
import All from './icon-set/all'
import Mic from './icon-set/mic'
import Save from './icon-set/save'
import Saved from './icon-set/saved'
import Download from './icon-set/download'
import Delete from './icon-set/delete'
import Copy from './icon-set/copy'
import Arrow from './icon-set/arrow'
import styles from './icon.module.scss'
import MicListening from './icon-set/micListening'
import MicWaiting from './icon-set/micWaiting'
import Dropdown from './icon-set/dropdown'
import Logo from './icon-set/logo'
import LogoLight from './icon-set/logoLight'
import Info from './icon-set/info'
import Close from './icon-set/close'
import ArrowDown from './icon-set/arrowDown'
import SwiperArrow from './icon-set/swiperArrow'
import Pin from './icon-set/pin'
import Unpin from './icon-set/unpin'
import PinSolid from './icon-set/pinSolid'
import CollapseArrow from './icon-set/collapseArrow'
import Play from './icon-set/play'
import Refresh from './icon-set/refresh'
import Drag from './icon-set/drag'
import Back from './icon-set/back'
import External from './icon-set/external'

import c from 'classnames'

export interface IIcon {
  name: keyof typeof Icons
  className?: string
}

export const Icons = {
  simile: Simile,
  unfold: Unfold,
  explode: Explode,
  unexpect: Unexpect,
  chain: Chain,
  pov: POV,
  alliteration: Alliteration,
  acronym: Acronym,
  fuse: Fuse,
  scene: Scene,
  all: All,
  mic: Mic,
  save: Save,
  saved: Saved,
  download: Download,
  delete: Delete,
  copy: Copy,
  micListening: MicListening,
  micWaiting: MicWaiting,
  arrow: Arrow,
  dropdown: Dropdown,
  logo: Logo,
  logoLight: LogoLight,
  info: Info,
  close: Close,
  arrowDown: ArrowDown,
  swiperArrow: SwiperArrow,
  pin: Pin,
  unpin: Unpin,
  pinSolid: PinSolid,
  collapseArrow: CollapseArrow,
  play: Play,
  refresh: Refresh,
  drag: Drag,
  back: Back,
  external: External
}

const Icon = ({name, className}: IIcon) => {
  const Component: any = Icons[name]

  if (Component) {
    return <Component className={c(styles.icon, className)} />
  }

  return null
}

export default Icon
