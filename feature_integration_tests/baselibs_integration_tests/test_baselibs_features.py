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
    partially_verifies=[
        "feat_req__baselibs__containers_library",
        "feat_req__baselibs__abi_containers",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_containers_library_dynamic_array(target):
    """Fill and iterate a DynamicArray, confirming size and element access.

    DynamicArray is the ABI-stable container (raw-pointer iterators,
    allocator-aware), so this also partially verifies the abi_containers
    requirement.
    """
    output = run_test_app(target, "containers")
    assert "size=4" in output
    assert "sum=100" in output


@add_test_properties(
    partially_verifies=[
        "feat_req__baselibs__result_library",
        "feat_req__baselibs__panic_free_development",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_result_library_error_handling(target):
    """Exercise the Result value and error paths without C++ exceptions.

    Returning errors as values instead of throwing is the panic-free error
    handling mechanism, so this also partially verifies the
    panic_free_development requirement.
    """
    output = run_test_app(target, "result")
    assert "ok_value=42" in output
    assert "error_handled=1" in output
    assert "error_msg=division by zero" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__concurrency_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_concurrency_library_notification(target):
    """Notify a Notification and confirm an already-notified wait returns."""
    output = run_test_app(target, "concurrency")
    assert "notified=1" in output
    assert "reset=ok" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__filesystem_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_filesystem_library_path_decomposition(target):
    """Decompose a path into filename, extension and parent components."""
    output = run_test_app(target, "filesystem")
    assert "filename=report.txt" in output
    assert "extension=.txt" in output
    assert "parent=/home/user/documents" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__memory_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_memory_library_pmr_ring_buffer(target):
    """Fill a PMR ring buffer past capacity and confirm it overwrites oldest."""
    output = run_test_app(target, "memory")
    assert "size=3" in output
    assert "front=20" in output
    assert "full=1" in output


@add_test_properties(
    partially_verifies=["feat_req__baselibs__static_reflection_library"],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_static_reflection_library_serialize_roundtrip(target):
    """Serialize a reflectable struct to bytes and deserialize it back."""
    output = run_test_app(target, "reflect")
    assert "id=43981" in output  # 0xABCD
    assert "count=7" in output
    assert "roundtrip=ok" in output


@add_test_properties(
    partially_verifies=[
        "feat_req__baselibs__flatbuffers_library",
        "feat_req__baselibs__multi_language_apis",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_flatbuffers_library_build_and_lookup(target):
    """Build a flatbuffer from a schema and look an element up by key.

    FlatBuffers is a language-neutral serialization format with generated C++
    and Rust APIs, so this also partially verifies the multi_language_apis
    requirement.
    """
    output = run_test_app(target, "flatbuffers")
    assert "items=3" in output
    assert "lookup20=twenty" in output
