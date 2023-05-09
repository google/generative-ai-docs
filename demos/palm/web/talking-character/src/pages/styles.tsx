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

import React, {useEffect, useState} from 'react';

export const COLORS = {
      primary: '#669DF6',
      grey: '#99A2AF',
      bgcolor: '#F2F5F8',
    };

const useStyle = 
  () => {
    const [boxWidth, setBoxWidth] = useState('40vh');
   
    useEffect(() => {
      const calculateWidth = () => {
        const vh = window.innerHeight * 0.01;
        const vw = window.innerWidth * 0.01;

        if (40 * vh > 100 * vw) {
          setBoxWidth('80vw');
        } else {
          setBoxWidth('40vh');
        }
      };

      window.addEventListener('resize', calculateWidth);
      calculateWidth();

      return () => window.removeEventListener('resize', calculateWidth);
    }, [boxWidth]);

    return {boxWidth}
}

export default useStyle;