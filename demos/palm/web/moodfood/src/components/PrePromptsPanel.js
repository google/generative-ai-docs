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

import React from 'react';
import { Stack } from '@mui/material';

import Dialogue from 'src/components/Dialogue';
import PromptCard from 'src/components/PromptCard';

import HeroData from 'src/data/hero';
import { ChefLogo } from 'src/assets/icons';

export default function PrePromptsPanel(props) {
  const { onUserSendMessage } = props;

  return (
    <Stack direction="column" gap={1.15}>
      <Dialogue type={'bot'}>
        {ChefLogo('none', '#646464')}
        <p style={{ marginTop: '0.5rem' }}>
          Hello, I can make anything you like
          <br />
          First, tell me about your day,
        </p>
        <p style={{ marginBottom: 0 }}>like:</p>
      </Dialogue>
      <Stack direction="column" gap={2.5}>
        {HeroData.map((val, index) => {
          if (val.id !== '0') {
            return (
              <PromptCard
                key={index}
                onClick={() => {
                  onUserSendMessage(val.heroText);
                }}
                color={val.colorTone}
              >
                {val.heroText}
              </PromptCard>
            );
          }
        })}
      </Stack>
    </Stack>
  );
}
