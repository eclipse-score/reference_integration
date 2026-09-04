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
"""Apply the module-under-test's own ``bazel_patches`` to its Stage-2 checkout.

Distinct from the patch transport in ``ResolvedDependencies.overwrite``, which hands a
*dependency's* patches to Bazel by label. The module under test is the root and is never
fetched, so its own patches are applied here directly, by filesystem path.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.module import Module

# ``//patches/<dir>:<file>``; known_good.json also carries bare paths, so both are accepted.
_LABEL_RE = re.compile(r"^//(?P<pkg>[^:]+):(?P<name>.+)$")

# Matches the patch_strip emitted with these same patches in Stage-1 override directives.
PATCH_STRIP = 1


class ModulePatchError(RuntimeError):
    """A declared patch could not be resolved or applied.

    Always a ref_int defect: ref_int's recorded patch no longer matches the commit it is
    declared against.
    """


def patch_relpath(patch: str) -> Path:
    """Map one ``bazel_patches`` entry (``//patches/x:y.patch`` or a bare path) to a workspace path."""
    match = _LABEL_RE.match(patch)
    relative = Path(match.group("pkg")) / match.group("name") if match else Path(patch)
    if relative.is_absolute():
        raise ModulePatchError(f"patch entry must be workspace-relative, got absolute path: {patch!r}")
    return relative


def resolve_patch_path(patch: str, ref_int_root: Path) -> Path:
    """Map one ``bazel_patches`` entry to an existing file in ref_int's tree."""
    relative = patch_relpath(patch)
    resolved = (ref_int_root / relative).resolve()
    if not resolved.is_file():
        raise ModulePatchError(f"declared patch {patch!r} does not exist at {resolved}")
    return resolved


def _git_apply(workspace: Path, patch_file: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(workspace), "apply", f"-p{PATCH_STRIP}", *extra, str(patch_file)],
        capture_output=True,
        text=True,
        check=False,
    )


def apply_module_patches(
    module: Module,
    workspace: Path,
    ref_int_root: Path,
    log=print,
) -> list[str]:
    """Apply ``module``'s declared patches to ``workspace`` in declaration order.

    Returns the newly applied entries; already-applied ones are reported and skipped. Raises
    :class:`ModulePatchError` on the first entry that neither applies nor is already applied —
    silently testing an unpatched checkout is the bug this step exists to fix.
    """
    if not module.bazel_patches:
        log(f"QR: {module.name} declares no bazel_patches; checkout is used as-is")
        return []

    applied: list[str] = []
    for patch in module.bazel_patches:
        patch_file = resolve_patch_path(patch, ref_int_root)

        # Idempotency for local re-runs (ci_local.sh reuses _module/); fresh CI never hits it.
        if _git_apply(workspace, patch_file, "--reverse", "--check").returncode == 0:
            log(f"QR: {patch} already applied to {workspace}; skipping")
            continue

        dry_run = _git_apply(workspace, patch_file, "--check")
        if dry_run.returncode != 0:
            raise ModulePatchError(
                f"ref_int harness defect: patch {patch} does not apply to {module.name} "
                f"at commit {module.hash}, and is not already applied.\n"
                f"git apply --check said:\n{dry_run.stderr.strip()}"
            )

        result = _git_apply(workspace, patch_file)
        if result.returncode != 0:
            raise ModulePatchError(
                f"ref_int harness defect: patch {patch} passed --check but failed to apply to "
                f"{module.name}.\ngit apply said:\n{result.stderr.strip()}"
            )
        log(f"QR: applied {patch} to {workspace}")
        applied.append(patch)

    return applied
