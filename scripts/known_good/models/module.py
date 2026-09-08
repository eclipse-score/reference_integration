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
class Docs:
    """How a module's documentation bundle is mounted into the ref_int docs site.

    Every module is mounted by default: a module that calls docs-as-code's ``docs()``
    macro automatically exposes a public ``//:docs_bundle``, and the integration wants
    that documentation in the combined site. A module that does not expose one (it has
    no ``docs()`` call, or its root package cannot be loaded from ref_int's graph) must
    opt out with ``"docs": false``, otherwise the docs build fails on a missing target.

    Attributes:
            enabled: Whether the module's bundle is mounted (default: True).
            bundle: Bundle label. Defaults to ``@<module_name>//:docs_bundle``.
            mount_at: Site path to mount at. Defaults to ``<section>/<module_name>``,
                    where the section is derived from the module's known_good group.
            attach_to: Optional document to attach the bundle to; passed through to
                    ``docs()``, which defaults it to the mount_at parent's index.
    """

    enabled: bool = True
    bundle: str | None = None
    mount_at: str | None = None
    attach_to: str | None = None

    @classmethod
    def from_value(cls, value: Any) -> Docs:
        """Create a Docs instance from a known_good.json ``docs`` value.

        Accepts the key being absent (``None``), a bool, or a dict of overrides:
        ``{"bundle": ..., "mount_at": ..., "attach_to": ...}``.

        Args:
                value: Raw value of the module's ``docs`` key.

        Returns:
                Docs instance
        """
        if value is None or value is True:
            return cls()
        if value is False:
            return cls(enabled=False)
        if isinstance(value, dict):
            unknown = set(value) - {"bundle", "mount_at", "attach_to"}
            if unknown:
                raise ValueError(f"Unknown keys in 'docs': {', '.join(sorted(unknown))}")
            return cls(
                enabled=True,
                bundle=value.get("bundle"),
                mount_at=value.get("mount_at"),
                attach_to=value.get("attach_to"),
            )
        raise ValueError(f"Invalid 'docs' value {value!r} (expected false, true or an object)")

    def to_value(self) -> Any:
        """Convert to the known_good.json ``docs`` value, or None when it is the default.

        Returns:
                False when disabled, a dict of overrides when any is set, else None so
                the key is omitted for the (default) plain-mounted case.
        """
        if not self.enabled:
            return False
        overrides = {
            key: value
            for key, value in (
                ("bundle", self.bundle),
                ("mount_at", self.mount_at),
                ("attach_to", self.attach_to),
            )
            if value is not None
        }
        return overrides or None


@dataclass
class Metadata:
    """Metadata configuration for a module.

    Attributes:
            code_root_path: Root path to the code directory
            extra_test_config: List of extra test configuration flags
            exclude_test_targets: List of test targets to exclude
            langs: List of languages supported (e.g., ["cpp", "rust"])
    """

    code_root_path: str = "//score/..."
    extra_test_config: list[str] = field(default_factory=lambda: [])
    exclude_test_targets: list[str] = field(default_factory=lambda: [])
    langs: list[str] = field(default_factory=lambda: ["cpp", "rust"])
    rust_coverage_config: str | None = "ferrocene-coverage"  # Optional field for Rust coverage configuration

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
            langs=data.get("langs", ["cpp", "rust"]),
            rust_coverage_config=data.get("rust_coverage_config", "ferrocene-coverage"),
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
            "langs": self.langs,
            "rust_coverage_config": self.rust_coverage_config,
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
    docs: Docs = field(default_factory=Docs)

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
                                        "langs": ["cpp", "rust"]
                                }
                                If not present, uses default Metadata values.
                        - branch (str, optional): Git branch name (default: main)
                        - pin_version (bool, optional): If true, module hash is not updated
                                            to latest HEAD by update scripts (default: false)
                        - docs (bool | dict, optional): Documentation mount for the combined
                                            docs site. Mounted by default; use false for a
                                            module that exposes no //:docs_bundle. See Docs.

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
            # Enable once we are able to remove '*' in known_good.json
            # if any("*" in target for target in metadata.exclude_test_targets):
            #     raise Exception(
            #         f"Module {name} has wildcard '*' in exclude_test_targets, which is not allowed. "
            #         "Please specify explicit test targets to exclude or remove the key if no exclusions are needed."
            #     )
        else:
            # If metadata key is missing, create with defaults
            metadata = Metadata()

        branch = module_data.get("branch", "main")
        pin_version = module_data.get("pin_version", False)

        try:
            docs = Docs.from_value(module_data.get("docs"))
        except ValueError as e:
            raise ValueError(f"Module '{name}': {e}") from None

        return cls(
            name=name,
            hash=commit_hash,
            repo=repo,
            version=version,
            bazel_patches=bazel_patches if bazel_patches else None,
            metadata=metadata,
            branch=branch,
            pin_version=pin_version,
            docs=docs,
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
        docs = self.docs.to_value()
        if docs is not None:
            result["docs"] = docs
        return result
