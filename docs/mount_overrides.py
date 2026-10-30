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
"""Relax sphinx-mounts' path check for module bundles that are not self-contained yet."""

from sphinx.application import Sphinx
from sphinx.config import Config

# score_logging v0.2.5 symlinks design docs/PlantUML files from score/ into docs/.
PATH_CHECK_OFF = {"modules/score_logging"}


def _relax_path_check(_app: Sphinx, config: Config) -> None:
    for mount in getattr(config, "mounts", None) or []:
        if isinstance(mount, dict) and mount.get("mount_at") in PATH_CHECK_OFF:
            mount["path_check"] = "off"


def setup(app: Sphinx) -> dict[str, object]:
    # After score_mounts (300) has filled config.mounts, before sphinx_mounts (400) reads it.
    app.connect("config-inited", _relax_path_check, priority=350)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
