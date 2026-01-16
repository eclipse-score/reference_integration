#!/usr/bin/env python3
"""Integration build script for SCORE modules.

Captures warning counts for regression tracking and generates build summaries.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add tools directory to path to import Module
script_dir = Path(__file__).parent
repo_root = script_dir.parent
sys.path.insert(0, str(repo_root / "tools"))

from models import Module



# Build target groups - maps module names to their Bazel targets
BUILD_TARGET_GROUPS = {
    "score_baselibs": "@score_baselibs//score/...",
    "score_communication": "@score_communication//score/mw/com:com",
    "score_persistency": "@score_persistency//src/cpp/src/... @score_persistency//src/rust/...",
    "score_kyron": "@score_kyron//src/...",
    "score_orchestrator": "@score_orchestrator//src/...",
    "score_test_scenarios": "@score_test_scenarios//test_scenarios_rust:test_scenarios_rust @score_test_scenarios//test_scenarios_cpp:test_scenarios_cpp",
    "score_feo": "-- @score_feo//... -@score_feo//:docs -@score_feo//:ide_support -@score_feo//:needs_json",
    "score_logging": """@score_logging//score/...
        --@score_baselibs//score/memory/shared/flags:use_typedshmd=False
        --@score_baselibs//score/json:base_library=nlohmann
        --@score_logging//score/datarouter/build_configuration_flags:persistent_logging=False
        --@score_logging//score/datarouter/build_configuration_flags:persistent_config_feature_enabled=False
        --@score_logging//score/datarouter/build_configuration_flags:enable_nonverbose_dlt=False
        --@score_logging//score/datarouter/build_configuration_flags:enable_dynamic_configuration_in_datarouter=False
        --@score_logging//score/datarouter/build_configuration_flags:dlt_file_transfer_feature=False
        --@score_logging//score/datarouter/build_configuration_flags:use_local_vlan=True""",
}


def load_modules(known_good_path: Path) -> Dict[str, Module]:
    """Load modules from known_good.json file.
    
    Args:
        known_good_path: Path to known_good.json file
        
    Returns:
        Dictionary mapping module names to Module instances
    """
    if not known_good_path.exists():
        return {}
    
    with open(known_good_path, 'r') as f:
        data = json.load(f)
    
    modules_dict = data.get('modules', {})
    modules = Module.parse_modules(modules_dict)
    
    return {m.name: m for m in modules}


