#!/usr/bin/env python3
"""
Update a known_good.json file by pinning modules to specific commits.

Usage:
    python3 tools/override_known_good_repo.py \
            --known known_good.json \
            --output known_good.updated.json \
            --module-override https://github.com/org/repo.git@abc123def

This script reads a known_good.json file and produces a new one with specified
module commit pins. The output can then be used with 
update_module_from_known_good.py to generate the MODULE.bazel file.
"""
import argparse
import os
import re
import datetime as dt
from pathlib import Path
from typing import Dict, List
import logging

from models import Module
from models.known_good import KnownGood, load_known_good

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def parse_and_apply_overrides(modules: Dict[str, Module], repo_overrides: List[str]) -> int:
    """
    Parse repo override arguments and apply them to modules.
    
    Supports two formats:
    1. module_name@hash                                  (find repo from module)
    2. module_name@repo_url@hash                         (explicit repo with module validation)
    
    Args:
        modules: Dictionary mapping module names to Module instances
        repo_overrides: List of override strings
    
    Returns:
        The number of overrides applied.
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
            
            # Validate module exists
            if module_name not in modules:
                logging.warning(
                    f"Module '{module_name}' not found in known_good.json\n"
                    f"Available modules: {', '.join(sorted(modules.keys()))}"
                )
                continue
            
            module = modules[module_name]
            old_value = module.version or module.hash
            
            if commit_hash == module.hash:
                logging.info(
                    f"Module '{module_name}' already at specified commit {commit_hash}, no change needed"
                )
            else:
                module.hash = commit_hash
                module.version = None  # Clear version when overriding hash
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
            
            # Validate module exists
            if module_name not in modules:
                logging.warning(
                    f"Module '{module_name}' not found in known_good.json\n"
                    f"Available modules: {', '.join(sorted(modules.keys()))}"
                )
                continue
            
            module = modules[module_name]
            old_value = module.version or module.hash
            
            if module.hash != commit_hash:
                module.hash = commit_hash
                module.version = None  # Clear version when overriding hash
            
            module.repo = repo_url
            logging.info(f"Applied override to {module_name}: {old_value} -> {commit_hash} (repo: {repo_url})")
            overrides_applied += 1
        
        else:
            raise SystemExit(
                f"Invalid override spec: {entry}\n"
                "Supported formats:\n"
                "  1. module_name@commit_hash\n"
                "  2. module_name@repo_url@commit_hash\n"
            )
    
    return overrides_applied


def apply_overrides(known_good: KnownGood, repo_overrides: List[str]) -> KnownGood:
    """Apply repository commit overrides to the known_good data.
    
    Args:
        known_good: KnownGood instance to modify
        repo_overrides: List of override strings
        
    Returns:
        Updated KnownGood instance
    """
    # Parse and apply overrides
    overrides_applied = parse_and_apply_overrides(known_good.modules, repo_overrides)
    
    if overrides_applied == 0:
        logging.warning("No overrides were applied to any modules")
    else:
        logging.info(f"Successfully applied {overrides_applied} override(s)")
    
    # Update timestamp
    known_good.timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat() + "Z"
    
    return known_good


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Override repository commits in known_good.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pin by module name (simplest - looks up repo automatically)
  python3 tools/override_known_good_repo.py \
      --known known_good.json \
      --output known_good.updated.json \
      --module-override score_baselibs@abc123def

  # Pin with module name and explicit repo URL
  python3 tools/override_known_good_repo.py \
      --known known_good.json \
      --output known_good.updated.json \
      --module-override score_baselibs@https://github.com/eclipse-score/baselibs.git@abc123

  # Pin multiple modules
  python3 tools/override_known_good_repo.py \
      --known known_good.json \
      --output known_good.updated.json \
      --module-override score_baselibs@abc123 \
      --module-override score_communication@def456
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
        "--module-override",
        dest="module_overrides",
        action="append",
        required=False,
        help=(
            "Override a module to a commit. Formats: module_name@hash | "
            "module_name@repo_url@hash. Can be specified multiple times."
        ),
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
    
    # Load, update, and output
    logging.info(f"Loading {known_path}")
    try:
        known_good = load_known_good(known_path)
    except FileNotFoundError as e:
        raise SystemExit(f"ERROR: {e}")
    except ValueError as e:
        raise SystemExit(f"ERROR: {e}")
    
    if not args.module_overrides:
        parser.error("at least one --module-override is required")

    overrides = args.module_overrides

    updated_known_good = apply_overrides(known_good, overrides)
    updated_known_good.write(Path(output_path), args.dry_run)


if __name__ == "__main__":
    main()
