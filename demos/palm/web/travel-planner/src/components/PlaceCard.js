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

import React, { useRef, useState } from 'react';
import { Stack, Fab, Typography, Box, Slide, Skeleton } from '@mui/material';
import Div100vh from 'react-div-100vh';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Circle, CloseOutlined, MapOutlined } from '@mui/icons-material';
import { Pagination } from 'swiper';
import MapCard from './MapCard';

const playCardsStyles = {
  image_stl: {
    objectFit: "cover",
    objectPosition: "center center"
  },
  division1: {
    position: 'absolute',
    width: '100%',
    height: '30%',
    background: 'linear-gradient(180deg, rgba(0, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0.2) 31.73%, rgba(255, 255, 255, 0) 68.15%)',
    top: 0,
    left: 0,
  },
  division2: {
    position: 'absolute',
    background: 'linear-gradient(183.73deg, #000000 -21.07%, rgba(0, 0, 0, 0) 94.07%)',
    mixBlendMode: 'multiply',
    transform: 'rotate(-180deg)',
    width: '100%',
    height: '100%',
    top: 0,
    left: 0
  }
}

function PlaceCard(props) {
  const { name, geometry, photos, description, onClose } = props;

  const [currentIndex, setCurrentIndex] = useState(0)

  const [openMapCard, setOpenMapCard] = useState(false)

  const containerRef = useRef(null);

  const handleOnSlideChange = (e) => {
    setCurrentIndex(e.activeIndex)
  }

  const handleOpenMapView = (e) => {
    setOpenMapCard(true)
  }

  const handleOnCloseMapView = (e) => {
    setOpenMapCard(false)
  }

  return (
    <Div100vh ref={containerRef} style={{ position: 'absolute', top: 0, left: 0, width: "100%", overflowY: "hidden", background: "black" }}>
      <Stack width="100%" height="100%" sx={{ backgroundColor: "black" }}>
        <Stack
          width="100%"
          height="100%"
          position="relative"
          sx={{
            top: 0,
            left: 0,
            zIndex: 1000,
          }}
          justifyContent="space-between"

        >
          <Stack direction="row" justifyContent="space-between" alignItems="center" alignContent="center"
            sx={{ margin: "20px", zIndex: 1000, color: "white" }}>
            <Fab sx={{ background: 'rgba(0,0,0,0.4)' }} onClick={() => { onClose && onClose() }}>
              <CloseOutlined sx={{ color: "#FFFFFF" }} />
            </Fab>

            <Stack onClick={handleOpenMapView} direction="row" spacing={1}>
              <MapOutlined />
              <Typography fontFamily="Google Sans" fontWeight="300"> Map View </Typography>
            </Stack>
          </Stack>

          <Swiper
            style={{ position: "absolute", width: "100%", height: "100%", backgroundColor: "black" }}
            slidesPerView={1}
            modules={[Pagination]}
            onSlideChange={(e) => { handleOnSlideChange(e) }}
          >
            {
              photos && photos.length !== 0 ? photos.map((photo, index) => {
                return (
                  <SwiperSlide key={index}>
                    <Box
                      width="100%" height="100%"
                    >
                      <Box
                        width="100%"
                        height="100%"
                        position="absolute"
                      >
                        <img
                          height="100%"
                          width="100%"
                          src={photo}
                          style={playCardsStyles.image_stl}
                        />
                        <div
                          style={playCardsStyles.division1}
                        >

                        </div>
                        <div
                          style={playCardsStyles.division2}
                        >

                        </div>
                      </Box>
                      <Box
                        width="100%"
                        height="100%"
                        sx={{ position: 'absolute', marginTop: `calc(${window.innerHeight}px * 0.479)`, zIndex: 100 }}>
                        <Stack direction="column" color="white" spacing={1.5} p={3}>

                          <Typography variant='h4' fontFamily="Google Sans" fontSize="24px" fontWeight="300">{name && name}</Typography>
                          <Typography variant='h7' fontFamily="Google Sans" fontSize="14px">
                            {description && description}
                          </Typography>

                        </Stack>
                      </Box>
                    </Box>
                  </SwiperSlide>
                )
              }) :
                <SwiperSlide>
                  <Box
                    width="100%"
                    height="100%"
                  >
                    <Box
                      width="100%"
                      height="100%"
                      position="absolute"
                    >
                      <Skeleton
                        height="100%"
                        width="100%"
                      />
                    </Box>

                    <Box
                      width="100%"
                      height="100%"
                      sx={{ position: 'absolute', marginTop: `calc(${window.innerHeight}px * 0.4)`, zIndex: 100 }}>
                      <Stack direction="column" color="white" spacing={1.5} p={3}>

                        <Typography variant='h4' fontFamily="Google Sans">{name && name}</Typography>
                        <Typography variant='h7' fontFamily="Google Sans">
                          {description && description}
                        </Typography>

                      </Stack>
                    </Box>
                  </Box>
                </SwiperSlide>

            }
          </Swiper>
        </Stack>
      </Stack>
      <Stack
        width="100%"
        zIndex="1000"
        color="white"
        direction="column"
        position="absolute"
        bottom="5%"
      >
        <Stack alignItems="center" justifyContent="center" direction="row" spacing={1}>
          {
            photos &&
            photos.length > 1 &&
            photos.map((_, index) => {
              return (
                <Circle key={index} sx={{ width: "10px", height: "10px", color: index === currentIndex ? "white" : "rgba(255, 255, 255, 0.5)" }} />
              )
            })
          }
        </Stack>
      </Stack>

      <Slide direction="up" in={openMapCard} mountOnEnter unmountOnExit container={containerRef.current}>
        <Box width="100%" height="100%">
          <MapCard {...geometry} onClose={handleOnCloseMapView} />
        </Box>
      </Slide>
    </Div100vh>
  );
}

export { PlaceCard };
