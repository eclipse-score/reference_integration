#!/usr/bin/env python3
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

"""
Basic tests for inject_overlay tool.

Note: Full integration tests require root partition access and are tagged
with 'requires-root-partition'. This file provides unit tests for
helper functions that can run without special privileges.
"""

import tarfile
import tempfile
import unittest
from pathlib import Path

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from inject_overlay import get_tar_size


class InjectOverlayBasicTest(unittest.TestCase):
    """Basic unit tests that don't require root partition access."""

    def test_get_tar_size_empty(self):
        """Test tar size calculation with empty tar."""
        with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Create empty tar
            with tarfile.open(tmp_path, 'w') as tf:
                pass
            
            size = get_tar_size(tmp_path)
            self.assertEqual(size, 0, "Empty tar should have zero size estimate")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_get_tar_size_with_files(self):
        """Test tar size calculation with actual files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = Path(tmpdir) / "test.tar"
            
            # Create tar with known content
            with tarfile.open(str(tar_path), 'w') as tf:
                import io
                content = b"Hello, World!"
                info = tarfile.TarInfo(name="test.txt")
                info.size = len(content)
                tf.addfile(info, io.BytesIO(content))
            
            size = get_tar_size(str(tar_path))
            
            # Size should be at least the content size
            self.assertGreater(size, len(content), 
                             "Size estimate should include content")
            # Should have 10% overhead added
            expected_size = int(len(content) * 1.1)
            self.assertEqual(size, expected_size,
                           "Size should be content + 10% overhead")


if __name__ == "__main__":
    unittest.main()
