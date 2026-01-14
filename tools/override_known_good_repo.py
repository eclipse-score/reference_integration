#!/usr/bin/env python3
"""
Update a known_good.json file by overriding specific repository commits.

Usage:
  python3 tools/override_known_good_repo.py \
      --known known_good.json \
      --output known_good.updated.json \
      --repo-override https://github.com/org/repo.git@abc123def

This script reads a known_good.json file and produces a new one with specified
repository commits overridden. The output can then be used with 
update_module_from_known_good.py to generate the MODULE.bazel file.
"""
import argparse
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def load_known_good(path: str) -> Dict[str, Any]:
    """Load and parse the known_good.json file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and isinstance(data.get("modules"), dict):
        return data
    raise SystemExit(
        f"Invalid known_good.json at {path} (expected object with 'modules' dict)"
    )


def parse_and_apply_overrides(modules: Dict[str, Any], repo_overrides: List[str]) -> int:
    """
    Parse repo override arguments and apply them to modules.
    
    Supports three formats:
    1. module_name@hash                                  (find repo from module)
    2. module_name@repo_url@hash                         (explicit repo with module validation)
    
    Returns the number of overrides applied.
    """
    repo_url_pattern = re.compile(r'^https://[a-zA-Z0-9.-]+/[a-zA-Z0-9._/-]+\.git$')
    hash_pattern = re.compile(r'^[a-fA-F0-9]{7,40}$')
    overrides_applied = 0
    
    # Parse and validate overrides
    for entry in repo_overrides:
        logging.info(f"Override registered: {entry}")
        parts = entry.split("@")
        
        if len(parts) == 2:
            # module_name@hash
            module_name, commit_hash = parts
            
            if not hash_pattern.match(commit_hash):
                raise SystemExit(
                    f"Invalid commit hash in '{entry}': {commit_hash}\n"
                    "Expected 7-40 hex characters"
                )
            
            # Validate module exists and matches repo (only if module is in known_good.json)
            if module_name not in modules:
                logging.warning(
                    f"Module '{module_name}' not found in known_good.json\n"
                    f"Available modules: {', '.join(sorted(modules.keys()))}"
                )
            old_value = modules[module_name].get("hash") or modules[module_name].get("commit") or modules[module_name].get("version")
            if commit_hash == old_value:
                logging.info(
                    f"Module '{module_name}' already at specified commit {commit_hash}, no change needed"
                )
            else:
                modules[module_name]["hash"] = commit_hash
                modules[module_name].pop("version", None)
                logging.info(f"Applied override to {module_name}: {old_value} -> {commit_hash}")
                overrides_applied += 1
        
        elif len(parts) == 3:
            # Format: module_name@repo_url@hash
            module_name, repo_url, commit_hash = parts
            
            if not hash_pattern.match(commit_hash):
                raise SystemExit(
                    f"Invalid commit hash in '{entry}': {commit_hash}\n"
                    "Expected 7-40 hex characters"
                )
            
            if not repo_url_pattern.match(repo_url):
                raise SystemExit(
                    f"Invalid repo URL in '{entry}': {repo_url}\n"
                    "Expected format: https://github.com/org/repo.git"
                )
            
            # Validate module exists and matches repo (only if module is in known_good.json)
            if module_name not in modules:
                logging.warning(
                    f"Module '{module_name}' not found in known_good.json\n"
                    f"Available modules: {', '.join(sorted(modules.keys()))}"
                )
                continue
            old_value = modules[module_name].get("hash") or modules[module_name].get("commit") or modules[module_name].get("version")
            if not old_value == commit_hash:
                modules[module_name]["hash"] = commit_hash
                modules[module_name].pop("version", None)
            modules[module_name]["repo"] = repo_url
            logging.info(f"Applied override to {module_name}: {old_value} -> {commit_hash}")
            overrides_applied += 1
        
        else:
            raise SystemExit(
                f"Invalid --override format: {entry}\n"
                "Supported formats:\n"
                "  1. module_name@commit_hash\n"
                "  2. module_name@repo_url@commit_hash\n"
            )
    
    return overrides_applied


def override_repo_commits(data: Dict[str, Any], repo_overrides: List[str]) -> Dict[str, Any]:
    """Apply repository commit overrides to the known_good data."""
    modules = data.get("modules", {})
    
    # Parse and apply overrides
    overrides_applied = parse_and_apply_overrides(modules, repo_overrides)
    
    if overrides_applied == 0:
        logging.warning("No overrides were applied to any modules")
    else:
        logging.info(f"Successfully applied {overrides_applied} override(s)")
    
    # Update timestamp
    data["timestamp"] = datetime.now().isoformat() + "Z"
    
    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Override repository commits in known_good.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Override by module name (simplest - looks up repo automatically)
  python3 tools/override_known_good_repo.py \\
      --known known_good.json \\
      --output known_good.updated.json \\
      --repo-override score_baselibs@abc123def

  # Override with explicit repo URL
  python3 tools/override_known_good_repo.py \\
      --known known_good.json \\
      --output known_good.updated.json \\
      --repo-override https://github.com/eclipse-score/baselibs.git@abc123def

  # Override with module name and repo (validates module exists and repo matches)
  python3 tools/override_known_good_repo.py \\
      --known known_good.json \\
      --output known_good.updated.json \\
      --repo-override score_baselibs@https://github.com/eclipse-score/baselibs.git@abc123

  # Override multiple repositories
  python3 tools/override_known_good_repo.py \\
      --known known_good.json \\
      --output known_good.updated.json \\
      --repo-override score_baselibs@abc123 \\
      --repo-override score_communication@def456
        """
    )
    
    parser.add_argument(
        "--known",
        default="known_good.json",
        help="Path to input known_good.json file (default: known_good.json)"
    )
    parser.add_argument(
        "--output",
        default="known_good.updated.json",
        help="Path to output JSON file (default: known_good.updated.json)"
    )
    parser.add_argument(
        "--repo-override",
        action="append",
        required=True,
        help="Override commit for a repo. Formats: module_name@hash | module_name@repo_url@hash. Can be specified multiple times."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the result instead of writing to file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    known_path = os.path.abspath(args.known)
    output_path = os.path.abspath(args.output)
    
    if not os.path.exists(known_path):
        raise SystemExit(f"Input file not found: {known_path}")
    
    # Load, update, and output
    logging.info(f"Loading {known_path}")
    data = load_known_good(known_path)
    updated_data = override_repo_commits(data, args.repo_override)
    output_json = json.dumps(updated_data, indent=4, sort_keys=False) + "\n"
    
    if args.dry_run:
        print(f"\nDry run: would write to {output_path}\n")
        print("---- BEGIN UPDATED JSON ----")
        print(output_json, end="")
        print("---- END UPDATED JSON ----")
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_json)
        logging.info(f"Successfully wrote updated known_good.json to {output_path}")


if __name__ == "__main__":
    main()
