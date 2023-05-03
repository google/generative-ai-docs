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

import { v4 as uuidv4 } from 'uuid';

export function markPlaces(strings, targets) {
  let ids = [];
  for (let i = 0; i < strings.length; i++) {
    let markedString = strings[i];
    for (let j = 0; j < targets.length; j++) {
      const name = targets[j]['name'];
      const country = targets[j]['country'];

      if (markedString.includes(`[${name}|${country}]`)) {
        const id = uuidv4();
        ids.push(id);
        markedString = markedString.replace(`[${name}|${country}]`, `<b id="${id}">${name}</b>`);
      }
    }
    strings[i] = markedString;
  }

  return {
    messages: strings, ids: ids
  }
}
