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

const Scene = (props: any) => {
  return (
    <svg
      width="30"
      height="30"
      viewBox="0 0 30 30"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M9.13854 18.9135H22.3385L18.2135 13.7917L15.0052 17.9167L12.2552 15.625L9.13854 18.9135ZM4.92188 27.0833V7.58125C4.92188 7.17715 5.08 6.81259 5.39625 6.48755C5.7125 6.16252 6.08146 6 6.50312 6H24.424C24.8281 6 25.1926 6.16252 25.5177 6.48755C25.8427 6.81259 26.0052 7.17715 26.0052 7.58125V21.2854C26.0052 21.6895 25.8427 22.0541 25.5177 22.3791C25.1926 22.7041 24.8281 22.8667 24.424 22.8667H9.13854L4.92188 27.0833ZM6.50312 23.262L8.47969 21.2854H24.424V7.58125H6.50312V23.262Z"
        fill="currentColor"
      />
      <circle cx="10.4882" cy="11.572" r="1.35536" fill="currentColor" />
    </svg>
  )
}

export default Scene
