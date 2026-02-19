#!/usr/bin/env python3
"""
Read a known_good.json file and generate a score_modules.MODULE.bazel file
with `bazel_dep` and `git_override` calls for each module in the JSON.
It generates also rust_coverage/BUILD file with `rust_coverage_report` for each module with rust impl.

Usage:
  python3 scripts/known_good/update_module_from_known_good.py \
      --known known_good.json \
      --output-dir-modules bazel_common \
      --output-dir-coverage rust_coverage

The generated score_modules_NAME_.MODULE.bazel file is included by MODULE.bazel.

Note: To override repository commits before generating the MODULE.bazel file,
use scripts/known_good/override_known_good_repo.py first to create an updated known_good.json.
"""

import argparse
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from models import Module
from models.known_good import load_known_good

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def generate_git_override_blocks(
    modules: List[Module], repo_commit_dict: Dict[str, str]
) -> List[str]:
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
                "single_version_override(\n"
                f'    module_name = "{module.name}",\n'
                f'    version = "{module.version}",\n'
                f"{patches_lines}"
                ")\n"
            )
        else:
            if not module.repo or not commit:
                logging.warning(
                    "Skipping module %s with missing repo or commit: repo=%s, commit=%s",
                    module.name,
                    module.repo,
                    commit,
                )
                continue

            # Validate commit hash format (7-40 hex characters)
            if not re.match(r"^[a-fA-F0-9]{7,40}$", commit):
                logging.warning(
                    "Skipping module %s with invalid commit hash: %s",
                    module.name,
                    commit,
                )
                continue

            # If no version, use bazel_dep with git_override
            block = (
                f'bazel_dep(name = "{module.name}")\n'
                "git_override(\n"
                f'    module_name = "{module.name}",\n'
                f'    remote = "{module.repo}",\n'
                f'    commit = "{commit}",\n'
                f"{patches_lines}"
                ")\n"
            )

        blocks.append(block)

    return blocks


def generate_local_override_blocks(modules: List[Module]) -> List[str]:
    """Generate bazel_dep and local_path_override blocks for each module."""
    blocks = []

    for module in modules:
        block = (
            f'bazel_dep(name = "{module.name}")\n'
            "local_path_override(\n"
            f'    module_name = "{module.name}",\n'
            f'    path = "{module.name}",\n'
            ")\n"
        )

        blocks.append(block)

    return blocks


def generate_coverage_blocks(modules: List[Module]) -> List[str]:
    """Generate rust_coverage_report  blocks for each module with rust impl."""
    blocks = ["""load("@score_tooling//:defs.bzl", "rust_coverage_report")\n\n"""]

    for module in modules:
        if "rust" not in module.metadata.langs:
            continue

        if module.metadata.exclude_test_targets:
            excluded_tests = f" except {' '.join([f'@{module.name}{target}' for target in module.metadata.exclude_test_targets])}"
        else:
            excluded_tests = ""

        block = f"""
rust_coverage_report(
    name = "rust_coverage_{module.name}",
    bazel_configs = [
        "linux-x86_64",
        "ferrocene-coverage",
    ],
    query = 'kind("rust_test", @{module.name}{module.metadata.code_root_path}){excluded_tests}',
    visibility = ["//visibility:public"],
)
            """

        blocks.append(block)

    return blocks


def generate_file_content(
    args: argparse.Namespace,
    modules: List[Module],
    repo_commit_dict: Dict[str, str],
    timestamp: Optional[str] = None,
    file_type: str = "module",
) -> str:
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
    if file_type == "module":
        if args.override_type == "git":
            blocks = generate_git_override_blocks(modules, repo_commit_dict)
        else:
            header += (
                "# Note: This file uses local_path overrides. Ensure that local paths are set up correctly.\n"
                "\n"
            )
            blocks = generate_local_override_blocks(modules)
    elif file_type == "build":
        blocks = generate_coverage_blocks(modules)
    else:
        raise ValueError(f"Invalid file_type: {file_type}")

    if not blocks:
        raise SystemExit("No valid modules to generate git_override blocks")

    return header + "\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate score_modules.MODULE.bazel file(s) from known_good.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate MODULE.bazel from known_good.json
  python3 scripts/known_good/update_module_from_known_good.py

  # Use a custom input file (generates score_modules_{group}.MODULE.bazel for each group)
  python3 scripts/known_good/update_module_from_known_good.py \\
      --known custom_known_good.json

  # Specify output directory for grouped modules
  python3 scripts/known_good/update_module_from_known_good.py \\
      --output-dir-modules ./bazel_modules

  # Preview without writing
  python3 scripts/known_good/update_module_from_known_good.py --dry-run

