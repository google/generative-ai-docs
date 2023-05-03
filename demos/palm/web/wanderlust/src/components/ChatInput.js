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

import * as React from 'react';
import Paper from '@mui/material/Paper';
import InputBase from '@mui/material/InputBase';
import IconButton from '@mui/material/IconButton';
import SendIcon from '@mui/icons-material/Send';
import { Stack } from '@mui/material';

export default function ({ onSendMessage, sending, inputRef }) {
  // const ref = inputRef = React.useRef(null);

  const sendMessage = () => {
    const msg = inputRef.current.value;
    inputRef.current.value = '';

    if(msg === '' || sending) return;
    onSendMessage(msg);
  }

  return (

    <Stack
      direction="row"
      justifyContent="center"
      sx={{
        background: '#FCF6F2',
        width: '100%',
        bottom: '0px',
        paddingTop: '5px',
        paddingBottom: '25px'
      }}

    >
      <Paper
        elevation={0}
        component="form"
        sx={{
          p: '2px 4px',
          display: 'flex',
          alignItems: 'center',
          width: 'calc(100% - 48px)',
          minHeight: '48px',
          maxWidth: 800,
          borderRadius: '20px',
          boxShadow: `0px 4px 4px rgba(0, 0, 0, 0.1)`
        }}
      >
        <InputBase
          disabled={sending}
          inputRef={inputRef}
          sx={{ ml: 1, flex: 1, fontFamily: "Google Sans", fontWeight: "300", fontSize: "14px"}}
          placeholder="Type your destination... "
          inputProps={{ 'aria-label': 'Type your destination...' }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              sendMessage();
            }
          }}
        />
        <IconButton
          disabled={sending}
          onClick={sendMessage}
          color="primary"
          sx={{ p: '10px' }}
          aria-label="send"
        >
          <SendIcon sx={{ color: '#DADCE0' }} />
        </IconButton>
      </Paper>
    </Stack>
  );
}
