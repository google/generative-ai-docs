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

const Copy = (props: any) => {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <g clipPath="url(#clip0_453_8814)">
        <path
          d="M5 22C4.45 22 3.975 21.8083 3.575 21.425C3.19167 21.025 3 20.55 3 20V6H5V20H16V22H5ZM9 18C8.45 18 7.975 17.8083 7.575 17.425C7.19167 17.025 7 16.55 7 16V4C7 3.45 7.19167 2.98333 7.575 2.6C7.975 2.2 8.45 2 9 2H18C18.55 2 19.0167 2.2 19.4 2.6C19.8 2.98333 20 3.45 20 4V16C20 16.55 19.8 17.025 19.4 17.425C19.0167 17.8083 18.55 18 18 18H9ZM9 16H18V4H9V16ZM9 16V4V16Z"
          fill="currentColor"
        />
      </g>
      <defs>
        <clipPath id="clip0_453_8814">
          <rect width="24" height="24" fill="white" />
        </clipPath>
      </defs>
    </svg>
  )
}

export default Copy
