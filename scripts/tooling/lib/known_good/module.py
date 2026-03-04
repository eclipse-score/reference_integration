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
"""Module dataclass for score reference integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List
from urllib.parse import urlparse


@dataclass
class Metadata:
    """Metadata configuration for a module."""

    code_root_path: str = "//score/..."
    extra_test_config: list[str] = field(default_factory=list)
    exclude_test_targets: list[str] = field(default_factory=list)
    langs: list[str] = field(default_factory=lambda: ["cpp", "rust"])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Metadata:
        return cls(
            code_root_path=data.get("code_root_path", "//score/..."),
            extra_test_config=data.get("extra_test_config", []),
            exclude_test_targets=data.get("exclude_test_targets", []),
            langs=data.get("langs", ["cpp", "rust"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code_root_path": self.code_root_path,
            "extra_test_config": self.extra_test_config,
            "exclude_test_targets": self.exclude_test_targets,
            "langs": self.langs,
        }


@dataclass
class Module:
    """A single known-good module entry."""

    name: str
    hash: str
    repo: str
    version: str | None = None
    bazel_patches: list[str] | None = None
    metadata: Metadata = field(default_factory=Metadata)
    branch: str = "main"
    pin_version: bool = False

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> Module:
        repo = data.get("repo", "")
        commit_hash = data.get("hash") or data.get("commit", "")
        version = data.get("version")

        if commit_hash and version:
            raise ValueError(
                f"Module '{name}' has both 'hash' and 'version' set. "
                "Use either 'hash' (git_override) or 'version' (single_version_override), not both."
            )

        bazel_patches = data.get("bazel_patches") or data.get("patches", [])

        metadata_data = data.get("metadata")
        metadata = Metadata.from_dict(metadata_data) if metadata_data is not None else Metadata()

        return cls(
            name=name,
            hash=commit_hash,
            repo=repo,
            version=version,
            bazel_patches=bazel_patches if bazel_patches else None,
            metadata=metadata,
            branch=data.get("branch", "main"),
            pin_version=data.get("pin_version", False),
        )

    @classmethod
    def parse_modules(cls, modules_dict: Dict[str, Any]) -> List[Module]:
        modules = []
        for name, module_data in modules_dict.items():
            module = cls.from_dict(name, module_data)
            if not module.repo and not module.version:
                logging.warning("Skipping module %s with missing repo", name)
                continue
            modules.append(module)
        return modules

    @property
    def owner_repo(self) -> str:
        """Return 'owner/repo' extracted from a GitHub HTTPS URL."""
        parsed = urlparse(self.repo)
        if parsed.netloc != "github.com":
            raise ValueError(f"Not a GitHub URL: {self.repo}")
        path = parsed.path.lstrip("/").removesuffix(".git")
        parts = path.split("/", 2)
        if len(parts) != 2:
            raise ValueError(f"Cannot parse owner/repo from: {self.repo}")
        return f"{parts[0]}/{parts[1]}"

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"repo": self.repo}
        if self.version:
            result["version"] = self.version
        else:
            result["hash"] = self.hash
        result["metadata"] = self.metadata.to_dict()
        if self.bazel_patches:
            result["bazel_patches"] = self.bazel_patches
        if self.branch and self.branch != "main":
            result["branch"] = self.branch
        if self.pin_version:
            result["pin_version"] = True
        return result
