#!/usr/bin/env python3
import argparse
import json
import csv

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
    parser.add_argument("--git-submodules",  dest="git_submodules", default=".gitmodules", help="File to output git submodules metadata")
    args = parser.parse_args()

    with open(args.known_good, "r") as f:
        data = json.load(f)

    modules = data.get("modules", {})
    
    gita_metadata = []
    for name, info in modules.items():
        repo_url = info.get("repo", "")
        if not repo_url:
            raise RuntimeError("repo must not be empty")
        
        # default branch: main
        branch = info.get("branch", "main")
        
        # if no hash is given, use branch
        hash_ = info.get("hash", branch)
        
        # workspace_path is not available in known_good.json, default to name of repository
        workspace_path = name
        
        # gita format: {url},{name},{path},{prop['type']},{repo_flags},{branch}
        row = [repo_url, name, workspace_path, "", "", hash_]
        gita_metadata.append(row)

    with open(args.gita_workspace, "w", newline="") as f:
        writer = csv.writer(f)
        for row in gita_metadata:
            writer.writerow(row)

    with open(args.git_submodules, "w") as f:
        for name, info in modules.items():
            repo_url = info.get("repo", "")
            branch = info.get("branch", "main")
            workspace_path = name
            f.write(f"[submodule \"{name}\"]\n")
            f.write(f"\tpath = {workspace_path}\n")
            f.write(f"\turl = {repo_url}\n")
            f.write(f"\tbranch = {branch}\n")

if __name__ == "__main__":
    main()
