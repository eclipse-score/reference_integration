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
# jq is already installed by the previous step.

# Read repositories from the repos.json file created by the previous step
repos=$(cat repos.json)
repo_count=$(echo "$repos" | jq length)
# Initialize an empty string for paths to be outputted
repo_paths_output=""
for i in $(seq 0 $((repo_count-1))); do
  name=$(echo "$repos" | jq -r ".[$i].name")
  url=$(echo "$repos" | jq -r ".[$i].url")
  ref=$(echo "$repos" | jq -r ".[$i].version") # This can be a branch, tag, or commit hash
  path=$(echo "$repos" | jq -r ".[$i].path") # e.g., "repos/score_baselibs"
  echo "Checking out $name ($ref) to $path"
  # Create the parent directory if it doesn't exist
  mkdir -p "$(dirname "$path")"
  # Check if 'ref' looks like a commit hash (e.g., 40 hex characters)
  # This is a heuristic; a more robust check might involve fetching refs first.
  if [[ "$ref" =~ ^[0-9a-fA-F]{40}$ ]]; then
    echo "  Detected commit hash. Cloning and then checking out."
    git clone "$url" "$path"
    (cd "$path" && git checkout "$ref")
  else
    echo "  Detected branch/tag. Cloning with --branch."
    git clone --depth 1 --branch v"$ref" "$url" "$path"
  fi
  # Append the path to the list, separated by commas
  if [ -z "$repo_paths_output" ]; then
    repo_paths_output="$path"
  else
    repo_paths_output="$repo_paths_output,$path"
  fi
done
# Output all paths as a single variable
echo "repo_paths=$repo_paths_output" >> $GITHUB_OUTPUT
