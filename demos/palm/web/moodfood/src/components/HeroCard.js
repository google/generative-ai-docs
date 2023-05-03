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
import { Button, Card, CardContent } from '@mui/material';

import { ChefLogo } from 'src/assets/icons';

const StyledCard = styled.div`
  height: 68vh;
  width: 77%;
  min-height: 420px;
  min-width: 250px;
  max-width: 480px;
  margin: auto;
  text-align: center;
  background: none;
  border: 1px dashed #938c82;
  borderradius: 0px;
  position: relative;
  padding: 0.25rem;
`;

export default function HeroCard(props) {
  const { id, heroText, actionButtonText, colorTone } = props;
  return (
    <StyledCard>
      <Card
        sx={{
          background: '#EBE9E7',
          boxShadow: 'none',
          color: colorTone,
          position: 'relative',
          height: '100%',
        }}
      >
        <CardContent sx={{ padding: 'clamp(1rem, calc(20vmin - 1vh), 4rem) clamp(0.5rem, calc(8vmin - 1vw), 2rem)' }}>
          <p
            style={{
              fontStyle: 'normal',
              fontWeight: 400,
              fontSize: '1.5rem',
              lineHeight: '2rem',
            }}
          >
            “{heroText}”
          </p>
          <span style={{ position: 'absolute', left: '50%', transform: 'translate(-50%, 0)', bottom: '5.25rem' }}>
            {ChefLogo('none', colorTone)}
          </span>
          <Link
            to={{
              pathname: '/chat',
            }}
            state={{ id: id }}
          >
            <Button
              size="medium"
              variant="contained"
              sx={{
                paddingX: '2rem',
                fontFamily: 'Google Sans',
                fontStyle: 'normal',
                fontWeight: 400,
                color: '#EBE9E7',
                background: colorTone,
                textTransform: 'none',
                position: 'absolute',
                left: '50%',
                bottom: '2.5rem',
                transform: 'translate(-50%, 0)',
                whiteSpace: 'nowrap',
              }}
            >
              {actionButtonText}
            </Button>
          </Link>
        </CardContent>
      </Card>
    </StyledCard>
  );
}
