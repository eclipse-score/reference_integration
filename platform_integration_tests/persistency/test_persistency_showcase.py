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
"""Platform integration test for the persistency (KVS) standalone showcase.

Verifies that the KVS showcase not only exits successfully but actually
writes key-value data to disk — the file at a known path is checked for
existence and content after the showcase completes.
"""

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases

_KVS_FILE = "/tmp/kvs_0_0.json"
_KVS_HASH = "/tmp/kvs_0_0.hash"


@add_test_properties(
    partially_verifies=["stkh_req__functional_req__data_persistency"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_persistency_kvs_showcase(target):
    """The KVS showcase writes typed key-value pairs to disk using the KVS
    API (flush → JSON file), then reopens the same instance and asserts the
    data survived. This test goes beyond log inspection: it verifies that the
    KVS file and its hash file actually exist on the target filesystem after
    the showcase exits."""
    run_showcases(target, "Persistency KVS Example")

    # Verify the KVS data file was written to disk.
    exit_code, _ = target.execute(f"test -f {_KVS_FILE}")
    assert exit_code == 0, f"KVS data file not written to disk at {_KVS_FILE}"

    # Verify the companion hash file was written (proves flush completed fully).
    exit_code, _ = target.execute(f"test -f {_KVS_HASH}")
    assert exit_code == 0, f"KVS hash file not written to disk at {_KVS_HASH}"

    # Verify the data file contains the keys written by createtestdata.
    exit_code, out = target.execute(f"cat {_KVS_FILE}")
    assert exit_code == 0, f"Failed to read {_KVS_FILE}"
    content = out.decode(errors="replace")
    for key in ("number", "bool", "string", "array", "object"):
        assert f'"{key}"' in content, (
            f"Expected key '{key}' not found in KVS data file:\n{content}"
        )
