"""Module dataclass for score reference integration."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Any, Dict, List
import logging


@dataclass
class Module:
	name: str
	hash: str
	repo: str
	version: str | None = None
	patches: list[str] | None = None
	branch: str = "main"

	@classmethod
	def from_dict(cls, name: str, module_data: Dict[str, Any]) -> Module:
		"""Create a Module instance from a dictionary representation.
		
		Args:
			name: The module name
			module_data: Dictionary containing module configuration with keys:
				- repo (str): Repository URL
				- hash or commit (str): Commit hash
				- version (str, optional): Module version
				- patches (list[str], optional): List of patch files
				- branch (str, optional): Git branch name (default: main)
		
		Returns:
			Module instance
		"""
		repo = module_data.get("repo", "")
		# Support both 'hash' and 'commit' keys
		commit_hash = module_data.get("hash") or module_data.get("commit", "")
		version = module_data.get("version")
		patches = module_data.get("patches", [])
		branch = module_data.get("branch", "main")
		
		return cls(
			name=name,
			hash=commit_hash,
			repo=repo,
			version=version,
			patches=patches if patches else None,
			branch=branch
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
			"hash": self.hash
		}
		if self.version:
			result["version"] = self.version
		if self.patches:
			result["patches"] = self.patches
		if self.branch and self.branch != "main":
			result["branch"] = self.branch
		return result
