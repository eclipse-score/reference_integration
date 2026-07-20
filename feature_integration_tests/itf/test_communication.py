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

import logging

import comm_helpers as comm
import pytest
from test_properties import add_test_properties

logger = logging.getLogger(__name__)


def test_fit_binaries_are_deployed(target):
    """The communication sender and receiver binaries are present in the image."""
    for binary in (comm.FIT_SENDER_BIN, comm.FIT_RECEIVER_BIN):
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
        "feat_req__com__data_corruption",
        "feat_req__com__data_reordering",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_received_samples_are_ordered_and_intact(target):
    """
    Verify that received samples are neither reordered nor corrupted: the
    sequence numbers the producer embedded in each payload arrive in
    non-decreasing order and every received value is one the producer actually
    sent (never a garbled value).
    """
    send_cycles = 80
    result = comm.run_event_exchange(target, send_cycles=send_cycles, recv_cycles=20)
    samples = result.received_samples
    logger.info("received sample sequence: %s", samples)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly"
    assert samples, "consumer received no samples"
    assert comm.is_non_decreasing(samples), f"received samples out of order: {samples}"
    assert comm.samples_are_intact(samples, send_cycles), (
        f"received a value the producer never sent (corruption): {samples}"
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
    (``-s <path>``), not compiled in. The deployed config is staged at a
    non-default runtime path and both roles are pointed at it; the consumer
    then discovers the service and receives samples over the config-declared
    SHM binding.
    """
    staged = "/tmp/comm_fit_runtime_manifest.json"
    copy_rc, _ = target.execute(f"cp {comm.DEFAULT_MANIFEST} {staged}")
    assert copy_rc == 0, "could not stage a runtime deployment manifest on target"

    result = comm.run_event_exchange(target, send_cycles=30, recv_cycles=5, manifest=staged)
    logger.info("runtime-config consumer stdout:\n%s", result.recv_stdout)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly with a runtime-path config"
    assert result.found_service, "service not discovered using the runtime-path config"
    assert result.received_samples, "no samples received over the config-declared SHM binding"


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


def _assert_fails_on_load_without_hang(result: comm.CommResult) -> None:
    """
    Shared check for the config-integrity tests below: the process must fail
    deterministically -- bounded by the shell `timeout` in
    run_receiver_with_manifest -- never silently succeed, and never proceed
    far enough to discover a service or process a sample.
    """
    assert result.recv_exit_code != 0, "consumer did not fail on an invalid/missing config"
    assert not result.found_service, "consumer proceeded past config load to service discovery"
    assert not result.received_samples, "consumer proceeded to receive samples despite bad config"


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
    _assert_fails_on_load_without_hang(result)


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
    _assert_fails_on_load_without_hang(result)


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
    _assert_fails_on_load_without_hang(result)


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
    exit, never discovers the service) and never receives a sample.

    Obtaining the excluded consumer's distinct UID uses `setpriv` on Linux,
    which lets an unprivileged UID still bring up its LoLa endpoint and so
    reach the shared-memory ACL check the assertions below rely on.

    Skipped on QNX: there, LoLa's MessagePassingService endpoint registration
    itself requires privilege, so a consumer launched under a lower-privilege
    UID (`on -u <uid>`) aborts at message-passing setup before reaching the
    shared-memory ACL -- a limitation of the QNX IPC layer itself, not of
    allowedConsumer enforcement, already documented for the removed
    ipc_bridge example.
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

    # Denied consumer: fails deterministically, never receives data.
    assert denied_result.recv_exit_code != 0, "consumer with an excluded UID was not denied"
    assert not denied_result.found_service, "consumer with an excluded UID reached service discovery"
    assert not denied_result.received_samples, "consumer with an excluded UID received samples"
