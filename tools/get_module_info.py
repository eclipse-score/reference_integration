#!/usr/bin/env python3
"""Extract module information from known_good.json."""

import json
import sys


def load_module_data(known_good_file, module_name):
    """
    Load module data from known_good.json.
    
    Args:
        known_good_file: Path to the known_good.json file
        module_name: Name of the module to look up
        
    Returns:
        Dictionary with module data, or empty dict if not found
    """
    try:
        with open(known_good_file, 'r') as f:
            data = json.load(f)
        modules = data.get('modules', {})
        return modules.get(module_name, {})
    except Exception:
        return {}


def get_module_field(module_data, field='hash'):
    """
    Extract a specific field from module data.
    
    Args:
        module_data: Dictionary with module information
        field: Field to extract ('hash', 'version', 'repo', or 'all')
        
    Returns:
        Requested field value, or 'N/A' if not found
        For 'hash': truncated to 8 chars if longer
        For 'all': returns hash/version (prefers hash, falls back to version)
    """
    if not module_data:
        return 'N/A'
    
    if field == 'repo':
        repo = module_data.get('repo', 'N/A')
        # Remove .git suffix if present
        if repo.endswith('.git'):
            repo = repo[:-4]
        return repo
    elif field == 'version':
        return module_data.get('version', 'N/A')
    elif field == 'hash':
        hash_val = module_data.get('hash', 'N/A')
        return hash_val
    else:  # field == 'all' or default
        hash_val = module_data.get('hash', module_data.get('version', 'N/A'))
        return hash_val


if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print('Usage: get_module_info.py <known_good.json> <module_name> [field]')
        print('  field: hash (default), version, repo, or all')
        print('N/A')
        sys.exit(1)
    
    known_good_file = sys.argv[1]
    module_name = sys.argv[2]
    field = sys.argv[3] if len(sys.argv) == 4 else 'all'
    
    module_data = load_module_data(known_good_file, module_name)
    result = get_module_field(module_data, field)
    print(result)
