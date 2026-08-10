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
"""Which Bazel release a Stage-2 module checkout is built with.

Stage 2 runs each module as the Bazel root in its own checkout, so that checkout's
``.bazelversion`` decides which Bazel binary bazelisk launches. ref_int imposes a floor on it,
not an exact version -- see :func:`resolve_stage2_bazel_version`.
"""

from __future__ import annotations

import re

# A plain dotted release, e.g. "8.6.0". Anything else -- "last_green", "latest", "8.4.0rc3",
# a fork's "8.4.2-score" -- has no meaningful order against ref_int's, so it is left alone
# rather than guessed at.
_RELEASE_RE = re.compile(r"\d+(?:\.\d+)*")


def _order(version: str) -> tuple[int, ...] | None:
    """The comparable form of a release string, or None if it is not a plain dotted release."""
    return tuple(int(part) for part in version.split(".")) if _RELEASE_RE.fullmatch(version) else None


def resolve_stage2_bazel_version(ref_int_version: str, module_version: str | None) -> str:
    """Return the Bazel release Stage 2 should build a module checkout with.

    ref_int's release is a floor, not a ceiling: a module pinning an older Bazel is raised so
    ``ci/stage2/module.bazelrc`` is never read by a Bazel older than it was written against, but a
    module pinning a newer one keeps it. Forcing a module *down* changes bzlmod resolution
    semantics, so its failures stop being reproducible by the team that owns it. Measured:
    ``score_baselibs`` resolves cleanly under the 8.6.0 it pins and fails under 8.4.2 with
    ``score_docs_as_code@4.6.0 depends on score_process@1.6.0 with compatibility level 1, but
    <root> depends on score_process@2.0.0 with compatibility level 2``. Both are the module's own
    dev dependencies, so no pin-scope change can reach it. Six of the eight ``target_sw`` modules
    pin newer than ref_int, so downgrading is the common case, not an outlier.

    No ``.bazelversion`` gets ref_int's. One that is not a plain dotted release cannot be ordered,
    so it is left as written -- the floor cannot be established, and the module's own value at
    least preserves its semantics.
    """
    if module_version is None:
        return ref_int_version
    module_order, ref_int_order = _order(module_version), _order(ref_int_version)
    if module_order is None or ref_int_order is None:
        return module_version
    return module_version if module_order > ref_int_order else ref_int_version
