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

export async function sendRequestToGoogleCloudApi(
    // tslint:disable-next-line:no-any Need to be able to serialize anything.
    endpoint: string, request: any, apikey: string, method = 'POST') {
  const endpointWithParam = endpoint + '?key=' + apikey;
  const response = await fetch(endpointWithParam, {
    method,
    mode: 'cors',
    cache: 'no-cache',
    body: method === 'POST' ? JSON.stringify(request) : undefined,
  });

  const text = await response.text();
  // tslint:disable:no-any no-unnecessary-type-assertion
  return JSON.parse(text) as any;
  // tslint:enable:no-any no-unnecessary-type-assertion
}
