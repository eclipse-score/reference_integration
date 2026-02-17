"""KnownGood dataclass for score reference integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
from pathlib import Path
import json
import datetime as dt

from .module import Module


@dataclass
class KnownGood:
	"""Known good configuration with modules and metadata.

	Module structure: modules = {"group1": {"module1": Module}, "group2": {"module2": Module}}
	"""
	modules: Dict[str, Dict[str, Module]]
	timestamp: str

	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> KnownGood:
		"""Create a KnownGood instance from a dictionary.

		Expected structure:
		{"modules": {"group1": {"score_baselibs": {...}}, "group2": {"score_logging": {...}}}}

		Args:
			data: Dictionary containing known_good.json data

		Returns:
			KnownGood instance
		"""
		modules_dict = data.get('modules', {})
		timestamp = data.get('timestamp', '')

		parsed_modules: Dict[str, Dict[str, Module]] = {}
		for group_name, group_modules in modules_dict.items():
			if isinstance(group_modules, dict):
				modules_list = Module.parse_modules(group_modules)
				parsed_modules[group_name] = {m.name: m for m in modules_list}

		return cls(modules=parsed_modules, timestamp=timestamp)

	def to_dict(self) -> Dict[str, Any]:
		"""Convert KnownGood instance to dictionary for JSON output.

		Returns:
			Dictionary with known_good configuration
		"""
		modules_output = {
			group_name: {name: module.to_dict() for name, module in group_modules.items()}
			for group_name, group_modules in self.modules.items()
		}

		return {
			"modules": modules_output,
			"timestamp": self.timestamp
		}
	
	def write(self, output_path: Path, dry_run: bool = False) -> None:
		"""Write known_good data to file or print for dry-run.
		
		Args:
			output_path: Path to output file
			dry_run: If True, print instead of writing
		"""
		
		# Update timestamp before writing
		self.timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat() + "Z"
		
		output_json = json.dumps(self.to_dict(), indent=4, sort_keys=False) + "\n"
		
		if dry_run:
			print(f"\nDry run: would write to {output_path}\n")
			print("---- BEGIN UPDATED JSON ----")
			print(output_json, end="")
			print("---- END UPDATED JSON ----")
		else:
			with open(output_path, "w", encoding="utf-8") as f:
				f.write(output_json)
			print(f"Successfully wrote updated known_good.json to {output_path}")


def load_known_good(path: Path) -> KnownGood:
	"""Load and parse the known_good.json file.
	
	Args:
		path: Path to known_good.json file
		
	Returns:
		KnownGood instance with parsed modules
	"""
	
	with open(path, "r", encoding="utf-8") as f:
		data = json.load(f)
	
	if not isinstance(data, dict) or not isinstance(data.get("modules"), dict):
		raise ValueError(
			f"Invalid known_good.json at {path} (expected object with 'modules' dict)"
		)
	
	return KnownGood.from_dict(data)
