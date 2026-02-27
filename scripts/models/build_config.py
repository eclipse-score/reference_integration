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
"""Build configuration management for SCORE modules."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class BuildModuleConfig:
    """Configuration for a build module."""

    name: str
    build_targets: str
    test_targets: Optional[str] = None


def load_build_config(config_path: Path) -> Dict[str, BuildModuleConfig]:
    """Load build configuration from JSON file.

    Args:
        config_path: Path to build_config.json file

    Returns:
        Dictionary mapping module names to BuildModuleConfig instances
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Build config file not found: {config_path}")

    with open(config_path, "r") as f:
        data = json.load(f)

    modules = data.get("modules", {})
    return {
        name: BuildModuleConfig(
            name=name, build_targets=module_data.get("build_targets", ""), test_targets=module_data.get("test_targets")
        )
        for name, module_data in modules.items()
    }