Note:
  - Generates score_modules_{group}.MODULE.bazel for each group
  - To override repository commits, use scripts/known_good/override_known_good_repo.py first.
        """,
    )
    parser.add_argument(
        "--known",
        default=Path(__file__).parents[2] / "known_good.json",
        help="Path to known_good.json (default: known_good.json in repo root)",
    )
    parser.add_argument(
        "--output-dir-modules",
        default=Path(__file__).parents[2] / "bazel_common",
        help="Output directory for grouped structure files (default: bazel_common in repo root)",
    )
    parser.add_argument(
        "--output-dir-coverage",
        default=Path(__file__).parents[2] / "rust_coverage",
        help="Output directory for BUILD coverage file (default: rust_coverage in repo root)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated content instead of writing to file",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--repo-override",
        action="append",
        help="Override commit for a specific repo (format: <REPO_URL>@<COMMIT_SHA>)",
    )
    parser.add_argument(
        "--override-type",
        choices=["local_path", "git"],
        default="git",
        help="Type of override to use (default: git)",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    known_path = os.path.abspath(args.known)

    if not os.path.exists(known_path):
        raise SystemExit(f"known_good.json not found at {known_path}")

    # Parse repo overrides
    repo_commit_dict = {}
    if args.repo_override:
        repo_pattern = re.compile(
            r"https://[a-zA-Z0-9.-]+/[a-zA-Z0-9._/-]+\.git@[a-fA-F0-9]{7,40}$"
        )
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

    # Generate files based on structure (flat vs grouped)
    output_dir_modules = os.path.abspath(args.output_dir_modules)
    os.makedirs(output_dir_modules, exist_ok=True)

    generated_files = []
    total_module_count = 0

    for group_name, group_modules in known_good.modules.items():
        modules = list(group_modules.values())

        if not modules:
            logging.warning(f"Skipping empty group: {group_name}")
            continue

        # Determine output filename: score_modules_{group}.MODULE.bazel
        output_filename = f"score_modules_{group_name}.MODULE.bazel"

        output_path_modules = os.path.join(output_dir_modules, output_filename)
        output_path_coverage = args.output_dir_coverage / "BUILD"

        # Generate file content of MODULE files
        content_module = generate_file_content(
            args, modules, repo_commit_dict, known_good.timestamp, file_type="module"
        )

        if args.dry_run:
            print(f"\nDry run: would write to {output_path_modules}\n")
            print("---- BEGIN GENERATED CONTENT FOR MODULE ----")
            print(content_module)
            print("---- END GENERATED CONTENT FOR MODULE ----")
            print(
                f"\nGenerated {len(modules)} {args.override_type}_override entries for group '{group_name}'"
            )
        else:
            with open(output_path_modules, "w", encoding="utf-8") as f:
                f.write(content_module)
            generated_files.append(output_path_modules)
            total_module_count += len(modules)
            print(
                f"Generated {output_path_modules} with {len(modules)} {args.override_type}_override entries"
            )

        # Generate file content of BUILD coverage files
        if "target_sw" not in group_name:
            continue  # Only generate coverage for software modules

        content_build = generate_file_content(
            args, modules, repo_commit_dict, known_good.timestamp, file_type="build"
        )

        if args.dry_run:
            print(f"\nDry run: would write to {output_path_coverage}\n")
            print("---- BEGIN GENERATED CONTENT FOR BUILD ----")
            print(content_build)
            print("---- END GENERATED CONTENT FOR BUILD ----")
            print(
                f"\nGenerated {len(modules)} {args.override_type}_override entries for group '{group_name}'"
            )
        else:
            with open(output_path_coverage, "w", encoding="utf-8") as f:
                f.write(content_build)
            generated_files.append(output_path_coverage)
            print(f"Generated {output_path_coverage}")

    if not args.dry_run and generated_files:
        print(
            f"\nSuccessfully generated {len(generated_files)} file(s) with {total_module_count} total modules"
        )


if __name__ == "__main__":
    main()
