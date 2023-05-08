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

import React, { useRef } from 'react';
import Paper from '@mui/material/Paper';
import InputBase from '@mui/material/InputBase';

export default function ({ onSendMessage, sending, loading, typing }) {
  const inputRef = useRef();

  return (
    <Paper
      elevation={0}
      component="form"
      sx={{
        pt: 2,
        pb: 4,
        display: 'flex',
        alignItems: 'center',
        width: '100%',
        maxWidth: 1024,
        position: 'fixed',
        bottom: '0px',
        borderTop: '0.5px solid #858585',
        borderRadius: '0px',
        backgroundColor: sending || loading || typing ? '#ebebeb' : '#fff',
      }}
      onSubmit={(e) => {
        e.preventDefault();
        const msg = inputRef.current.value;
        inputRef.current.value = '';
        onSendMessage(msg);
      }}
    >
      <InputBase
        inputRef={inputRef}
        disabled={sending || loading || typing}
        sx={{ ml: 3, flex: 1 }}
        placeholder={sending || loading || typing ? 'loading...' : 'type something...'}
        inputProps={{ 'aria-label': 'type something...' }}
      />
    </Paper>
  );
}
