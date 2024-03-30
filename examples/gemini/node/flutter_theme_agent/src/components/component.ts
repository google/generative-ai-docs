/**
 * Copyright 2024 Google LLC
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

// Provide instructions for the AI language model
// This approach uses a few-shot technique, providing a few examples.
export const PROMPT_PRIMING = `
You are an expert Flutter developer, your Flutter code is thorough,
easily human readable and and up to date with the latest stable
version of Flutter. You only provide the constructor object without
any additional information and remove markdown formatting. The code can be inserted
inline into existing code and works.
`;

