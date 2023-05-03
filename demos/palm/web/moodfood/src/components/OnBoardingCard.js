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
import styled from '@emotion/styled';
import { Link } from 'react-router-dom';
import { Button, Card, CardActions, CardContent, Stack } from '@mui/material';

import { Decorator, MoodFoodLogo } from 'src/assets/icons';

const StyledCard = styled.div`
  height: 66vh;
  width: 72%;
  min-height: 420px;
  min-width: 240px;
  max-width: 480px;
  margin: auto;
  text-align: center;
  background: #c1c5cd;
  -webkit-clip-path: polygon(6.5% 0, 70% 0%, 100% 0, 100% 95.5%, 93.5% 100%, 0 100%, 0% 70%, 0 4.5%);
  clip-path: polygon(6.5% 0, 70% 0%, 100% 0, 100% 95.5%, 93.5% 100%, 0 100%, 0% 70%, 0 4.5%);
  position: relative;
  padding: 0.75rem;
`;

export default function OnBoardingCard(props) {
  const { heroText, actionButtonText, colorTone } = props;
  return (
    <StyledCard>
      <Card
        sx={{
          background: 'transparent',
          border: '1px solid #938C82',
          borderRadius: '0px',
          boxShadow: 'none',
          color: colorTone,
          position: 'relative',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <CardContent sx={{ mb: 'clamp(45px,9vh,100px)' }}>
          <Stack direction="column" alignItems="center" gap="clamp(10px,2vh,50px)">
            {MoodFoodLogo('#DADFE8', colorTone)}
            <span
              style={{
                fontStyle: 'normal',
                fontWeight: 400,
                fontSize: 'clamp(0.9rem, calc(1.25vmin + 1vh + 1vw), 1rem)',
                lineHeight: 'clamp(1.5rem, calc(1.25vmin + 1.5vh + 4vw), 2rem)',
              }}
            >
              {heroText}
            </span>
            {Decorator('none', colorTone)}
          </Stack>
        </CardContent>
        <CardActions
          sx={{
            position: 'absolute',
            left: '50%',
            bottom: 'clamp(1rem, 1.5vmin + 2vh, 2.5rem)',
            transform: 'translate(-50%, 0)',
          }}
        >
          <Link
            to={{
              pathname: '/chat',
            }}
          >
            <Button
              size="medium"
              variant="contained"
              sx={{
                paddingX: '2rem',
                fontFamily: 'Google Sans',
                fontStyle: 'normal',
                fontWeight: 400,
                color: '#C0C5CF',
                background: colorTone,
                textTransform: 'none',
                whiteSpace: 'nowrap',
              }}
            >
              {actionButtonText}
            </Button>
          </Link>
        </CardActions>
      </Card>
    </StyledCard>
  );
}
