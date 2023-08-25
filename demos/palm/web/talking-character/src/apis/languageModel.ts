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

import {useContext, useEffect, useMemo} from 'react';

import {ConfigContext} from '../context/config';
import {LANGUAGE_MODEL_URL} from '../context/constants';

/**
 * Represents a message object with an author and content.
 * @interface
 * @property {string} author - The author of the message.
 * @property {string} content - The content of the message.
 */
export interface MessageProps {
  author: string;
  content: string;
}

/**
 * Represents an example object that defines the expected input and output for a
 * prompt.
 * @interface
 * @property {string} input.content - The content of the input for the example.
 * @property {string} output.content - The expected output content for the
 * example.
 */
export interface ExampleProps {
  input: {content: string};
  output: {content: string};
}

/**
 * Represents the properties for a prompt object, which contains a context,
 * examples, and a list of messages.
 * @interface
 * @property {string} [context] - The context for the prompt.
 * @property {ExampleProps[]} [examples] - An array of example objects that
 * define the expected input and output of the prompt.
 * @property {MessageProps[]} messages - An array of message objects that
 * represent the prompt's messages.
 */
export interface PromptProps {
  context?: string;
  examples?: ExampleProps[];
  messages: MessageProps[];
}

/**
 * Represents the response object returned by the sendPrompt function.
 * @interface
 * @property {MessageProps[]} messages - An array of message objects that
 * represent the prompt's messages.
 * @property {MessageProps[]} candidates - An array of message objects that
 * represent the potential responses to the prompt.
 */
export interface SendPromptResponse {
  candidates: MessageProps[];
  messages: MessageProps[];
}

type LanguageModel = {
  sendMessage: (message: string) => Promise<string>;
};

const useLanguageModel = ():
    LanguageModel => {
      const config = useContext(ConfigContext);

      let messages: MessageProps[] = [];

      const sendPrompt = async(prompt: PromptProps, temperature: number):
          Promise<SendPromptResponse> => {
            const payload = {
              prompt: {...prompt},
              temperature,
              candidate_count: 1,
            };

            const response = await fetch(LANGUAGE_MODEL_URL, {
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(payload),
              method: 'POST',
            });

            return response.json() as Promise<SendPromptResponse>;
          };

      const context = useMemo(() => `Your task is to acting as a character that has this personality: "${config.state
        .personality}". Your response must be based on your personality. You have this backstory: "${config.state.backStory}". Your knowledge base is: "${config.state
        .knowledgeBase}". The response should be one single sentence only.`, [config])

      const sendMessage = async(message: string): Promise<string> => {
        const content = `Please answer within 100 characters. {${
            message}}. The response must be based on the personality, backstory, and knowledge base that you have. The answer must be concise and short.`;

        const prompt: PromptProps = {
          context: context,
          messages: messages.concat([{author: '0', content}]),
        };

        const response = await sendPrompt(prompt, 0.25);

        messages = response.messages.concat(response.candidates[0]);

        return response.candidates[0].content;
      };

      return {
        sendMessage,
      }
    }

export default useLanguageModel;
