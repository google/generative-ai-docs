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

function getProperFontHeaderProperties(name, fontFamily) {
  const numChars = name.length;
  const baseFontSize = 1.25;

  const fontSizeReduction = -numChars / 150 - 0.02 * Math.floor(numChars / 20);

  let fontProperties = {
    fontFamily: fontFamily,
    fontSize: baseFontSize + fontSizeReduction,
    lineHeight: '1em',
  };
  switch (fontFamily) {
    case 'Cinzel Decorative':
      fontProperties.fontSize = `${fontProperties.fontSize}em`;
      break;
    case 'Josefin Sans':
      fontProperties.fontSize = `${fontProperties.fontSize + 0.2}em`;
      break;
    case 'Milonga':
      fontProperties.fontSize = `${fontProperties.fontSize + 0.1}em`;
      break;
    case 'Sacramento':
      fontProperties.fontSize = `${fontProperties.fontSize + 0.3}em`;
      break;
    case 'Tulpen One':
      fontProperties.fontSize = `${fontProperties.fontSize + 0.75}em`;
      fontProperties.lineHeight = '0.9em';
      break;
    case 'Ultra':
      fontProperties.fontSize = `${fontProperties.fontSize - 0.1}em`;
      fontProperties.lineHeight = '1.1em';
      break;
    case 'Urbanist':
      fontProperties.fontSize = `${fontProperties.fontSize + 0.1}em`;
      break;
    case 'Wire One':
      fontProperties.fontSize = `${fontProperties.fontSize + 0.5}em`;
      fontProperties.lineHeight = '0.9em';
      break;
    default:
      fontProperties.fontSize = `${fontProperties.fontSize}em`;
      break;
  }
  return fontProperties;
}

export { getProperFontHeaderProperties };
