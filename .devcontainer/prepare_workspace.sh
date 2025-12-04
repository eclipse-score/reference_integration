#!/bin/bash
set -euo pipefail

# Install pipx
sudo apt update
sudo apt install -y pipx

# Install gita
pipx install gita

# Enable bash autocompletion for gita
echo "eval \"\$(register-python-argcomplete gita -s bash)\"" >> ~/.bashrc

# Set GITA_PROJECT_HOME environment variable
echo "export GITA_PROJECT_HOME=$(pwd)/.gita" >> ~/.bashrc
GITA_PROJECT_HOME=$(pwd)/.gita
mkdir -p "$GITA_PROJECT_HOME"
export GITA_PROJECT_HOME

# Generate a few workspace metadata files from known_good.json:
# - .gita-workspace.csv
python3 tools/known_good_to_workspace_metadata.py --known-good known_good.json --gita-workspace .gita-workspace.csv
