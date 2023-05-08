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

import React, { useState } from "react";
import Div100vh from "react-div-100vh";
import { Box, Fab, Link, Paper, Stack, Typography } from "@mui/material";


const OnBoarding = () => {

  return (
    <Paper
      elevation={0}
      sx={{
        width: '100%',
        height: '100%'
      }}
    >
      <Stack
        sx={{
          background: 'url(onboarding.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          width: '100%',
          height: '100%'
        }}
      >
        <Stack position="absolute" bottom="40%" alignItems="center" sx={{ zIndex: 1000 }} justifyContent="center" width="100%" direction="row" spacing={1}>
          <Link href="/chat" sx={{ textDecoration: 'none' }}>
            <Fab

              sx={{
                fontFamily: "Google Sans",
                backgroundColor: 'rgba(255, 255, 255, 0.8)',
                color: '#9E4F36',
                boxShadow: '0px 2px 3px rgba(255, 255, 255, 0.25)',
                textTransform: 'none'
              }}
              variant="extended"
            >
              Let’s go!
            </Fab>
          </Link>
        </Stack>
      </Stack>
    </Paper>
  )
}
export default function () {
  const [currentIndex, setCurrentIndex] = useState(0)

  const handleOnSlideChange = (e) => {
    setCurrentIndex(e.activeIndex)
  }

  return (
    <Div100vh>
      <Stack position="relative" width="100%" height="100%">
        <Stack
          position="absolute"
          width="100%"
          height="100%"
          sx={{
            top: 0,
            left: 0,
            zIndex: 1000,
          }}
          justifyContent="space-between"
        >
          <Stack
            textAlign="center"
            position="absolute"
            direction="column"
            alignItems="center"
            color="white"
            zIndex="1000"
            paddingLeft="30px"
            paddingRight="30px"
            spacing={4}
            sx={{
              transform: 'translate(-50%, 0)',
              top: '30%',
              left: '50%'
            }}
          >
            <Typography fontFamily="Google Sans" fontWeight="bold" variant="h3">Wanderlust</Typography>
            <Typography fontFamily="Google Sans" variant="h7">Get your travel itinerary as simple as talking to a friend</Typography>
          </Stack>

          <Box
            style={{ position: "absolute", width: '100%', height: '100%' }}
          >
            <OnBoarding />
          </Box>
        </Stack>
      </Stack>
    </Div100vh>
  )
}
