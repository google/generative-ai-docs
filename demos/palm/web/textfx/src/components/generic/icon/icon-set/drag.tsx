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

const Drag = (props: any) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      fill="none"
      viewBox="0 0 24 24"
      {...props}
    >
      <g clipPath="url(#a)">
        <path
          fill="#151515"
          d="M9 20C8.45 20 7.975 19.8083 7.575 19.425C7.19167 19.025 7 18.55 7 18C7 17.45 7.19167 16.9833 7.575 16.6C7.975 16.2 8.45 16 9 16C9.55 16 10.0167 16.2 10.4 16.6C10.8 16.9833 11 17.45 11 18C11 18.55 10.8 19.025 10.4 19.425C10.0167 19.8083 9.55 20 9 20ZM15 20C14.45 20 13.975 19.8083 13.575 19.425C13.1917 19.025 13 18.55 13 18C13 17.45 13.1917 16.9833 13.575 16.6C13.975 16.2 14.45 16 15 16C15.55 16 16.0167 16.2 16.4 16.6C16.8 16.9833 17 17.45 17 18C17 18.55 16.8 19.025 16.4 19.425C16.0167 19.8083 15.55 20 15 20ZM9 14C8.45 14 7.975 13.8083 7.575 13.425C7.19167 13.025 7 12.55 7 12C7 11.45 7.19167 10.9833 7.575 10.6C7.975 10.2 8.45 10 9 10C9.55 10 10.0167 10.2 10.4 10.6C10.8 10.9833 11 11.45 11 12C11 12.55 10.8 13.025 10.4 13.425C10.0167 13.8083 9.55 14 9 14ZM15 14C14.45 14 13.975 13.8083 13.575 13.425C13.1917 13.025 13 12.55 13 12C13 11.45 13.1917 10.9833 13.575 10.6C13.975 10.2 14.45 10 15 10C15.55 10 16.0167 10.2 16.4 10.6C16.8 10.9833 17 11.45 17 12C17 12.55 16.8 13.025 16.4 13.425C16.0167 13.8083 15.55 14 15 14ZM9 8C8.45 8 7.975 7.80833 7.575 7.425C7.19167 7.025 7 6.55 7 6C7 5.45 7.19167 4.98333 7.575 4.6C7.975 4.2 8.45 4 9 4C9.55 4 10.0167 4.2 10.4 4.6C10.8 4.98333 11 5.45 11 6C11 6.55 10.8 7.025 10.4 7.425C10.0167 7.80833 9.55 8 9 8ZM15 8C14.45 8 13.975 7.80833 13.575 7.425C13.1917 7.025 13 6.55 13 6C13 5.45 13.1917 4.98333 13.575 4.6C13.975 4.2 14.45 4 15 4C15.55 4 16.0167 4.2 16.4 4.6C16.8 4.98333 17 5.45 17 6C17 6.55 16.8 7.025 16.4 7.425C16.0167 7.80833 15.55 8 15 8Z"
        />
      </g>
      <defs>
        <clipPath id="a">
          <path fill="#fff" d="M0 0H24V24H0z" />
        </clipPath>
      </defs>
    </svg>
  )
}
export default Drag
