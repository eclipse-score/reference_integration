#!/usr/bin/env python3
"""Extract module information from known_good.json."""

import json
import sys
from typing import Optional

from models import Module


def load_module(known_good_file: str, module_name: str) -> Optional[Module]:
    """
    Load module from known_good.json.
    
    Args:
        known_good_file: Path to the known_good.json file
        module_name: Name of the module to look up
        
    Returns:
        Module instance, or None if not found
    """
    try:
        with open(known_good_file, 'r') as f:
            data = json.load(f)
        modules_dict = data.get('modules', {})
        module_data = modules_dict.get(module_name)
        
        if not module_data:
            return None
        
        return Module.from_dict(module_name, module_data)
    except Exception as e:
        # Log error to stderr for debugging
        print(f"Error loading {known_good_file}: {e}", file=sys.stderr)
        return None


def get_module_field(module: Optional[Module], field: str = 'hash') -> str:
    """
    Extract a specific field from module.
    
    Args:
        module: Module instance
        field: Field to extract ('hash', 'version', 'repo', or 'all')
        
    Returns:
        Requested field value, or 'N/A' if not found
        For 'hash': returns the hash value
        For 'all': returns hash/version (prefers hash, falls back to version)
    """
    if not module:
        return 'N/A'
    
    if field == 'repo':
        repo = module.repo or 'N/A'
        # Remove .git suffix if present
        if repo.endswith('.git'):
            repo = repo[:-4]
        return repo
    elif field == 'version':
        return module.version or 'N/A'
    elif field == 'hash':
        return module.hash or 'N/A'
    else:  # field == 'all' or default
        return module.hash or module.version or 'N/A'


if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print('Usage: get_module_info.py <known_good.json> <module_name> [field]')
        print('  field: hash (default), version, repo, or all')
        print('N/A')
        sys.exit(1)
    
    known_good_file = sys.argv[1]
    module_name = sys.argv[2]
    field = sys.argv[3] if len(sys.argv) == 4 else 'all'
    
    module = load_module(known_good_file, module_name)
    result = get_module_field(module, field)
    print(result)
