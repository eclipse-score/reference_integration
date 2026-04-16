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

"""
Recategorize CodeQL SARIF results according to coding standards.
"""

import json
import re
import subprocess
import sys
from pathlib import Path


# Configuration paths
RECATEGORIZE_SCRIPT = "codeql-coding-standards-repo/scripts/guideline_recategorization/recategorize.py"
CODING_STANDARDS_CONFIG = "./.github/codeql/coding-standards.yml"
CODING_STANDARDS_SCHEMA = "codeql-coding-standards-repo/schemas/coding-standards-schema-1.0.0.json"
SARIF_SCHEMA = "codeql-coding-standards-repo/schemas/sarif-schema-2.1.0.json"
SARIF_FILE = "sarif-results/cpp.sarif"
OUTPUT_DIR = "sarif-results-recategorized"


def validate_paths():
    """
    Validate that required files exist.

    Note: Only validates files needed for recategorization if SARIF exists.
    Returns:
        True if validation passes or SARIF doesn't exist, False on critical errors
    """
    # First check if SARIF file exists - if not, nothing to recategorize
    if not Path(SARIF_FILE).exists():
        print(f"Info: SARIF file not found at {SARIF_FILE}", file=sys.stderr)
        return False  # Signal to skip recategorization

    # SARIF exists, check for recategorization dependencies
    optional_files = [
        RECATEGORIZE_SCRIPT,
        CODING_STANDARDS_SCHEMA,
        SARIF_SCHEMA,
    ]

    required_files = [
        CODING_STANDARDS_CONFIG,
    ]

    # Check required files (fail if missing)
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"Error: Required file not found: {file_path}", file=sys.stderr)
            return False

    # Warn about optional files but don't fail
    missing_optional = []
    for file_path in optional_files:
        if not Path(file_path).exists():
            missing_optional.append(file_path)

    if missing_optional:
        print(f"Warning: Some recategorization files not found: {missing_optional}", file=sys.stderr)
        print("Recategorization will be skipped, but filtering will still be applied.", file=sys.stderr)

    return True


def recategorize_sarif():
    """
    Run the CodeQL recategorization script on SARIF results.

    Returns:
        True if successful or skipped, False on critical errors
    """
    # Check if recategorization script exists
    if not Path(RECATEGORIZE_SCRIPT).exists():
        print(f"Info: Recategorization script not found at {RECATEGORIZE_SCRIPT}", file=sys.stderr)
        print("Skipping recategorization step (will apply filtering only).", file=sys.stderr)
        return True  # Not a failure, just skip this step

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / Path(SARIF_FILE).name

    print(f"Processing {SARIF_FILE} for recategorization...")

    try:
        # Run recategorization script
        result = subprocess.run(
            [
                sys.executable,
                RECATEGORIZE_SCRIPT,
                "--coding-standards-schema-file",
                CODING_STANDARDS_SCHEMA,
                "--sarif-schema-file",
                SARIF_SCHEMA,
                CODING_STANDARDS_CONFIG,
                SARIF_FILE,
                str(output_file),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        print("Recategorization completed successfully")
        if result.stdout:
            print("Output:", result.stdout)

        # Replace original SARIF file with recategorized version
        sarif_path = Path(SARIF_FILE)

        if sarif_path.exists():
            sarif_path.unlink()
            print(f"Removed original {SARIF_FILE}")

        # Move recategorized file to original location
        output_file.replace(sarif_path)
        print(f"Moved recategorized SARIF to {SARIF_FILE}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: Recategorization script failed: {e}", file=sys.stderr)
        if e.stderr:
            print(f"Error output: {e.stderr}", file=sys.stderr)
        return False
    except (FileNotFoundError, OSError) as e:
        print(f"Error: File operation failed: {e}", file=sys.stderr)
        return False


def filter_sarif_results():
    """
    Filter SARIF results to only include entries with paths matching repos/*.

    Returns:
        True if successful, False otherwise
    """
    sarif_path = Path(SARIF_FILE)

    if not sarif_path.exists():
        print(f"Warning: SARIF file not found: {SARIF_FILE}", file=sys.stderr)
        return False

    try:
        # Load SARIF file
        with open(sarif_path, "r") as f:
            sarif_data = json.load(f)

        print("Filtering SARIF results to only include entries with paths matching repos/* ...")

        # Filter runs and results
        if "runs" in sarif_data:
            for run in sarif_data["runs"]:
                if "results" in run:
                    filtered_results = []

                    for result in run["results"]:
                        # Check if result has locations
                        locations = result.get("locations", [])
                        if not locations:
                            continue

                        # Check if first location URI matches repos/ pattern
                        first_location = locations[0].get("physicalLocation", {})
                        artifact_uri = first_location.get("artifactLocation", {}).get("uri", "")

                        # Pattern: (^|/)repos/ - matches repos/ at start or after a /
                        if artifact_uri and re.search(r"(^|/)repos/", artifact_uri):
                            filtered_results.append(result)

                    # Update results with filtered list
                    run["results"] = filtered_results
                    print(
                        f"Run '{run.get('tool', {}).get('driver', {}).get('name', 'unknown')}' "
                        f"now has {len(filtered_results)} results"
                    )

        # Write filtered SARIF back to file
        with open(sarif_path, "w") as f:
            json.dump(sarif_data, f, indent=2)

        print(f"Filtered SARIF written to {SARIF_FILE}")
        return True

    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Failed to filter SARIF file: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    # Validate required files exist
    has_sarif = validate_paths()

    if not has_sarif:
        # No SARIF file to process - this is normal before CodeQL analysis runs
        print("No SARIF file found - skipping recategorization.")
        print("This is expected if CodeQL analysis hasn't completed yet.")
        sys.exit(0)

    # Run recategorization (will skip gracefully if script not available)
    if not recategorize_sarif():
        print("Warning: Recategorization failed, continuing with filtering...", file=sys.stderr)

    # Filter SARIF results to only include repos/*
    if not filter_sarif_results():
        sys.exit(1)

    print("Recategorization workflow completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
