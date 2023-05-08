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

export default class LLMCaller {
  constructor() {
    this.apiKey = import.meta.env.VITE_GOOGLE_GENERATIVE_LANGUAGE_API_KEY
    this.baseUrl = 'https://autopush-generativelanguage.sandbox.googleapis.com';
  }

  async sendPrompt(context, examples, messages, temperature = 0) {
    return new Promise(async(resolve, reject)=> {

      const payload = {
        prompt: {...context, ...examples, messages: messages},
        temperature: temperature,
        candidate_count: 3
      }

      try {
        const response = await fetch(`${this.baseUrl}/v1beta1/models/chat-bison-001:generateMessage?key=${this.apiKey}`, {
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
          method: 'POST',
        });
        if(response.status === 200) {
          resolve((await response).json());
        } else {
          const res = await response.json();
          reject(res.error.message)
        }
      } catch (error) {
        reject(error)
      }

    })
  }
}
