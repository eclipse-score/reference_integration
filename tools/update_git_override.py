#!/usr/bin/env python3
"""Update a commit hash of a git_override stanza in a Bazel MODULE.bazel file.

!!! Temporary Script !!!

Usage:
    ./tools/update_git_override.py REMOTE@HASH [REMOTE@HASH ...] [--file MODULE.bazel]

Examples:
    ./tools/update_git_override.py https://github.com/eclipse-score/baselibs.git@deadbeef123...
    ./tools/update_git_override.py \
            https://github.com/eclipse-score/baselibs.git@deadbeef123... \
            https://github.com/eclipse-score/tooling.git@cafebabefeedface0123...

Behavior:
    - For each REMOTE@HASH argument, finds the git_override( ... ) block whose remote matches REMOTE.
    - Updates (or inserts if missing) the commit = "HASH" attribute inside that block.
    - Preserves indentation and other attributes.
    - If any remote is not found, exits with non-zero status and does not write changes (except still shows diff in --dry-run if partial matches occurred).

Limitations:
  - Does not validate that HASH exists in the remote repo.
  - Expects reasonably well-formed Starlark (one git_override per block).

"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

GIT_OVERRIDE_START_RE = re.compile(r"^\s*git_override\s*\(\s*$")
REMOTE_LINE_RE = re.compile(r"^\s*remote\s*=\s*\"(?P<remote>[^\"]+)\"\s*,?\s*$")
COMMIT_LINE_RE = re.compile(r"^\s*commit\s*=\s*\"(?P<commit>[0-9a-fA-F]+)\"\s*,?\s*$")

# Simple state machine to collect a git_override block

def parse_args():
    p = argparse.ArgumentParser(description="Update commit hash(es) for git_override remote(s)")
    p.add_argument("remote_and_hash", nargs="+", help="One or more REMOTE@HASH entries e.g. https://github.com/eclipse-score/baselibs.git@abc123...")
    p.add_argument("--file", default="MODULE.bazel", help="Path to MODULE.bazel (default: MODULE.bazel)")
    p.add_argument("--dry-run", action="store_true", help="Show diff without writing")
    return p.parse_args()


def main():
    args = parse_args()
    # Parse all remote@hash pairs
    targets = []
    for item in args.remote_and_hash:
        if "@" not in item:
            print(f"ERROR: argument must be REMOTE@HASH (got: {item})", file=sys.stderr)
            return 2
        remote, new_hash = item.split("@", 1)
        targets.append((remote, new_hash))
    module_path = Path(args.file)
    if not module_path.exists():
        print(f"ERROR: file not found: {module_path}", file=sys.stderr)
        return 2

    lines = module_path.read_text().splitlines()

    # Track which remotes were updated
    requested_remotes = {r for r, _ in targets}
    updated_remotes = set()
    updated_any = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if GIT_OVERRIDE_START_RE.match(line):
            # capture block
            block_start = i
            i += 1
            # find end: a line with a lone ')'
            while i < len(lines) and not lines[i].strip().startswith(")"):
                i += 1
            block_end = i  # index of line with ')' or end
            block = lines[block_start:block_end+1]

            # Determine if this block matches the remote
            found_remote = None
            commit_idx = None
            remote_idx = None
            for j, bline in enumerate(block):
                m_remote = REMOTE_LINE_RE.match(bline)
                if m_remote:
                    found_remote = m_remote.group("remote")
                    remote_idx = j
                m_commit = COMMIT_LINE_RE.match(bline)
                if m_commit:
                    commit_idx = j
            if found_remote and found_remote in requested_remotes:
                # Determine target hash for this remote
                new_hash = next(h for (r, h) in targets if r == found_remote)
                if len(block) > 1:
                    m_indent = re.match(r"^(\s*)", block[1])
                    indent = m_indent.group(1) if m_indent else "    "
                else:
                    indent = "    "
                # Prepare new commit line
                new_commit_line = f"{indent}commit = \"{new_hash}\"," if not block[block_end-block_start].strip().startswith(")") else f"{indent}commit = \"{new_hash}\","  # fallback
                if commit_idx is not None:
                    old = block[commit_idx]
                    block[commit_idx] = re.sub(COMMIT_LINE_RE, new_commit_line, old)
                else:
                    # Insert commit after remote line if available else before closing paren
                    insert_pos = commit_idx or (remote_idx + 1 if remote_idx is not None else len(block)-1)
                    block.insert(insert_pos, new_commit_line)
                    block_end += 1
                # Replace into lines
                lines[block_start:block_end+1] = block
                updated_any = True
                updated_remotes.add(found_remote)
                # continue search (in case multiple matching blocks?) but typically one
        i += 1

    missing = requested_remotes - updated_remotes
    if missing:
        print("ERROR: remote(s) not found: " + ", ".join(sorted(missing)), file=sys.stderr)
        if not updated_any:
            return 1
        # If some were updated and some missing, still allow diff/write decision below, but exit non-zero.
        exit_code_on_missing = 1
    else:
        exit_code_on_missing = 0

    new_content = "\n".join(lines) + "\n"
    if args.dry_run:
        old_content = module_path.read_text()
        if old_content == new_content:
            print("No changes.")
            return exit_code_on_missing
        # rudimentary diff
        import difflib
        diff = difflib.unified_diff(old_content.splitlines(), new_content.splitlines(), fromfile=str(module_path), tofile=str(module_path)+" (updated)")
        for dline in diff:
            print(dline)
        return exit_code_on_missing

    module_path.write_text(new_content)
    if updated_remotes:
        for r in sorted(updated_remotes):
            print(f"Updated commit for remote {r}")
    return exit_code_on_missing

if __name__ == "__main__":
    raise SystemExit(main())
