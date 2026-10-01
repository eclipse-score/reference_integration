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
"""Feature integration tests for the Eclipse S-CORE base libraries.

Each test drives one subcommand of the on-target ``baselibs_test_app``
binary (see ``test_app/``) on the deployed target image through ``run_test_app``
and asserts on its deterministic stdout line, thereby verifying one baselibs
feature library end-to-end on the platform.

Each test references the ``feat_req__baselibs__*`` feature requirement it
partially verifies via ``@add_test_properties``. docs-as-code's source code
linker turns those properties into ``testlink`` attributes on the referenced
requirement needs, which surface in the baselibs feature coverage figures of
the platform verification report.

All tests in this package are combined into the single ``bit`` suite by this
package's ``BUILD`` file, which CI runs before the documentation build.
"""

from attribute_plugin import add_test_properties
from test_app_runner import run_test_app


@add_test_properties(
    partially_verifies=["feat_req__baselibs__json_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_json_library_parses_document(target):
    """Parse a JSON document and read back object, number and list members."""
    output = run_test_app(target, "json")
    assert "name=baselibs" in output
    assert "version=2" in output
    assert "libs_count=2" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__utils_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_utils_library_base64_roundtrip(target):
    """Base64-encode and decode a byte buffer and confirm the round-trip."""
    output = run_test_app(target, "base64")
    assert "encoded=Zm9vYmFy" in output
    assert "decoded=foobar" in output
    assert "roundtrip=ok" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__bitmanipulation"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_bitmanipulation_library_sets_and_toggles_bits(target):
    """Set, check and toggle individual bits of an integral value."""
    output = run_test_app(target, "bitmanip")
    assert "value=16" in output
    assert "check_bit4=1" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__hash_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_hash_library_crc32_ieee_check_value(target):
    """Compute the IEEE CRC-32 of the canonical "123456789" check vector."""
    output = run_test_app(target, "crc32")
    # IEEE 802.3 CRC-32 check value for the ASCII string "123456789".
    assert "checksum=0xcbf43926" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__containers_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_containers_library_dynamic_array(target):
    """Fill and iterate a DynamicArray, confirming size and element access."""
    output = run_test_app(target, "containers")
    assert "size=4" in output
    assert "sum=100" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__result_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_result_library_error_handling(target):
    """Exercise the Result value and error paths without C++ exceptions."""
    output = run_test_app(target, "result")
    assert "ok_value=42" in output
    assert "error_handled=1" in output
    assert "error_msg=division by zero" in output
