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
"""Platform integration test for the persistency (KVS) standalone showcase."""

import json

from attribute_plugin import add_test_properties
from showcase_runner import run_showcases

_KVS_FILE = "/data/kvs_0_0.json"
_EXPECTED_KEYS = {"number", "bool", "string", "null", "array", "object"}


@add_test_properties(
    partially_verifies=["stkh_req__functional_req__data_persistency"],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_persistency_kvs_showcase(target):
    """Verifies that the KVS showcase writes six typed key-value pairs to disk
    and that a second KVS process can reload them — exercising hash validation."""
    output = run_showcases(target, "Persistency KVS Example")
    assert "Done!" in output, f"createtestdata did not complete:\n{output}"

    exit_code, out = target.execute(f"cat {_KVS_FILE}")
    assert exit_code == 0, f"KVS data file not found at {_KVS_FILE}"
    root = json.loads(out.decode(errors="replace"))
    data = root.get("v", {})
    assert set(data) == _EXPECTED_KEYS, f"Unexpected keys in KVS data file: {set(data)}"
    assert data.get("number", {}).get("t") == "f64", f"'number' has wrong type tag: {data.get('number')}"
    assert data.get("number", {}).get("v") == 123.0, f"'number' has wrong value: {data.get('number')}"

    exit_code, out = target.execute("/showcases/bin/kvs_tool -d /data -o getkey -k number")
    out = out.decode(errors="replace")
    assert exit_code == 0, f"kvs_tool getkey failed:\n{out}"
    assert "Key 'number' exists!" in out, f"getkey did not confirm key presence:\n{out}"
