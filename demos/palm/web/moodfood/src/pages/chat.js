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

import React, { useEffect, useRef } from 'react';
import Lottie from 'lottie-react';
import WebFont from 'webfontloader';
import { Box, Stack } from '@mui/material';
import { useLocation } from 'react-router-dom';

import BotResponses from 'src/components/BotResponses';
import ChatInput from 'src/components/ChatInput';
import Dialogue from 'src/components/Dialogue';
import PrePromptsPanel from 'src/components/PrePromptsPanel';

import useChat from 'src/hooks/useChat';
import useImageResize from 'src/hooks/useImageResize';

import fonts from 'src/data/fonts';
import HeroData from 'src/data/hero';
import loadingPan from 'src/assets/lotties/loading_pan_01.json';

const Chat = () => {
  const { displayMsg, onUserSendMessage, sending, loading, typing } = useChat();
  const { imageRef, imageWidth } = useImageResize(displayMsg);

  const bottomRef = useRef(null);

  useEffect(() => {
    WebFont.load({
      custom: {
        families: fonts,
      },
    });
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [JSON.stringify(displayMsg)]);

  const location = useLocation();
  const predefinedId = location.state && location.state.id.toString();
  if (predefinedId && displayMsg.length === 0) {
    const heroCardObj = {};
    HeroData.forEach((val) => {
      heroCardObj[val.id] = val;
    });
    if (Object.keys(heroCardObj).includes(predefinedId)) {
      const heroText = heroCardObj[predefinedId].heroText;
      onUserSendMessage(heroText);
    }
    window.history.replaceState({}, document.title);
  }

  return (
    <div style={{ background: '#f8f7f7', minHeight: '100%' }}>
      <Stack width="100vw"></Stack>
      <Stack
        direction="column"
        justifyContent="space-between"
        sx={{
          paddingLeft: '24px',
          paddingRight: '24px',
        }}
        mb={14}
      >
        <Stack direction="column" justifyContent="space-between" width="100%" mt={5} spacing={2}>
          {displayMsg.length == 0 && <PrePromptsPanel onUserSendMessage={onUserSendMessage} />}
          {displayMsg.map((msg, index) => {
            return msg.author === '0' ? (
              <Stack key={index} width="100%" alignItems="flex-end">
                <Dialogue key={`diag-sender-${index}`} type={'sender'}>
                  {msg.parsed}
                </Dialogue>
              </Stack>
            ) : msg.parsed.error ? (
              <Stack key={index} width="100%" alignItems="flex-start">
                <Dialogue key={`diag-bot-${index}`} type={'bot'}>
                  {msg.parsed.error}
                </Dialogue>
              </Stack>
            ) : (
              msg.parsed.reaction && (
                <Stack key={index} width="100%" alignItems="flex-start">
                  <BotResponses
                    key={`res-bot-${index}`}
                    reaction={msg.parsed.reaction}
                    recipes={msg.parsed.recipes}
                    typeItInstance={msg.parsed.typeItInstance}
                    imageRef={imageRef}
                    imageWidth={imageWidth}
                    onUserSendMessage={onUserSendMessage}
                  />
                </Stack>
              )
            );
          })}
        </Stack>
        {loading && (
          <Stack
            direction="column"
            width="100%"
            height="100%"
            alignItems="center"
            justifyContent="center"
            sx={
              displayMsg.length <= 2
                ? {
                    position: 'fixed',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                  }
                : {}
            }
          >
            <Lottie animationData={loadingPan} loop={true} style={{ width: 'clamp(40px,18vmin,80px)' }} />
          </Stack>
        )}
      </Stack>
      <Box
        sx={{
          width: '100%',
          bottom: '1.5rem',
        }}
      >
        <Stack direction="row" justifyContent="center" width="100%">
          <ChatInput onSendMessage={onUserSendMessage} sending={sending} loading={loading} typing={typing} />
        </Stack>
      </Box>
      <div ref={bottomRef}></div>
    </div>
  );
};

export default Chat;
