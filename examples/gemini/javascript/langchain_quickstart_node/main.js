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

import { readFile } from 'node:fs/promises';
import { ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings } from '@langchain/google-genai';
import { HumanMessage } from '@langchain/core/messages';

/**
 * Creates a Gemini Pro text-only chat model, invokes the model with a single
 * input, and logs the result.
 */
async function invokeGeminiPro() {
  const model = new ChatGoogleGenerativeAI({
    modelName: 'gemini-pro',
    maxOutputTokens: 1024,
  });

  const result = await model.invoke([
    [
      'human',
      'What is the meaning of life?',
    ],
  ]);

  console.log(result);
}

/**
 * Creates a Gemini Pro Vision multimodal chat model, invokes the model with an
 * input containing text and image data, and logs the result.
 */
async function invokeGeminiProVision() {
  const model = new ChatGoogleGenerativeAI({
    modelName: 'gemini-pro-vision',
    maxOutputTokens: 1024,
  });

  const image = await readFile('./image.jpg', { encoding: 'base64' });
  const input = [
    new HumanMessage({
      content: [
        {
          type: 'text',
          text: 'Write a short, engaging blog post based on this picture. ' +
              'It should include a description of the meal in the photo ' +
              'and talk about my journey meal prepping.',
        },
        {
          type: 'image_url',
          image_url: `data:image/png;base64,${image}`,
        },
      ],
    }),
  ];
  const result = await model.invoke(input);
  console.log(result);
}

/**
 * Creates an embedding model, embeds text data, and logs the result.
 */
async function embedText() {
  const model = new GoogleGenerativeAIEmbeddings({
    modelName: 'embedding-001',
  });
  const text = 'The quick brown fox jumps over the lazy dog.';
  const result = await model.embedQuery(text);
  console.log(result, result.length)
}

/**
 * Runs the example functions. The functions are asynchronous, so we don't know
 * the order in which they'll return.
 */
async function run() {
  invokeGeminiPro();
  invokeGeminiProVision();
  embedText();
}

run();
