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

import React, { useEffect, useState } from "react";
import { Box, Paper, Skeleton, Stack, Typography } from "@mui/material";

export default function (props) {
  const [registeredEvent, setRegisteredEvent] = useState(false)
  const { day_number, trip_message, places = [], activities, formattedActivities, placeIds, onClick, onClickPlace } = props;

  const photos = places && places.length > 0 ? places[0].photos : []

  useEffect(() => {
    if (typeof (placeIds) === 'undefined') return;

    if (placeIds.length > 0 && !registeredEvent) {
      for (let i = 0; i < placeIds.length; i++) {
        try {
          const placeSelection = document.getElementById(placeIds[i])
          placeSelection.addEventListener('click', (e) => {
            onClickPlace && onClickPlace(placeSelection.innerHTML, places[i])
          })
        } catch (error) {
          // console.error(error)
        }

      }
    }
    setRegisteredEvent(true)
  });

  return (
    <Stack direction="row" spacing={2} mb={1}>
      <Box
        sx={{
          position: 'relative',
          cursor: 'pointer'
        }}
        mt={0.75}
        onClick={onClick}
      >
        {
          photos ? (
            photos.length === 0 ?
              <Skeleton
                variant="rectangular"
                animation="wave"
                width="120px"
                height="120px"
                sx={{ borderRadius: "12px", bgcolor: "gray.900", filter: 'drop-shadow(0px 4px 14px rgba(77, 73, 69, 0.25))' }}>
              </Skeleton>
              :
              <img
                src={photos[0]}
                alt={""}
                style={{
                  borderRadius: "12px",
                  objectFit: "cover",
                  objectPosition: "center center",
                  filter: 'drop-shadow(0px 4px 14px rgba(77, 73, 69, 0.25))'

                }}
                width="120px"
                height="120px"
                onClick={() => {
                  // window.open(map_url, '_blank');
                }}
              />
          )
            :
            (
              <Skeleton
                variant="rectangular"
                animation="wave"
                width="120px"
                height="120px"
                sx={{ borderRadius: "12px", bgcolor: "gray.900", filter: 'drop-shadow(0px 4px 14px rgba(77, 73, 69, 0.25))' }}>
              </Skeleton>
            )
        }

        <Paper
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            padding: "4px 5px",
            background: 'rgba(255, 255, 255, 0.5)',
            borderRadius: '8.94737px',
            marginLeft: '7.8px',
            marginTop: '4px'
          }}
          elevation={0}
        >
          <Typography fontFamily="Google Sans" fontSize="10px" sx={{ color: "#614646" }}>
            🏖️ Day {day_number && day_number}
          </Typography>
        </Paper>
      </Box>
      <Box
        width="67%"
      >
        <span
          style={{
            color: '#614646',
            fontSize: '14px'
          }}
        >
          {
            !formattedActivities ?

              <>
                <Skeleton />
                <Skeleton animation="wave" />
                <Skeleton animation={false} />
                <Skeleton animation="wave" />
                <Skeleton animation={false} />
              </>

              :

              <ul
                style={{
                  overflowY: "hidden",
                  textOverflow: "ellipsis",
                  display: "-webkit-box",
                  WebkitLineClamp: 5,
                  WebkitBoxOrient: "vertical",
                  paddingLeft: '18px',
                  marginTop: '2px',
                  marginBottom: '2px'

                }}
              >
                {
                  formattedActivities &&
                  formattedActivities.map((activity, i) => <li key={i} dangerouslySetInnerHTML={{ __html: activity }}></li>)
                }
              </ul>
          }

          <div
            style={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              display: "-webkit-box",
              WebkitLineClamp: 5,
              WebkitBoxOrient: "vertical"
            }}
            dangerouslySetInnerHTML={{ __html: trip_message }}></div>
        </span>
      </Box>
    </Stack>
  )
}
