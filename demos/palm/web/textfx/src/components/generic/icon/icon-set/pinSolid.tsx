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

const PinSolid = (props: any) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      fill="none"
      viewBox="0 0 24 24"
      {...props}
    >
      <path
        fill="currentColor"
        d="M12 22L11 21V16H5V14L7 11V4C7 3.45 7.19167 2.98333 7.575 2.6C7.975 2.2 8.45 2 9 2H15C15.55 2 16.0167 2.2 16.4 2.6C16.8 2.98333 17 3.45 17 4V11L19 14V16H13V21L12 22Z"
      />
    </svg>
  )
}

export default PinSolid
