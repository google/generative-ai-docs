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
import { AppBar, Stack, Container, Typography } from '@mui/material';
import useAuth from 'src/hooks/useAuth';
import Avatar from './Avatar';

const styles = {
  appBar: {
    minHeight: 80,
    backgroundColor: 'white',
    position: 'relative',
    flexDirection: 'row',
    justifyContent: 'start',
    alignItems: 'center',
    boxShadow: '1'
  },
  typography: {
    fontSize: 21,
    fontWeight: 700,
    fontFamily: 'Space Grotesk',
    margin: 0,
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    color: 'black',
  },
};

export default function Header() {
  const { isAuthenticated } = useAuth();

  return (
    <AppBar position="static" sx={styles.appBar}>
      <Container
        sx={{
          display: 'flex',
          flexDirection: 'row',
          height: '100%',
          justifyContent: 'space-between',

        }}
        maxWidth="xxl"
      >
        <Stack></Stack>
        <Typography fontFamily="Google Sans" sx={styles.typography}>Travel Genie</Typography>
        <Stack>{!isAuthenticated && <Avatar />}</Stack>
      </Container>
    </AppBar>
  );
}
