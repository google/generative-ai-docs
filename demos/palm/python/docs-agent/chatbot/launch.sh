#!/bin/bash

#
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Default values
port=5000
name='chatbot'
# Specify port number with -p argument `launch.sh -p 5555`
while getopts "n:p:h" opt; do
  case $opt in
    p) port="${OPTARG}";;
    h) echo "Usage: $0 [-p port]"; exit 1;;
    \?) echo "Invalid option: -$OPTARG"; exit 1;;
  esac
done
# Define your hostname
if [[ -z "$HOSTNAME" ]]; then
  export HOSTNAME="localhost"
fi
export FLASK_PORT=$port
export FLASK_APP=$name
export FLASK_DEBUG=true

flask run --host=$HOSTNAME --port=$FLASK_PORT
