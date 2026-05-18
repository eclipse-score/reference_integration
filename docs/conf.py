# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
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

# Configuration file for the Sphinx documentation builder.

import os as _os
import sys as _sys

# Make docs/ importable so needs_filters.py (and similar helpers) can be used
# as :filter-func: targets in sphinx-needs directives.
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))


def _patch_needpie_suppress_legend() -> None:
    """Suppress all in-chart legends in sphinx-needs needpie charts."""
    try:
        import matplotlib.axes

        matplotlib.axes.Axes.legend = lambda self, *args, **kwargs: None
    except Exception:
        pass


_patch_needpie_suppress_legend()

project = "REF_INT"
project_url = "https://eclipse-score.github.io/reference_integration"
version = "0.1"

extensions = [
    # TODO: remove plantuml here once
    # https://github.com/useblocks/sphinx-needs/pull/1508 is merged and docs-as-code
    # is updated with new sphinx-needs version
    "sphinxcontrib.plantuml",
    "score_sphinx_bundle",
]

# Enable markdown rendering
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Custom static assets (CSS, etc.)
html_static_path = ["_assets"]
html_css_files = ["custom.css"]


html_theme_options = {
    "secondary_sidebar_items": {
        "**": ["page-toc"],
        "feature_and_process_status": [],
        "s_core_v_1/roadmap/overall_status": [],
    },
    "show_toc_level": 2,
    "navigation_with_keys": False,
}
