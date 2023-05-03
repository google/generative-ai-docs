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

import React, { useState } from 'react';
import TypeIt from 'typeit-react';
import { v4 as uuidv4 } from 'uuid';

import ImageGenerator from 'src/components/ImageGenerator';

import LLMCaller from 'src/apis/llmCaller';
import LLMTextParser from 'src/utils/llmTextParser';

const llmCaller = new LLMCaller();
const llmParser = new LLMTextParser();

const creativeContext = {
  context:
    'I want you to act as a very creative chef who is an expert in foods and ingredients. In every user\'s message, you have to come up with an unimaginable recipe based on the user\'s message and any specific interests or preferences they may have. There can be more than one recipe based on the user\'s message. Answer in markdown format that includes only the following sections: "reaction", "name", "ingredients", "instructions", and "description". The "reaction" should be your humorous response to the user\'s message in a polite way. The "name" should be a possible name that plays with polite puns and does not offend anyone. The "ingredients" section should be a list of ingredients with their measurements. The "instructions" section should be a step-by-step guide on how to cook the recipe. The "description" should be the food description introduced by you as the funny chef. Do not include "variations" and "tips". Do not use the user\'s hated ingredients in the recipe. When the user asks for changing the ingredients, please make an update to the latest recipe',
};

const jsonReactionPrompt = 'Rewrite only the "Reaction" response into this JSON format: ```{"reaction":string}```';

const jsonSafeNamePrompt =
  'Rewrite only the "Name" response into this JSON format: ```{"recipes":[{"name":string},{...}]}```. Make sure that there are no words related to politics, religion, or race.';

const jsonRecipesPrompt =
  'You have to rewrite your response into this JSON format: ```{"recipes":[{"name":string,"course":string,"ingredients":[]string,"instructions":[]string,"description":string},...,{...}]}```';

