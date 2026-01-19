#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

from models.known_good import load_known_good

MODULES_CSV_HEADER = [
    "repo_url",
    "name",
    "workspace_path",
    "version",
    "hash",
    "branch"
]

def main():
    parser = argparse.ArgumentParser(description="Convert known_good.json to workspace metadata files for gita and git submodules.")

    parser.add_argument("--known-good", dest="known_good", default="known_good.json", help="Path to known_good.json")
    parser.add_argument("--gita-workspace", dest="gita_workspace", default=".gita-workspace.csv", help="File to output gita workspace metadata")
    args = parser.parse_args()

    # Load known_good using KnownGood dataclass
    known_good = load_known_good(Path(args.known_good))
    modules = list(known_good.modules.values())
    
    gita_metadata = []
    for module in modules:
        if not module.repo:
            raise RuntimeError(f"Module {module.name}: repo must not be empty")
        
        # if no hash is given, use branch
        hash_value = module.hash if module.hash else module.branch
        
        # workspace_path is not available in known_good.json, default to name of repository
        workspace_path = module.name
        
        # gita format: {url},{name},{path},{prop['type']},{repo_flags},{branch}
        row = [module.repo, module.name, workspace_path, "", "", hash_value]
        gita_metadata.append(row)

    with open(args.gita_workspace, "w", newline="") as f:
        writer = csv.writer(f)
        for row in gita_metadata:
            writer.writerow(row)

if __name__ == "__main__":
    main()
