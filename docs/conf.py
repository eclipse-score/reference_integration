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

exclude_patterns = [
    # The following entries are not required when building the documentation via 'bazel
    # build //:docs', as that command runs in a sandboxed environment. However, when
    # building the documentation via 'bazel run //:docs' or esbonio, these
    # entries are required to prevent the build from failing.
    "**/CONTRIBUTION.md",
    "**/README.md",
    "**/.github/**",
    "**/improvement.md",
    "bazel-*",
    ".venv*",
    "_build",
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
        "s_core_v_1/releases/progress_overview": [],
    },
    "show_toc_level": 2,
    "navigation_with_keys": False,
    # Show every top-level section in the header instead of folding some into "More".
    "header_links_before_dropdown": 100,
}

# score_logging v0.2.5 symlinks design docs/PlantUML files from score/ into docs/,
# which sphinx-mounts reports as path_escape. Remove once its bundle is self-contained.
_PATH_CHECK_OFF = {"modules/score_logging"}


def _relax_path_check(_app, config) -> None:
    for mount in getattr(config, "mounts", None) or []:
        if isinstance(mount, dict) and mount.get("mount_at") in _PATH_CHECK_OFF:
            mount["path_check"] = "off"


# Navigation labels for the mounted module docs, so the Modules list, the section navigation
# and prev/next links use plain module names instead of each module's own page title.
_MODULE_NAV_TITLES = {
    "modules/score_baselibs/index": "Base Libraries",
    "modules/score_persistency/index": "Persistency",
    "modules/score_kyron/index": "Kyron",
    "modules/score_lifecycle/index": "Lifecycle",
    "modules/score_logging/index": "Logging",
    "modules/score_time/index": "Time",
    "modules/score_itf/index": "Integration Test Framework",
    "modules/score_platform/index": "Platform",
    "modules/score_docs_as_code/index": "Docs-as-Code",
    "modules/score_process_description/index": "Process Description",
}


def _apply_module_nav_title(app, _doctree) -> None:
    from docutils import nodes

    docname = app.env.current_document.docname
    title = _MODULE_NAV_TITLES.get(docname)
    if title is None:
        return
    # A new node, so env.longtitles (the HTML <title>) keeps the page's own title.
    app.env.titles[docname] = nodes.title(title, title)
    first_entry = next(app.env.tocs[docname].findall(nodes.reference), None)
    if first_entry is not None:
        first_entry.children[:] = [nodes.Text(title)]


# Defined here, not as a docs/*.py extension: the sandboxed needs_json build only ships conf.py.
def setup(app):
    # After score_mounts (300) has filled config.mounts, before sphinx_mounts (400) reads it.
    app.connect("config-inited", _relax_path_check, priority=350)
    # After Sphinx's title and toctree collectors (500) have recorded the page title.
    app.connect("doctree-read", _apply_module_nav_title, priority=600)
