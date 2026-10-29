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
ITF tests for the communication module (LoLa / mw::com).

Scope covers delivery, ordering, integrity, service discovery, runtime
deployment config, late join, deployment-config integrity (negative
scenarios), and ASIL-B/ACL isolation.
"""

import json
import logging

import comm_helpers as comm
import pytest
from attribute_plugin import add_test_properties  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


def test_fit_binaries_are_deployed(target):
    """The communication sender and receiver binaries are present in the image."""
    for binary in (
        comm.FIT_SENDER_BIN,
        comm.FIT_RECEIVER_BIN,
        comm.FIT_SENDER_CC_BIN,
        comm.FIT_RECEIVER_CC_BIN,
    ):
        exit_code, _ = target.execute(f"test -f {binary}")
        assert exit_code == 0, f"{binary} not found on target"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__event_type",
        "feat_req__com__producer_consumer",
        "feat_req__com__interfaces",
        "feat_req__com__data_driven_arch",
        "feat_req__com__service_discovery",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_event_exchange_delivers_data(target):
    """
    Verify that a producer and consumer, running as two separate processes,
    exchange cyclic events over shared memory: the consumer discovers the
    offered service, receives samples, and exits cleanly.
    """
    result = comm.run_event_exchange(target, send_cycles=50, recv_cycles=10)
    logger.info("consumer stdout:\n%s", result.recv_stdout)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly"
    assert result.found_service, "service discovery did not locate the provider"
    assert result.received_samples, "consumer received no samples"
    assert result.completed, "consumer did not report a clean completion"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__multi_lang",
        "feat_req__com__event_type",
        "feat_req__com__producer_consumer",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_cpp_sender_rust_receiver(target):
    """
    Verify that the C++ and Rust public APIs are interoperable: the C++
    fit_sender_cc offers VehicleInterface over shared memory and the Rust
    fit_receiver consumes it.  A successful exchange shows that the native
    C++ API path and the Rust FFI API path operate on the same LoLa SHM
    binding, partially evidencing feat_req__com__multi_lang.
    """
    result = comm.run_event_exchange(
        target,
        send_cycles=50,
        recv_cycles=10,
        sender_bin=comm.FIT_SENDER_CC_BIN,
        receiver_bin=comm.FIT_RECEIVER_BIN,
    )
    logger.info("C++→Rust consumer stdout:\n%s", result.recv_stdout)
    logger.info("C++ sender stdout:\n%s", result.send_stdout)

    assert "FIT_SEND_OFFERED" in result.send_stdout, "C++ sender did not report offering the service"
    assert result.recv_exit_code == 0, "Rust consumer did not exit cleanly"
    assert result.found_service, "Rust consumer did not discover the C++ service"
    assert result.received_samples, "Rust consumer received no samples from C++ sender"
    assert result.completed, "Rust consumer did not report a clean completion"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__multi_lang",
        "feat_req__com__event_type",
        "feat_req__com__producer_consumer",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_rust_sender_cpp_receiver(target):
    """
    Verify the reverse direction of C++/Rust API interoperability: the Rust
    fit_sender offers VehicleInterface over shared memory and the C++
    fit_receiver_cc consumes it.  Together with test_cpp_sender_rust_receiver
    this exercises both API directions for feat_req__com__multi_lang.
    """
    result = comm.run_event_exchange(
        target,
        send_cycles=50,
        recv_cycles=10,
        sender_bin=comm.FIT_SENDER_BIN,
        receiver_bin=comm.FIT_RECEIVER_CC_BIN,
    )
    logger.info("Rust→C++ consumer stdout:\n%s", result.recv_stdout)
    logger.info("Rust sender stdout:\n%s", result.send_stdout)

    assert "FIT_SEND_OFFERED" in result.send_stdout, "Rust sender did not report offering the service"
    assert result.recv_exit_code == 0, "C++ consumer did not exit cleanly"
    assert result.found_service, "C++ consumer did not discover the Rust service"
    assert result.received_samples, "C++ consumer received no samples from Rust sender"
    assert result.completed, "C++ consumer did not report a clean completion"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__data_corruption",
        "feat_req__com__data_reordering",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_received_samples_are_ordered_and_intact(target):
    """
    Verify that received samples are neither reordered, duplicated, nor
    corrupted: each consecutive pair of sequence numbers the producer
    embedded in the payload increases by exactly one, and every received
    value is one the producer actually sent (never a garbled value). A
    duplicate delivery of the same sample, a dropped-then-repeated value, or
    an out-of-range/non-numeric payload all fail this check.
    """
    send_cycles = 80
    result = comm.run_event_exchange(target, send_cycles=send_cycles, recv_cycles=20)
    samples = result.received_samples
    logger.info("received sample sequence: %s", samples)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly"
    assert samples, "consumer received no samples"
    assert all(0 <= s < send_cycles for s in samples), (
        f"received samples contain out-of-range sequence values: {samples}"
    )
    assert all(b == a + 1 for a, b in zip(samples, samples[1:])), (
        f"received samples were reordered or duplicated: {samples}"
    )


@add_test_properties(
    partially_verifies=[
        "feat_req__com__depl_config_runtime",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_deployment_config_is_read_from_runtime_path(target):
    """
    Verify that the SHM binding and service identity are taken from a
    deployment manifest read at runtime from an explicit on-target path
    (``-s <path>``), not compiled in.

    A copy of the deployed config is staged at a non-default runtime path
    with its instance identity *changed* to one that exists nowhere else,
    and both roles are pointed at the modified copy via ``-i``. If the
    runtime path were ignored (e.g. silently falling back to the compiled-in
    default), this instance would not exist anywhere and discovery would
    fail -- so a successful exchange proves the modified content at the
    runtime path was actually parsed and used, not merely that some path
    argument was accepted.
    """
    default_specifier = "/Vehicle/Service1/Instance"
    modified_specifier = "/Vehicle/ServiceRuntimeConfigTest/Instance"

    _, default_bytes = target.execute(f"cat {comm.DEFAULT_MANIFEST}")
    manifest = json.loads(default_bytes.decode())
    for instance in manifest["serviceInstances"]:
        if instance["instanceSpecifier"] == default_specifier:
            instance["instanceSpecifier"] = modified_specifier
            break
    else:
        pytest.fail(f"test setup error: default manifest did not contain {default_specifier!r} to modify")

    staged = "/tmp/comm_fit_runtime_manifest.json"
    comm.write_remote_file(target, staged, json.dumps(manifest))

    result = comm.run_event_exchange(
        target, send_cycles=30, recv_cycles=5, manifest=staged, instance_specifier=modified_specifier
    )
    logger.info("runtime-config consumer stdout:\n%s", result.recv_stdout)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly with a modified runtime-path config"
    assert result.found_service, "service not discovered using the modified runtime-path config"
    assert result.received_samples, "no samples received over the modified config-declared SHM binding"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__stateless_communication",
        "feat_req__com__producer_consumer",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_late_joining_consumer_receives_data(target):
    """
    Verify that a consumer subscribing well after the producer has started
    still binds and receives valid samples, proving communication does not
    depend on the consumer being present from the first cycle.
    """
    result = comm.run_event_exchange(target, send_cycles=80, recv_cycles=10, startup_delay_s=3)
    logger.info("late-join consumer stdout:\n%s", result.recv_stdout)

    assert result.recv_exit_code == 0, "late-joining consumer did not exit cleanly"
    assert result.found_service, "late-joining consumer failed to discover the service"
    assert result.received_samples, "late-joining consumer received no samples"


def _assert_missing_config_fails_deterministically(result: comm.CommResult) -> None:
    """
    A missing manifest takes a distinct code path from malformed JSON (see
    fit_receiver.rs's init_lola_runtime): no parse is attempted, so it must
    be caught by our own controlled exit(1)/FIT_RECV_NO_SERVICE path, not a
    parser abort. Pinned to that exact exit code and both markers -- rather
    than just "exit != 0" -- so an unrelated crash (segfault, wrong binary,
    panic elsewhere) cannot be mistaken for this specific contract.
    """
    assert "FIT_RECV_CONFIG_MISSING" in result.recv_stdout, (
        f"consumer did not report the config file as missing:\n{result.recv_stdout}"
    )
    assert result.recv_exit_code == 1, (
        f"expected the controlled exit(1)/FIT_RECV_NO_SERVICE path (got exit "
        f"{result.recv_exit_code}):\n{result.recv_stdout}"
    )
    assert "FIT_RECV_NO_SERVICE" in result.recv_stdout, (
        f"consumer did not report giving up on service discovery:\n{result.recv_stdout}"
    )
    assert not result.found_service, "consumer proceeded past config load to service discovery"
    assert not result.received_samples, "consumer proceeded to receive samples despite a missing config"


def _assert_malformed_config_aborts(result: comm.CommResult) -> None:
    """
    Syntactically invalid or schema-invalid JSON is expected to abort the
    process while parsing the config -- empirically observed as SIGABRT
    (shell exit 134) on both Linux and QNX. Pinned to that exact exit code
    -- rather than just "exit != 0" -- so an unrelated crash cannot be
    mistaken for a config-parse failure.
    """
    assert result.recv_exit_code == 134, (
        f"expected a config-parse abort (SIGABRT, shell exit 134), got exit "
        f"{result.recv_exit_code}:\n{result.recv_stdout}"
    )
    assert not result.found_service, "consumer proceeded past config load to service discovery"
    assert not result.received_samples, "consumer proceeded to receive samples despite a malformed config"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__depl_config_runtime",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_missing_config_file_fails_deterministically(target):
    """
    Verify that a missing deployment manifest causes the process to fail
    deterministically and quickly rather than hang or silently continue.
    """
    result = comm.run_receiver_with_manifest(target, "/tmp/comm_fit_missing_config.json")
    logger.info("missing-config consumer output:\n%s", result.recv_stdout)
    _assert_missing_config_fails_deterministically(result)


@add_test_properties(
    partially_verifies=[
        "feat_req__com__depl_config_runtime",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_truncated_config_fails_deterministically(target):
    """
    Verify that syntactically invalid JSON in the deployment manifest fails
    deterministically rather than hang or silently continue.
    """
    manifest_path = "/tmp/comm_fit_truncated_config.json"
    comm.write_remote_file(target, manifest_path, comm.TRUNCATED_CONFIG_JSON)

    result = comm.run_receiver_with_manifest(target, manifest_path)
    logger.info("truncated-config consumer output:\n%s", result.recv_stdout)
    _assert_malformed_config_aborts(result)


@add_test_properties(
    partially_verifies=[
        "feat_req__com__depl_config_runtime",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_schema_invalid_config_fails_deterministically(target):
    """
    Verify that well-formed JSON missing the required schema structure fails
    deterministically rather than hang or silently continue.
    """
    manifest_path = "/tmp/comm_fit_schema_invalid_config.json"
    comm.write_remote_file(target, manifest_path, comm.SCHEMA_INVALID_CONFIG_JSON)

    result = comm.run_receiver_with_manifest(target, manifest_path)
    logger.info("schema-invalid-config consumer output:\n%s", result.recv_stdout)
    _assert_malformed_config_aborts(result)


@add_test_properties(
    partially_verifies=[
        "feat_req__com__depl_config_runtime",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_cc_missing_config_file_fails_deterministically(target):
    """
    Verify the C++ receiver exits non-zero on a missing manifest rather than
    hanging or silently continuing.  The C++ receiver exits 1 immediately
    after printing FIT_RECV_CONFIG_MISSING, unlike the Rust receiver which
    also reaches FIT_RECV_NO_SERVICE; both contracts are non-zero + no data.
    """
    result = comm.run_receiver_with_manifest(
        target, "/tmp/comm_fit_cc_missing_config.json", receiver_bin=comm.FIT_RECEIVER_CC_BIN
    )
    logger.info("C++ missing-config consumer output:\n%s", result.recv_stdout)

    assert "FIT_RECV_CONFIG_MISSING" in result.recv_stdout, (
        f"C++ consumer did not report the config file as missing:\n{result.recv_stdout}"
    )
    assert result.recv_exit_code == 1, (
        f"expected controlled exit(1) from C++ consumer (got {result.recv_exit_code}):\n{result.recv_stdout}"
    )
    assert not result.found_service, "C++ consumer proceeded to service discovery despite missing config"
    assert not result.received_samples, "C++ consumer received samples despite a missing config"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__depl_config_runtime",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_cc_truncated_config_fails_deterministically(target):
    """
    Verify the C++ receiver fails deterministically on syntactically invalid
    JSON.  Both C++ and Rust receivers share the same upstream JSON parser, so
    the expected signal is SIGABRT (shell exit 134), same as the Rust test.
    """
    manifest_path = "/tmp/comm_fit_cc_truncated_config.json"
    comm.write_remote_file(target, manifest_path, comm.TRUNCATED_CONFIG_JSON)

    result = comm.run_receiver_with_manifest(target, manifest_path, receiver_bin=comm.FIT_RECEIVER_CC_BIN)
    logger.info("C++ truncated-config consumer output:\n%s", result.recv_stdout)
    _assert_malformed_config_aborts(result)


@add_test_properties(
    partially_verifies=[
        "feat_req__com__asil",
        "feat_req__com__acl_for_consumer",
        "feat_req__com__acl_for_producer",
        "feat_req__com__acl_per_service_instance",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_mixed_criticality_acl_isolation(target):
    """
    Verify ASIL-B mixed-criticality isolation: an ASIL-B provider offers to
    exactly one allowed UID (the target's own default identity). Two
    consumers subscribe concurrently -- one running as that allowed UID, one
    running as a UID deliberately excluded from allowedConsumer.

    The allowed consumer receives samples while the excluded consumer is
    active concurrently, proving the excluded consumer cannot affect the
    allowed stream. The excluded consumer fails deterministically (non-zero
    exit, an ACL/proxy-denial diagnostic, never receives a sample) -- observed
    as an uncaught panic in the generated bindings once the shared-memory
    open is denied, not a graceful, catchable error.

    Obtaining the excluded consumer's distinct UID uses `setpriv` on Linux,
    which lets an unprivileged UID still bring up its LoLa endpoint and so
    reach the shared-memory ACL check the assertions below rely on.

    Skipped on QNX: LoLa's MessagePassingService endpoint registration requires
    privilege, so a lower-privilege UID aborts at message-passing setup before
    reaching the shared-memory ACL check.
    """
    if comm.is_qnx(target):
        pytest.skip(
            "allowedConsumer ACL enforcement cannot be exercised via a "
            "lower-privilege UID on QNX: LoLa's MessagePassingService endpoint "
            "registration requires privilege, so a consumer run under `on -u` "
            "aborts at message-passing setup before reaching the shared-memory "
            "ACL check."
        )

    allowed_result, denied_result, allowed_uid = comm.run_acl_isolation_scenario(target)
    logger.info("ACL scenario allowed_uid=%s", allowed_uid)
    logger.info("allowed consumer stdout:\n%s", allowed_result.recv_stdout)
    logger.info("denied consumer stdout:\n%s", denied_result.recv_stdout)

    # Allowed consumer: unaffected by the concurrently-running denied one.
    assert allowed_result.recv_exit_code == 0, "allowed consumer did not exit cleanly"
    assert allowed_result.received_samples, "allowed consumer received no samples"

    # Denied consumer: fails deterministically, never receives data, and the
    # failure is specifically attributable to the ACL/proxy-creation path
    # (not some unrelated crash) -- see comm.ACL_DENIAL_MARKERS for what this
    # denial actually looks like on the wire (an uncaught panic in the
    # generated bindings, not a graceful Err from builder.build()).
    assert any(marker in denied_result.recv_stdout for marker in comm.ACL_DENIAL_MARKERS), (
        f"consumer with an excluded UID did not report an ACL/proxy denial:\n{denied_result.recv_stdout}"
    )
    assert denied_result.recv_exit_code != 0, "consumer with an excluded UID was not denied"
    assert not denied_result.found_service, "consumer with an excluded UID reached service discovery"
    assert not denied_result.received_samples, "consumer with an excluded UID received samples"