def get_module_version_gh(repo_url: str, commit_hash: str) -> Optional[str]:
    """Get version tag from GitHub API for a commit hash.
    
    Args:
        repo_url: GitHub repository URL
        commit_hash: Commit hash to look up
        
    Returns:
        Tag name if found, None otherwise
    """
    # Check if gh CLI is installed
    if not subprocess.run(['which', 'gh'], capture_output=True).returncode == 0:
        print("::warning::gh CLI not found. Install it to resolve commit hashes to tags.")
        return None
    
    # Extract owner/repo from GitHub URL
    match = re.search(r'github\.com[/:]([^/]+)/([^/.]+)(\.git)?$', repo_url)
    if not match:
        print(f"::warning::Invalid repo URL format: {repo_url}")
        return None
    
    owner, repo = match.group(1), match.group(2)
    
    print(f"::debug::Querying GitHub API: repos/{owner}/{repo}/tags for commit {commit_hash}")
    
    try:
        result = subprocess.run(
            ['gh', 'api', f'repos/{owner}/{repo}/tags', '--jq', 
             f'.[] | select(.commit.sha == "{commit_hash}") | .name'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            tag = result.stdout.strip().split('\n')[0]
            print(f"::debug::Found tag: {tag}")
            return tag
        
        print(f"::debug::No tag found for commit {commit_hash}")
        return None
    except Exception as e:
        print(f"::warning::Error querying GitHub API: {e}")
        return None


def truncate_hash(hash_str: str, length: int = 8) -> str:
    """Truncate hash to specified length.
    
    Args:
        hash_str: Full hash string
        length: Maximum length
        
    Returns:
        Truncated hash
    """
    if len(hash_str) > length:
        return hash_str[:length]
    return hash_str


def count_pattern(log_file: Path, pattern: str) -> int:
    """Count lines matching pattern in log file.
    
    Args:
        log_file: Path to log file
        pattern: Pattern to search for (case-insensitive)
        
    Returns:
        Number of matching lines found
    """
    if not log_file.exists():
        return 0
    
    count = 0
    with open(log_file, 'r') as f:
        for line in f:
            if pattern in line.lower():
                count += 1
    return count


def get_identifier_and_link(module: Optional[Module]) -> Tuple[Optional[str], str]:
    """Get display identifier and link for a module.
    
    Args:
        module: Module instance or None
        
    Returns:
        Tuple of (identifier, link_url)
    """
    if not module or not module.hash:
        return None, ""
    
    if module.version:
        identifier = module.version
        link = f"{module.repo}/releases/tag/{module.version}" if module.repo else ""
    else:
        # Try to get version from GitHub
        if module.repo:
            gh_version = get_module_version_gh(module.repo, module.hash)
            if gh_version:
                identifier = gh_version
                link = f"{module.repo}/releases/tag/{gh_version}"
            else:
                identifier = truncate_hash(module.hash)
                link = f"{module.repo}/tree/{module.hash}"
        else:
            identifier = truncate_hash(module.hash)
            link = ""
    
    return identifier, link


def build_group(group_name: str, targets: str, config: str, log_file: Path) -> Tuple[int, int]:
    """Build a group of Bazel targets.
    
    Args:
        group_name: Name of the build group
        targets: Bazel targets to build
        config: Bazel config to use
        log_file: Path to log file
        
    Returns:
        Tuple of (exit_code, duration_seconds)
    """
    print(f"--- Building group: {group_name} ---")
    
    # Build command
    cmd = ['bazel', 'build', '--verbose_failures', f'--config={config}'] + targets.split()
    #cmd = ['ls'] # for testing purposes only, remove on PR

    print(f"bazel build --verbose_failures --config {config} {targets}")
    print(f"::group::Bazel build ({group_name})")
    
    start_time = time.time()
    
    # Run build and capture output
    with open(log_file, 'w') as f:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Stream output to both terminal and file
        if process.stdout:
            for line in process.stdout:
                print(line, end='')
                f.write(line)
        
        process.wait()
    
    end_time = time.time()
    duration = int(end_time - start_time)
    
    print("::endgroup::")
    
    return process.returncode, duration


def format_commit_version_cell(
    group_name: str,
    old_modules: Dict[str, Module],
    new_modules: Dict[str, Module]
) -> str:
    """Format the commit/version cell for the summary table.
    
    Args:
        group_name: Name of the module group
        old_modules: Modules from old known_good.json
        new_modules: Modules from new known_good.json
        
    Returns:
        Formatted markdown cell content
    """
    # Get module info or defaults
    old_module = old_modules.get(group_name)
    new_module = new_modules.get(group_name)
    
    if new_module is None or new_module.hash is None:
        return "N/A"
    
    print(f"::debug::Module={group_name}, old_version={old_module.version if old_module else 'None'}, "
          f"old_hash={old_module.hash if old_module else 'None'}, "
          f"new_version={new_module.version}, "
          f"new_hash={new_module.hash}, "
          f"repo={new_module.repo}")
    
    # Get identifiers and links
    old_identifier, old_link = get_identifier_and_link(old_module)
    
    # Check if hash changed
    hash_changed = old_module is None or old_module.hash != new_module.hash
    
    # Determine new identifier only if hash changed
    new_identifier, new_link = (None, "") if not hash_changed else get_identifier_and_link(new_module)
    
    # Format output
    if hash_changed:
        # Hash changed - show old -> new
        if new_module.repo and old_module and old_link and new_link and old_module.hash and new_identifier:
            return f"[{old_identifier}]({old_link}) → [{new_identifier}]({new_link}) ([diff]({new_module.repo}/compare/{old_module.hash}...{new_module.hash}))"
        elif new_module.repo and new_link and new_identifier:
            return f"{old_identifier} → [{new_identifier}]({new_link})"
        elif new_identifier:
            return f"{old_identifier} → {new_identifier}"
        else:
            return "N/A"
    elif old_identifier:
        # Hash not changed - show only old
        if old_link:
            return f"[{old_identifier}]({old_link})"
        else:
            return old_identifier
    else:
        return "N/A"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Integration build script for SCORE modules',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--known-good',
        type=Path,
        help='Path to known_good.json file'
    )
    parser.add_argument(
        '--config',
        default=os.environ.get('CONFIG', 'bl-x86_64-linux'),
        help='Bazel config to use (default: bl-x86_64-linux, or from CONFIG env var)'
    )
    
    args = parser.parse_args()
    
    # Configuration
    config = args.config
    log_dir = Path(os.environ.get('LOG_DIR', '_logs/logs'))
    summary_file = Path(os.environ.get('SUMMARY_FILE', '_logs/build_summary.md'))
    
    known_good_file = args.known_good
    if not known_good_file and Path('known_good.json').exists():
        known_good_file = Path('known_good.json')
    
    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load modules from known_good files
    old_modules = load_modules(Path('known_good.json')) if Path('known_good.json').exists() else {}
    new_modules = load_modules(known_good_file) if known_good_file else {}
    
    # Start summary
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(summary_file, 'w') as f:
        f.write(f"=== Integration Build Started {timestamp} ===\n")
        f.write(f"Config: {config}\n")
        if known_good_file:
            f.write(f"Known Good File: {known_good_file}\n")
        f.write("\n")
        f.write("## Build Groups Summary\n")
        f.write("\n")
        f.write("| Group | Status | Duration (s) | Warnings | Deprecated refs | Commit/Version |\n")
        f.write("|-------|--------|--------------|----------|-----------------|----------------|\n")
    
    print(f"=== Integration Build Started {timestamp} ===")
    print(f"Config: {config}")
    if known_good_file:
        print(f"Known Good File: {known_good_file}")
    
    overall_warn_total = 0
    overall_depr_total = 0
    any_failed = False
    
    # Build each group
    for group_name, targets in BUILD_TARGET_GROUPS.items():
        log_file = log_dir / f"{group_name}.log"
        
        exit_code, duration = build_group(group_name, targets, config, log_file)
        
        if exit_code != 0:
            any_failed = True
        
        # Count warnings and deprecated
        warn_count = count_pattern(log_file, 'warning:')
        depr_count = count_pattern(log_file, 'deprecated')
        overall_warn_total += warn_count
        overall_depr_total += depr_count
        
        # Format status
        status_symbol = "✅" if exit_code == 0 else f"❌({exit_code})"
        
        # Format commit/version cell
        commit_version_cell = format_commit_version_cell(group_name, old_modules, new_modules)
        
        # Append row to summary
        row = f"| {group_name} | {status_symbol} | {duration} | {warn_count} | {depr_count} | {commit_version_cell} |\n"
        with open(summary_file, 'a') as f:
            f.write(row)
        print(row.strip())
    
    # Append totals
    with open(summary_file, 'a') as f:
        f.write(f"| TOTAL |  |  | {overall_warn_total} | {overall_depr_total} |  |\n")
    
    # Print summary
    print('::group::Build Summary')
    print('=== Build Summary ===')
    with open(summary_file, 'r') as f:
        for line in f:
            print(line, end='')
    print('::endgroup::')
    
    # Exit with error if any build failed
    if any_failed:
        print("::error::One or more build groups failed. See summary above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