const useChat = () => {
  const [coreMsg, updateCoreMsg] = useState([]);
  const [displayMsg, updateDisplayMsg] = useState([]);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);

  const _coreMsg = [...coreMsg];
  const _displayMsg = [...displayMsg];

  const handleErrorMessage = (msg = 'Internal server error!', _displayMsg) => {
    setSending(false);
    setLoading(false);
    setTyping(false);
    updateChunkDisplayMsg({ error: msg.toString() }, _displayMsg);
  };

  const onUserSendMessage = async (msg) => {
    const id = uuidv4();

    const greetingText = _coreMsg.length == 0 ? 'Hello!, the message is ' : '';
    const coreSendMsg = {
      author: '0',
      content: `${greetingText}"${msg}". Answer the recipe in the format I provided. Do not include any words related to politics, religion, or race.`,
    };
    const displaySendMsg = {
      id: id,
      type: 'sender',
      author: coreSendMsg.author,
      content: coreSendMsg.content,
      parsed: msg,
    };

    const _displayRecvMsg = {
      id: id,
      type: 'bot',
      author: '1',
      content: '',
      parsed: {},
    };

    _coreMsg.push(coreSendMsg);
    _displayMsg.push(displaySendMsg);
    updateDisplayMsg((prev) => prev.concat(displaySendMsg));
    _displayMsg.push(_displayRecvMsg);
    updateDisplayMsg((prev) => prev.concat(_displayRecvMsg));

    setSending(true);
    setLoading(true);

    try {
      const res = await llmCaller.sendPrompt(creativeContext, {}, _coreMsg, 0.75);
      const candidate = res.candidates[0];
      const coreRecvMsg = {
        author: candidate.author,
        content: candidate.content,
      };
      _displayMsg[_displayMsg.length - 1].content = candidate.content;
      updateDisplayMsg((prev) => [..._displayMsg]);
      updateCoreMsg((prev) => prev.concat(coreSendMsg));
      updateCoreMsg((prev) => prev.concat(coreRecvMsg));
      const preMsgs = [coreSendMsg, coreRecvMsg];
      onUserReceiveMessage(preMsgs, _displayMsg);
    } catch (error) {
      handleErrorMessage(error, _displayMsg);
      return;
    }
  };

  const updateChunkDisplayMsg = (res, _displayMsg) => {
    const latestIdx = _displayMsg.length - 1;
    _displayMsg[latestIdx].parsed = { ..._displayMsg[latestIdx].parsed, ...res };
    updateDisplayMsg([..._displayMsg]);
  };

  const filterReactionMarkDown = (preMsgs) => {
    const latestIdx = preMsgs.length - 1;
    const content = preMsgs[latestIdx].content;
    preMsgs[latestIdx].content = content.split('**Name')[0];
    return preMsgs;
  };

  const getJSONSafeName = async (preMsgsStr, _displayMsg) => {
    const nameMsg = {
      author: '0',
      content: jsonSafeNamePrompt,
    };
    const nameMsgs = [...JSON.parse(preMsgsStr), nameMsg];
    let nameResponse = '';
    try {
      const res = await llmCaller.sendPrompt({}, {}, nameMsgs, 0.1);
      nameResponse = res.candidates[0].content;
    } catch (error) {
      handleErrorMessage(error, _displayMsg);
      return;
    }
    try {
      let llmText2JSON = llmParser.llmText2JSON(nameResponse);
      if (llmText2JSON.recipes) {
        return llmText2JSON.recipes;
      } else {
        handleErrorMessage('Internal Server Error!', _displayMsg);
        return;
      }
    } catch (error) {
      handleErrorMessage('Internal Server Error!', _displayMsg);
      return;
    }
  };

  const getJSONReaction = async (preMsgsStr, _displayMsg) => {
    const preMsgs = filterReactionMarkDown(JSON.parse(preMsgsStr));
    const reactionMsg = {
      author: '0',
      content: jsonReactionPrompt,
    };
    const reactionMsgs = [...preMsgs, reactionMsg];
    let reactionResponse = '';
    try {
      const res = await llmCaller.sendPrompt({}, {}, reactionMsgs, 0.0);
      reactionResponse = res.candidates[0].content;
    } catch (error) {
      handleErrorMessage(error, _displayMsg);
      return;
    }
    try {
      let llmText2JSON = llmParser.llmText2JSON(reactionResponse);
      if (llmText2JSON.reaction) {
        setTyping(true);
        llmText2JSON.reaction = (
          <TypeIt
            options={{
              strings: [llmText2JSON.reaction, '</>', 'I recommend trying my recipe for'],
              speed: 50,
              afterComplete: (instance) => {
                updateChunkDisplayMsg({ typeItInstance: instance }, _displayMsg);
                setTyping(false);
              },
            }}
          />
        );
        return llmText2JSON.reaction ? llmText2JSON : {};
      } else {
        handleErrorMessage('Internal Server Error!', _displayMsg);
        return;
      }
    } catch (error) {
      handleErrorMessage('Internal Server Error!', _displayMsg);
      return;
    }
  };

  const getJSONRecipes = async (preMsgsStr) => {
    const preMsgs = JSON.parse(preMsgsStr);
    const recipeMsg = {
      author: '0',
      content: jsonRecipesPrompt,
    };
    const recipeMsgs = [...preMsgs, recipeMsg];
    let recipeResponse = '';
    let jsonNames = [];
    try {
      const _jsonNames = getJSONSafeName(preMsgsStr);
      const res = await llmCaller.sendPrompt({}, {}, recipeMsgs, 0.0);
      recipeResponse = res.candidates[0].content;
      jsonNames = await _jsonNames;
    } catch (error) {
      handleErrorMessage(error, _displayMsg);
      return;
    }
    try {
      let llmText2JSON = llmParser.llmText2JSON(recipeResponse);
      const minLength = Math.min(jsonNames.length, llmText2JSON.recipes.length);
      for (let i = 0; i < minLength; i++) {
        llmText2JSON.recipes[i].name = jsonNames[i].name;
      }
      if (Object.keys(llmText2JSON).length > 0) {
        return llmText2JSON;
      } else {
        handleErrorMessage('Internal Server Error!', _displayMsg);
        return;
      }
    } catch (error) {
      handleErrorMessage('Internal Server Error!', _displayMsg);
      return;
    }
  };

  const onUserReceiveMessage = async (preMsgs, _displayMsg) => {
    const preMsgsStr = JSON.stringify(preMsgs);
    getJSONReaction(preMsgsStr, _displayMsg).then((res) => {
      setLoading(false);
      updateChunkDisplayMsg(res, _displayMsg);
    });
    getJSONRecipes(preMsgsStr).then((res) => {
      try {
        res.recipes.forEach((item) => {
          if (item.image === undefined) {
            const rand1 = Math.random();
            const rand2 = Math.random();
            const rand3 = Math.random();
            item.getImage = (imageRef) => ImageGenerator(item.name, [rand1, rand2, rand3], imageRef);
          }
        });
        setSending(false);
        updateChunkDisplayMsg(res, _displayMsg);
      } catch (error) {
        handleErrorMessage('Internal Server Error!', _displayMsg);
        return;
      }
    });
  };
  return { displayMsg, onUserSendMessage, sending, loading, typing };
};

export default useChat;
