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
            exclude_test_targets: List of test targets to exclude
            langs: List of languages supported (e.g., ["cpp", "rust"])
    """

    code_root_path: str = "//score/..."
    exclude_test_targets: list[str] = field(default_factory=lambda: [])
    langs: list[str] = field(default_factory=lambda: ["cpp", "rust"])

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
            exclude_test_targets=data.get("exclude_test_targets", []),
            langs=data.get("langs", ["cpp", "rust"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Metadata instance to dictionary representation.

        Returns:
                Dictionary with metadata configuration
        """
        return {
            "code_root_path": self.code_root_path,
            "exclude_test_targets": self.exclude_test_targets,
            "langs": self.langs,
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
                                        "exclude_test_targets": [""],
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
        # Support both 'bazel_patches' and legacy 'patches' keys
        bazel_patches = module_data.get("bazel_patches") or module_data.get(
            "patches", []
        )

        # Parse metadata - if not present or is None/empty dict, use defaults
        metadata_data = module_data.get("metadata")
        if metadata_data is not None:
            metadata = Metadata.from_dict(metadata_data)
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
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError(f"Cannot parse owner/repo from: {self.repo}")

        return f"{parts[0]}/{parts[1]}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert Module instance to dictionary representation for JSON output.

        Returns:
                Dictionary with module configuration
        """
        result: Dict[str, Any] = {
            "repo": self.repo,
            "hash": self.hash,
            "metadata": self.metadata.to_dict(),
        }
        if self.version:
            result["version"] = self.version
        if self.bazel_patches:
            result["bazel_patches"] = self.bazel_patches
        if self.branch and self.branch != "main":
            result["branch"] = self.branch
        if self.pin_version:
            result["pin_version"] = True
        return result
