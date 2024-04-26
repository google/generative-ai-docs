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

# IF NECESSARY, ADJUST THIS PATH TO YOUR `docs-agent` DIRECTORY.
docs_agent_dir="$HOME/docs-agent"

# Initialize request and filename variables.
request=""
filename=""

# Loop through the arguments and look for the `--file` flag.
while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      shift
      filename="$1"
      shift
      ;;
    *)
      request="$request $1"
      shift
      ;;
  esac
done

# Get the full path for the filename.
if [[ -n "$filename" ]]; then
  filename=$(readlink -m ${filename})
else
  filename="None"
fi

# Check if the POETRY_ACTIVE environment variable is set
if [ -z "$POETRY_ACTIVE" ]; then
  cd "$docs_agent_dir" && poetry run agent helpme "$request" --file "$filename"
else
  agent helpme "$request" --file "$filename"
fi
