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
    parser = argparse.ArgumentParser(description="Convert known_good.json to baseline.csv format.")
    parser.add_argument("input_json", help="Path to known_good.json")
    parser.add_argument("output_csv", help="Path to output baseline.csv")
    args = parser.parse_args()

    with open(args.input_json, "r") as f:
        data = json.load(f)

    modules = data.get("modules", {})
    rows = []
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
        rows.append(row)

    with open(args.output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    main()
