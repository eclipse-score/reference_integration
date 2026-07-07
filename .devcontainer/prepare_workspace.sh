#!/bin/bash
# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
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
set -euo pipefail

# Install pipx
sudo apt update
sudo apt install -y pipx

# Install gita
pipx ensurepath
pipx install gita

# Enable bash autocompletion for gita
echo "eval \"\$(register-python-argcomplete gita -s bash)\"" >> ~/.bashrc

# Set GITA_PROJECT_HOME environment variable
echo "export GITA_PROJECT_HOME=$(pwd)/.gita" >> ~/.bashrc
GITA_PROJECT_HOME=$(pwd)/.gita
mkdir -p "$GITA_PROJECT_HOME"
export GITA_PROJECT_HOME

# Generate workspace metadata files from known_good.json:
# - .gita-workspace.csv
python3 scripts/known_good/known_good_to_workspace_metadata.py --known-good known_good.json --gita-workspace .gita-workspace.csv
