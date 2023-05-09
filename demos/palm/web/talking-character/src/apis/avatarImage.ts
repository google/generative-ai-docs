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

import React, {useState} from 'react';

const useAvatarImage =
    () => {
      const [storedImage, setStoredImage] =
          useState(localStorage.getItem('imageUrl') ?? '');

      const handleUploadImage =
          async (event: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
          const reader = new FileReader();
          reader.readAsDataURL(selectedFile);
          reader.onload = () => {
            const imageUrl = reader.result as string;
            localStorage.setItem(
                'previousUrl', localStorage.getItem('imageUrl') ?? '');
            localStorage.setItem(
                'imageUrl', imageUrl);  // Store image URL in localStorage
            setStoredImage(imageUrl);
          };
        }
      };

      const handleCancelUploadImage =
          () => {
            const previousUrl = localStorage.getItem('previousUrl');
            if (previousUrl !== null && previousUrl !== undefined) {
              localStorage.setItem('imageUrl', previousUrl);
              setStoredImage(previousUrl);
              localStorage.removeItem('previousUrl');
            }
          }

      const finishAvatarChange =
          () => {
            localStorage.removeItem('previousUrl');
          }

      return {
        storedImage, setStoredImage, handleUploadImage, handleCancelUploadImage,
            finishAvatarChange,
      }
    }

export default useAvatarImage;