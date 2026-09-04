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
    """Metadata configuration for a module.

    Attributes:
            code_root_path: Root path to the code directory
            extra_test_config: List of extra test configuration flags
            exclude_test_targets: List of test targets to exclude
            exclude_test_target_reasons: Why each excluded target is excluded, keyed by
                    the label as it appears in exclude_test_targets. Every exclusion needs
                    one: without it nobody can tell a scope-independent exclusion (a
                    benchmark, a sanitizer target) from a stale workaround for a build
                    scope that no longer exists.
            legacy_exclude_test_targets: central-mode-only exclusions. Predate the audit, so
                    exempt from the wildcard and reason checks; deleted with that runner.
            langs: List of languages supported (e.g., ["cpp", "rust"])
    """

    code_root_path: str = "//score/..."
    extra_test_config: list[str] = field(default_factory=lambda: [])
    exclude_test_targets: list[str] = field(default_factory=lambda: [])
    exclude_test_target_reasons: dict[str, str] = field(default_factory=lambda: {})
    legacy_exclude_test_targets: list[str] = field(default_factory=lambda: [])
    langs: list[str] = field(default_factory=lambda: ["cpp", "rust"])
    rust_coverage_config: str | None = "ferrocene-coverage"
    bazel_config: list[str] = field(default_factory=lambda: [])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Metadata:
        """Create a Metadata instance from a dictionary.

        Args:
                data: Dictionary containing metadata configuration

        Returns:
                Metadata instance
        """
        return cls(
            code_root_path=data.get("code_root_path", "//score/..."),
            extra_test_config=data.get("extra_test_config", []),
            exclude_test_targets=data.get("exclude_test_targets", []),
            exclude_test_target_reasons=data.get("exclude_test_target_reasons", {}),
            legacy_exclude_test_targets=data.get("legacy_exclude_test_targets", []),
            langs=data.get("langs", ["cpp", "rust"]),
            rust_coverage_config=data.get("rust_coverage_config", "ferrocene-coverage"),
            bazel_config=data.get("bazel_config", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Metadata instance to dictionary representation.

        Returns:
                Dictionary with metadata configuration
        """
        return {
            "code_root_path": self.code_root_path,
            "extra_test_config": self.extra_test_config,
            "exclude_test_targets": self.exclude_test_targets,
            "exclude_test_target_reasons": self.exclude_test_target_reasons,
            "legacy_exclude_test_targets": self.legacy_exclude_test_targets,
            "langs": self.langs,
            "rust_coverage_config": self.rust_coverage_config,
            "bazel_config": self.bazel_config,
        }


@dataclass
class Module:
    name: str
    hash: str
    repo: str
    version: str | None = None
    bazel_patches: list[str] | None = None
    metadata: Metadata = field(default_factory=Metadata)
    branch: str = "main"
    pin_version: bool = False

    @classmethod
    def from_dict(cls, name: str, module_data: Dict[str, Any]) -> Module:
        """Create a Module instance from a dictionary representation.

        Args:
                name: The module name
                module_data: Dictionary containing module configuration with keys:
                        - repo (str): Repository URL
                        - hash or commit (str): Commit hash
                        - version (str, optional): Module version (when present, hash is ignored)
                        - bazel_patches (list[str], optional): List of patch files for Bazel
                        - metadata (dict, optional): Metadata configuration
                                Example: {
                                        "code_root_path": "path/to/code/root",
                                        "extra_test_config": [""],
                                        "exclude_test_targets": [""],
                                        "exclude_test_target_reasons": {"": ""},
                                        "langs": ["cpp", "rust"]
                                }
                                If not present, uses default Metadata values.
                        - branch (str, optional): Git branch name (default: main)
                        - pin_version (bool, optional): If true, module hash is not updated
                                            to latest HEAD by update scripts (default: false)

        Returns:
                Module instance
        """
        repo = module_data.get("repo", "")
        # Support both 'hash' and 'commit' keys
        commit_hash = module_data.get("hash") or module_data.get("commit", "")
        version = module_data.get("version")

        if commit_hash and version:
            raise ValueError(
                f"Module '{name}' has both 'hash' and 'version' set. "
                "Use either 'hash' (git_override) or 'version' (single_version_override), not both."
            )
        # Support both 'bazel_patches' and legacy 'patches' keys
        bazel_patches = module_data.get("bazel_patches") or module_data.get("patches", [])

        # Parse metadata - if not present or is None/empty dict, use defaults
        metadata_data = module_data.get("metadata")
        if metadata_data is not None:
            metadata = Metadata.from_dict(metadata_data)
            # A wildcard hides how much it excludes: '//score/json/examples:*' silently grows with
            # every target added to that package, so the report cannot say what was skipped. The
            # last two were dropped by the Stage-2 exclusion audit, so this can enforce now.
            wildcards = [target for target in metadata.exclude_test_targets if "*" in target]
            if wildcards:
                raise ValueError(
                    f"Module '{name}' has wildcard exclude_test_targets: {wildcards}. "
                    "List explicit test targets instead, so the excluded set cannot grow unnoticed."
                )
            # Stage 2 runs each module as the Bazel root, which retired the blanket
            # "invisible dev_dependency" justification. Every exclusion states its own reason.
            unexplained = [
                target
                for target in metadata.exclude_test_targets
                if not metadata.exclude_test_target_reasons.get(target, "").strip()
            ]
            if unexplained:
                raise ValueError(
                    f"Module '{name}' excludes test targets with no recorded reason: {unexplained}. "
                    "Add metadata.exclude_test_target_reasons[<label>] explaining why it cannot run."
                )
        else:
            # If metadata key is missing, create with defaults
            metadata = Metadata()

        branch = module_data.get("branch", "main")
        pin_version = module_data.get("pin_version", False)

        return cls(
            name=name,
            hash=commit_hash,
            repo=repo,
            version=version,
            bazel_patches=bazel_patches if bazel_patches else None,
            metadata=metadata,
            branch=branch,
            pin_version=pin_version,
        )

    @classmethod
    def parse_modules(cls, modules_dict: Dict[str, Any]) -> List[Module]:
        """Parse modules dictionary into Module dataclass instances.

        Args:
                modules_dict: Dictionary mapping module names to their configuration data

        Returns:
                List of Module instances, skipping invalid modules
        """
        modules = []
        for name, module_data in modules_dict.items():
            module = cls.from_dict(name, module_data)

            # Skip modules with missing repo and no version
            if not module.repo and not module.version:
                logging.warning("Skipping module %s with missing repo", name)
                continue

            modules.append(module)

        return modules

    @property
    def owner_repo(self) -> str:
        """Return owner/repo part extracted from HTTPS GitHub URL."""
        # Examples:
        # https://github.com/eclipse-score/logging.git -> eclipse-score/logging
        parsed = urlparse(self.repo)
        if parsed.netloc != "github.com":
            raise ValueError(f"Not a GitHub URL: {self.repo}")

        # Extract path, remove leading slash and .git suffix
        path = parsed.path.lstrip("/").removesuffix(".git")

        # Split and validate owner/repo format
        parts = path.split("/", 2)  # Split max 2 times to get owner and repo
        if len(parts) != 2:
            raise ValueError(f"Cannot parse owner/repo from: {self.repo}")

        return f"{parts[0]}/{parts[1]}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert Module instance to dictionary representation for JSON output.

        Returns:
                Dictionary with module configuration
        """
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
