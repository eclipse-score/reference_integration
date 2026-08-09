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

Stage 2 runs each module as the Bazel root inside its own checkout, so the ``.bazelversion``
in that checkout is what decides which Bazel binary bazelisk launches. ref_int rewrites that
file so the centralized ``ci/stage2/module.bazelrc`` is always read by a Bazel it is known to
work with -- but the version it writes is a **floor**, not an exact match. See
:func:`resolve_stage2_bazel_version` for why the difference is load-bearing.
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

    ref_int's release is a **floor**: a module pinning an older Bazel is raised to it, so the
    centralized ``ci/stage2/module.bazelrc`` is never read by a Bazel older than the one it was
    written against. That is the whole of what ref_int needs, and it is deliberately **not** a
    ceiling.

    Forcing a module *down* to ref_int's release changes bzlmod resolution semantics, which is
    precisely the "built with semantics different from its own CI" that
    ``ci/stage2/README.md``'s criterion 5 forbids. This is measured, not theoretical:
    ``score_baselibs`` at its known_good pin resolves cleanly under the 8.6.0 it pins itself and
    fails outright under ref_int's 8.4.2, with

        score_docs_as_code@4.6.0 depends on score_process@1.6.0 with compatibility level 1, but
        <root> depends on score_process@2.0.0 with compatibility level 2 which is different

    The check itself is unchanged between the two releases -- its message and throw site are
    byte-identical in ``Selection.java`` at both tags -- so what differs is the selection that
    precedes it; 8.6.0 walks the dep graph twice and prunes modules reachable only via nodep
    edges. Which specific change admits this graph has **not** been isolated, and the rule below
    does not depend on knowing. Both modules are the module's own ``dev_dependency``
    declarations, so no ref_int override is involved and no change to the pin scope can reach
    it. The run executes zero tests, which the README classifies as a ref_int harness defect.
    Six of the eight ``target_sw`` modules pin a Bazel newer than ref_int's, so being
    downgraded is the common case here, not an outlier.

    A module with no ``.bazelversion`` gets ref_int's. A module whose ``.bazelversion`` is not a
    plain dotted release cannot be ordered against ref_int's, so it is left as the module wrote
    it: the floor cannot be established, and keeping the module's own value at least keeps its
    semantics intact. If ref_int's rc then fails on that Bazel it fails loudly, which is the
    trade this area has already settled once (see the ``--noworkspace_rc`` note in the README).
    """
    if module_version is None:
        return ref_int_version
    module_order, ref_int_order = _order(module_version), _order(ref_int_version)
    if module_order is None or ref_int_order is None:
        return module_version
    return module_version if module_order > ref_int_order else ref_int_version
