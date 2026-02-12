#!/usr/bin/env python3
"""
Read a known_good.json file and generate a score_modules.MODULE.bazel file
with `bazel_dep` and `git_override` calls for each module in the JSON.

Usage:
  python3 scripts/known_good/update_module_from_known_good.py \
      --known known_good.json \
      --output score_modules.MODULE.bazel

The generated score_modules.MODULE.bazel file is included by MODULE.bazel.

Note: To override repository commits before generating the MODULE.bazel file,
use scripts/known_good/override_known_good_repo.py first to create an updated known_good.json.
"""
import argparse
import os
import re
import logging
from typing import Dict, List, Optional
from pathlib import Path

from models import Module
from models.known_good import load_known_good

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')


def generate_git_override_blocks(modules: List[Module], repo_commit_dict: Dict[str, str]) -> List[str]:
    """Generate bazel_dep and git_override blocks for each module."""
    blocks = []
    
    for module in modules:
        commit = module.hash
        
        # Allow overriding specific repos via command line
        if module.repo in repo_commit_dict:
            commit = repo_commit_dict[module.repo]
        
        # Generate patches lines if bazel_patches exist
        patches_lines = ""
        if module.bazel_patches:
            patches_lines = "    patches = [\n"
            for patch in module.bazel_patches:
                patches_lines += f'        "{patch}",\n'
            patches_lines += "    ],\n    patch_strip = 1,\n"
        
        if module.version:
            # If version is provided, use bazel_dep with single_version_override
            block = (
                f'bazel_dep(name = "{module.name}")\n'
                'single_version_override(\n'
                f'    module_name = "{module.name}",\n'
                f'    version = "{module.version}",\n'
                f'{patches_lines}'
                ')\n'
            )
        else:
            if not module.repo or not commit:
                logging.warning("Skipping module %s with missing repo or commit: repo=%s, commit=%s", 
                              module.name, module.repo, commit)
                continue

            # Validate commit hash format (7-40 hex characters)
            if not re.match(r'^[a-fA-F0-9]{7,40}$', commit):
                logging.warning("Skipping module %s with invalid commit hash: %s", module.name, commit)
                continue
            
            # If no version, use bazel_dep with git_override
            block = (
                f'bazel_dep(name = "{module.name}")\n'
                'git_override(\n'
                f'    module_name = "{module.name}",\n'
                f'    remote = "{module.repo}",\n'
                f'    commit = "{commit}",\n'
                f'{patches_lines}'
                ')\n'
            )
        
        blocks.append(block)
    
    return blocks

def generate_local_override_blocks(modules: List[Module]) -> List[str]:
    """Generate bazel_dep and local_path_override blocks for each module."""
    blocks = []
    
    for module in modules:
        block = (
            f'bazel_dep(name = "{module.name}")\n'
            'local_path_override(\n'
            f'    module_name = "{module.name}",\n'
            f'    path = "{module.name}",\n'
            ')\n'
        )
        
        blocks.append(block)
    
    return blocks

def generate_file_content(args: argparse.Namespace, modules: List[Module], repo_commit_dict: Dict[str, str], timestamp: Optional[str] = None) -> str:
    """Generate the complete content for score_modules.MODULE.bazel."""
    # License header
    header = (
        "# *******************************************************************************\n"
        "# Copyright (c) 2025 Contributors to the Eclipse Foundation\n"
        "#\n"
        "# See the NOTICE file(s) distributed with this work for additional\n"
        "# information regarding copyright ownership.\n"
        "#\n"
        "# This program and the accompanying materials are made available under the\n"
        "# terms of the Apache License Version 2.0 which is available at\n"
        "# https://www.apache.org/licenses/LICENSE-2.0\n"
        "#\n"
        "# SPDX-License-Identifier: Apache-2.0\n"
        "# *******************************************************************************\n"
        "\n"
    )

    if timestamp:
        header += (
            f"# Generated from known_good.json at {timestamp}\n"
            "# Do not edit manually - use scripts/known_good/update_module_from_known_good.py\n"
            "\n"
        )
    
    if args.override_type == "git":
        blocks = generate_git_override_blocks(modules, repo_commit_dict)
    else:
        header += (
            "# Note: This file uses local_path overrides. Ensure that local paths are set up correctly.\n"
            "\n"
        )
        blocks = generate_local_override_blocks(modules)

    
    if not blocks:
        raise SystemExit("No valid modules to generate git_override blocks")
    
    return header + "\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate score_modules.MODULE.bazel from known_good.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate MODULE.bazel from known_good.json
  python3 scripts/known_good/update_module_from_known_good.py

  # Use a custom input and output file
  python3 scripts/known_good/update_module_from_known_good.py \\
      --known custom_known_good.json \\
      --output custom_modules.MODULE.bazel

  # Preview without writing
  python3 scripts/known_good/update_module_from_known_good.py --dry-run

Note: To override repository commits, use scripts/known_good/override_known_good_repo.py first.
        """
    )
    parser.add_argument(
        "--known",
        default="known_good.json",
        help="Path to known_good.json (default: known_good.json)"
    )
    parser.add_argument(
        "--output",
        default="score_modules.MODULE.bazel",
        help="Output file path (default: score_modules.MODULE.bazel)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated content instead of writing to file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--repo-override",
        action="append",
        help="Override commit for a specific repo (format: <REPO_URL>@<COMMIT_SHA>)"
    )
    parser.add_argument(
        "--override-type",
        choices=["local_path", "git"],
        default="git",
        help="Type of override to use (default: git)"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    known_path = os.path.abspath(args.known)
    output_path = os.path.abspath(args.output)
    
    if not os.path.exists(known_path):
        raise SystemExit(f"known_good.json not found at {known_path}")
    
    # Parse repo overrides
    repo_commit_dict = {}
    if args.repo_override:
        repo_pattern = re.compile(r'https://[a-zA-Z0-9.-]+/[a-zA-Z0-9._/-]+\.git@[a-fA-F0-9]{7,40}$')
        for entry in args.repo_override:
            if not repo_pattern.match(entry):
                raise SystemExit(
                    f"Invalid --repo-override format: {entry}\n"
                    "Expected format: https://github.com/org/repo.git@<commit_sha>"
                )
            repo_url, commit_hash = entry.split("@", 1)
            repo_commit_dict[repo_url] = commit_hash
    
    # Load known_good.json
    try:
        known_good = load_known_good(Path(known_path))
    except FileNotFoundError as e:
        raise SystemExit(f"ERROR: {e}")
    except ValueError as e:
        raise SystemExit(f"ERROR: {e}")
    
    if not known_good.modules:
        raise SystemExit("No modules found in known_good.json")
    
    # Get modules list
    modules = list(known_good.modules.values())
    
    # Generate file content
    content = generate_file_content(args, modules, repo_commit_dict, known_good.timestamp)
    
    if args.dry_run:
        print(f"Dry run: would write to {output_path}\n")
        print("---- BEGIN GENERATED CONTENT ----")
        print(content)
        print("---- END GENERATED CONTENT ----")
        print(f"\nGenerated {len(modules)} git_override entries")
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generated {output_path} with {len(modules)} {args.override_type}_override entries")


if __name__ == "__main__":
    main()
