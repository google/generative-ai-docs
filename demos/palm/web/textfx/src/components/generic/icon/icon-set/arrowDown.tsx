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

const ArrowDown = (props: any) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="36"
      height="36"
      fill="none"
      viewBox="0 0 36 36"
      {...props}
    >
      <circle cx="18" cy="18" r="18" fill="#EDEDED" />
      <g clipPath="url(#arrowClip)">
        <path
          fill="#151515"
          d="M18 24L12 18L13.4 16.6L17 20.2V11H19V20.2L22.6 16.6L24 18L18 24Z"
        />
      </g>
      <defs>
        <clipPath id="arrowClip">
          <path fill="#fff" d="M0 0H24V24H0z" transform="translate(6 6)" />
        </clipPath>
      </defs>
    </svg>
  )
}

export default ArrowDown
