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

export default class LLMTextParser {
  constructor(mode = 'json') {
    this.mode = mode;
    this.regex1 = /(?<=```json)[\s\S]*?(?=```)/gm;
    this.regex2 = /(?<=```)[\s\S]*?(?=```)/gm;
    this.regex3 = /(?<=`)[\s\S]*?(?=`)/gm;

  }

  filterJSONText(llmText, regex) {
    return llmText.match(regex);
  }

  llmText2JSON(llmText) {
    if (this.mode === 'json') {
      const regex = /\,(?!\s*?[\{\[\"\'\w])/g;
      const res = this.filterJSONText(llmText, this.regex1);
      if (res) {
        const json = res[0].replace(regex, '');
        // const stringyfyRes = JSON.stringify(res);
        try {
          return JSON.parse(json);

        } catch (error) {
          return null
        }
      }
      else {
        let res = this.filterJSONText(llmText, this.regex2);

        if (res === null) {
          res = this.filterJSONText(llmText, this.regex3);
        }
        const json = res[0].replace(regex, '');

        // const stringyfyRes = JSON.stringify(res);
        try {
          return JSON.parse(json);
        } catch (error) {
          return null
        }
      }
    }
  }
}
