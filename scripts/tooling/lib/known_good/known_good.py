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
"""KnownGood model and loader for score reference integration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from .module import Module


@dataclass
class KnownGood:
    """Parsed contents of known_good.json.

    modules: {"group_name": {"module_name": Module, ...}, ...}
    """

    modules: Dict[str, Dict[str, Module]]
    timestamp: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> KnownGood:
        parsed: Dict[str, Dict[str, Module]] = {}
        for group_name, group_modules in data.get("modules", {}).items():
            if isinstance(group_modules, dict):
                parsed[group_name] = {m.name: m for m in Module.parse_modules(group_modules)}
        return cls(modules=parsed, timestamp=data.get("timestamp", ""))


def load_known_good(path: Path) -> KnownGood:
    """Parse known_good.json at *path* and return a typed :class:`KnownGood`.

    Args:
        path: Path to the known_good.json file.

    Returns:
        Fully-typed KnownGood instance.

    Raises:
        ValueError: On malformed JSON or unexpected top-level structure.
        FileNotFoundError: If *path* does not exist.
    """
    text = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        lines = text.splitlines()
        line = lines[e.lineno - 1] if 0 <= e.lineno - 1 < len(lines) else ""
        pointer = " " * (e.colno - 1) + "^"
        hint = "Possible causes: trailing comma, missing value, or extra comma." if "Expecting value" in e.msg else ""
        raise ValueError(
            f"Invalid JSON at line {e.lineno}, column {e.colno}\n{line}\n{pointer}\n{e.msg}. {hint}"
        ) from None

    if not isinstance(data, dict) or not isinstance(data.get("modules"), dict):
        raise ValueError(f"Invalid known_good.json at {path}: expected object with 'modules' dict")

    return KnownGood.from_dict(data)
