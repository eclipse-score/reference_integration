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

# Generate .gita-workspace.csv from known_good.json
python3 tools/known_good_to_gita_workspace.py known_good.json .gita-workspace.csv
python3 tools/update_module_from_known_good.py --override-type local_path

# Automagically clone repositories listed in .gita-workspace.csv
echo "Cloning repositories listed in .gita-workspace.csv..."
gita clone --preserve-path --from-file .gita-workspace.csv
# Output the status of all cloned repositories
echo "Status of all cloned repositories:"
gita ll
