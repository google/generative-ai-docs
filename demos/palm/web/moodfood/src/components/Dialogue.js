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
import { Paper } from '@mui/material';

const dialogueStyle = {
  sender: {
    background: 'transparent',
    borderRadius: '20px 0px 20px 20px',
    textAlign: 'right',
    padding: '10px 16px',
    gap: '10px',
    width: '85%',
    color: '#646464',
    margin: '0 0 0.5rem 0',
  },
  bot: {
    background: 'transparent',
    color: '#646464',
    padding: '0 1rem',
  },
};

export default function (props) {
  const { type, children } = props;
  return (
    <Paper elevation={0} sx={dialogueStyle[type]}>
      {children}
    </Paper>
  );
}
