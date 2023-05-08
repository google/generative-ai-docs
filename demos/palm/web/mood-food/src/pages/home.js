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

import React, { useState, useEffect } from 'react';
import WebFont from 'webfontloader';
import { Pagination } from 'swiper';
import { Stack } from '@mui/material';
import { Circle } from '@mui/icons-material';
import { Swiper, SwiperSlide } from 'swiper/react';

import HeroCard from 'src/components/HeroCard';
import OnBoardingCard from 'src/components/OnBoardingCard';

import fonts from '../data/fonts';
import HeroData from '../data/hero';

const Home = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleOnSlideChange = (e) => {
    setCurrentIndex(e.activeIndex);
  };

  useEffect(() => {
    WebFont.load({
      custom: {
        families: fonts,
      },
    });
  }, []);

  return (
    <section
      style={{
        width: '100%',
        minHeight: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: '#F8F7F7',
        color: '#393939',
      }}
    >
      <Stack gap={6} direction="column" alignItems="center" mt={6}>
        <Swiper
          slidesPerView={1}
          modules={[Pagination]}
          onSlideChange={(e) => {
            handleOnSlideChange(e);
          }}
          style={{ width: '100vw', maxWidth: '1024px' }}
        >
          {HeroData.map((val, index) => {
            return (
              <SwiperSlide key={index}>
                {val.id === '0' ? <OnBoardingCard {...val} /> : <HeroCard {...val} />}
              </SwiperSlide>
            );
          })}
        </Swiper>
        <div>
          {HeroData.map((_, index) => {
            return (
              <Circle
                key={index}
                sx={{
                  width: '10px',
                  height: '10px',
                  margin: '0 2px',
                  color: index === currentIndex ? '#5E5E5E' : '#B5B5B5',
                }}
              />
            );
          })}
        </div>
      </Stack>
    </section>
  );
};

export default Home;
