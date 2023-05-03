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

import React from 'react';

import fonts from 'src/data/fonts';
import palettes from 'src/data/palettes';
import patterns from 'src/assets/patterns';

import { getProperFontProperties } from 'src/utils/images';
import { getProperFontHeaderProperties } from 'src/utils/ingredientHeader';

export default function ImageGenerator(name, rands, imageRef) {
  const [rand1, rand2, rand3] = rands;
  const randPatternIdx = Math.floor(rand1 * patterns.length);
  const randPaletteIdx = Math.floor(rand2 * palettes.length);
  const randFontIdx = Math.floor(rand3 * fonts.length);
  const fontProperties = getProperFontProperties(name, fonts[randFontIdx], randPatternIdx);
  const fontHeaderProperties = getProperFontHeaderProperties(name, fonts[randFontIdx]);
  return [
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '88%',
        display: 'flex',
        justifyContent: 'center',
        maxWidth: '400px',
      }}
      ref={imageRef}
    >
      <span
        style={{
          position: 'absolute',
          textAlign: 'center',
          wordBreak: 'break-word',
          width: '75%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: palettes[randPaletteIdx][1],
          ...fontProperties,
        }}
      >
        {name}
      </span>
      {patterns[randPatternIdx](...palettes[randPaletteIdx])}
    </div>,
    fontHeaderProperties,
    palettes[randPaletteIdx],
  ];
}
