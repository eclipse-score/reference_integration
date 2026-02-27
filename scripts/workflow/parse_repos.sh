#!/bin/bash
# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
sudo apt-get update && sudo apt-get install -y jq
JSON_FILE="./known_good.json"
# Check if the file exists
if [ ! -f "$JSON_FILE" ]; then
  echo "Error file not found '$JSON_FILE' "
  ls -la .
  exit 1
fi
# Create repos.json from known_good.json
# This jq command transforms the 'modules' object into an array of repository objects
# with 'name', 'url', 'version' (branch/tag/hash), and 'path'.
jq '[.modules.target_sw | to_entries[] | {
  name: .key,
  url: .value.repo,
  version: (.value.branch // .value.hash // .value.version),
  path: ("repos/" + .key)
}]' "$JSON_FILE" > repos.json
echo "Generated repos.json:"
cat repos.json
echo "" # Add a newline for better readability
# The following GITHUB_OUTPUT variables are set for each module.
# These might be useful for other steps, but are not directly used by the 'checkout-repos' step
# which now reads 'repos.json' directly.
echo "MODULE_COUNT=$(jq '.modules.target_sw | length' "$JSON_FILE")" >> $GITHUB_OUTPUT
jq -c '.modules.target_sw | to_entries[]' "$JSON_FILE" | while read -r module_entry; do
  module_name=$(echo "$module_entry" | jq -r '.key')
  repo_url=$(echo "$module_entry" | jq -r '.value.repo // empty')
  version=$(echo "$module_entry" | jq -r '.value.version // empty')
  branch=$(echo "$module_entry" | jq -r '.value.branch // empty')
  hash=$(echo "$module_entry" | jq -r '.value.hash // empty')
  echo "${module_name}_url=$repo_url" >> $GITHUB_OUTPUT
  if [ -n "$version" ]; then
  echo "${module_name}_version=$version" >> $GITHUB_OUTPUT
  fi
  if [ -n "$branch" ]; then
    echo "${module_name}_branch=$branch" >> $GITHUB_OUTPUT
  fi
  if [ -n "$hash" ]; then
    echo "${module_name}_hash=$hash" >> $GITHUB_OUTPUT
  fi
done
