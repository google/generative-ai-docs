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

import React, { useEffect, useRef, useState } from "react";
import { Stack, Box, Typography, Skeleton } from "@mui/material";
import { Swiper, SwiperSlide } from 'swiper/react';

import { Pagination } from "swiper";
import { ArrowBack, Circle } from "@mui/icons-material";
import Div100vh from "react-div-100vh";

export default React.forwardRef((props, ref) => {
  const placeViewDescriptionRef = useRef(null);

  const [registeredEvent, setRegisteredEvent] = useState(false)

  const { day_number, places, placeIds, formattedActivities, onClose } = props;

  const [currentIndex, setCurrentIndex] = useState(0)

  const handleOnSlideChange = (e) => {
    setCurrentIndex(e.activeIndex)
  }

  useEffect(() => {
    if (typeof (placeIds) === 'undefined') return;

    if (placeIds.length > 0 && !registeredEvent) {
      const placeViewDescriptionElement = placeViewDescriptionRef.current;
      const placeElementList = placeViewDescriptionElement.getElementsByTagName("b");
      for (let i = 0; i < placeElementList.length; i++) {
        try {
          placeElementList[i].addEventListener('click', (e) => {
            props.onClickPlace && props.onClickPlace(placeElementList[i].innerHTML, places[i])
          })
        } catch (e) {
          // console.error(e);
        }
      }
    }
    setRegisteredEvent(true)
  });

  return (
    <Div100vh ref={ref} style={{ position: 'absolute', top: 0, left: 0, width: "100%", zIndex: 200, background: "#FCF6F2" }}>
      <Stack direction="column">
        <Stack position="relative" width="100%" style={{ height: `calc(0.5 * ${window.innerHeight}px)` }}>
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
            <Box sx={{ margin: "20px", zIndex: 1000, color: "white" }}>
              <Box onClick={() => { onClose && onClose() }}>
                <ArrowBack />
              </Box>
            </Box>

            <Swiper
              style={{ position: "absolute", width: "100%", height: "100%" }}
              slidesPerView={1}
              modules={[Pagination]}
              onSlideChange={(e) => { handleOnSlideChange(e) }}
            >
              {places && places.map((placeData, index) => {
                const photos = typeof (placeData.photos) !== "undefined" ? placeData.photos : [];

                return (
                  <SwiperSlide key={index}>
                    <Box width="100%" height="100%">
                      {!photos && photos.length === 0 ?
                        <Skeleton variant="rectangular"
                          width="100%"
                          height="100%"
                          animation="wave"
                          sx={{
                            bgcolor: "gray.900"
                          }}
                        >
                        </Skeleton>
                        :
                        <img
                          style={{
                            objectFit: "cover",
                            objectPosition: "center center"

                          }}
                          width="100%"
                          height="100%"
                          src={photos[0]} />
                      }
                      <div
                        style={{
                          position: 'absolute',
                          background: 'linear-gradient(183.73deg, #000000 -21.07%, rgba(0, 0, 0, 0) 94.07%)',
                          mixBlendMode: 'multiply',
                          opacity: '0.4',
                          width: '100%',
                          height: '100%',
                          transform: 'rotate(-180deg)',
                          top: 0,
                          left: 0
                        }}
                      >

                      </div>
                    </Box>
                  </SwiperSlide>
                )
              })}
            </Swiper>

            <Stack
              zIndex="1000"
              color="white"
              m="20px"
              direction="column"
            >
              <Stack direction="row" spacing={1}>
                <Typography fontFamily="Google Sans">
                  🏖️  Day {day_number}
                </Typography>

                <Typography fontFamily="Google Sans">
                  📍 {places[currentIndex].country}
                </Typography>
              </Stack>
              <Stack direction="row">
                <Box width="80%">
                  <Typography variant="h5" fontFamily="Google Sans" fontWeight="300">
                    {places[currentIndex].name}
                  </Typography>

                </Box>

                <Stack alignItems="flex-end" justifyContent="flex-end" width="20%" direction="row" spacing="4px" mb="-4px">
                  {
                    places.length > 1 &&
                    places.map((_, index) => {
                      return (
                        <Circle key={index} sx={{ width: "10px", height: "10px", color: index === currentIndex ? "white" : "rgba(255, 255, 255, 0.5)" }} />
                      )
                    })
                  }
                </Stack>
              </Stack>
            </Stack>
          </Stack>

        </Stack>

        <Box
          padding="20px"
        >
          <div
            ref={placeViewDescriptionRef}
            style={{ fontFamily: "Google Sans", fontSize: "14px", color: "#614646" }}
          >
            <ul style={{ paddingLeft: '12px', fontSize: "16px" }}>
              {
                formattedActivities &&
                formattedActivities.map((activity, i) => <li key={i} dangerouslySetInnerHTML={{ __html: activity }}></li>)
              }
            </ul>
          </div>
        </Box>
      </Stack>
    </Div100vh>
  )
})
