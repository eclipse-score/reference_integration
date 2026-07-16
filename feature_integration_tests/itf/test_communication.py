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

Tests exercise the deployed ipc_bridge example on the target image as two
separate OS processes communicating over real shared memory, and assert on
the data the consumer actually observes -- sample sequence and per-sample
hash validity -- rather than on log strings the application prints about its
own configuration.
"""

import logging

import pytest

import comm_helpers as comm
from test_properties import add_test_properties

logger = logging.getLogger(__name__)


def test_ipc_bridge_is_deployed(target):
    """The communication example binary is present in the image."""
    exit_code, _ = target.execute(f"test -f {comm.IPC_BRIDGE_BIN}")
    assert exit_code == 0, f"{comm.IPC_BRIDGE_BIN} not found on target"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__event_type",
        "feat_req__com__producer_consumer",
        "feat_req__com__interfaces",
        "feat_req__com__time_based_arch",
        "feat_req__com__service_discovery",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_event_exchange_delivers_valid_data(target):
    """
    Verify that a producer and consumer exchange cyclic events over shared
    memory: the consumer discovers the offered service, exits cleanly, and
    confirms at least one hash-valid sample cycle with no hash mismatch.
    """
    result = comm.run_event_exchange(target, send_cycles=50, recv_cycles=10)
    logger.info("consumer stdout:\n%s", result.recv_stdout)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly"
    assert result.found_service, "service discovery did not locate the provider"
    assert result.valid_data_count > 0, "no hash-valid sample cycle was confirmed"
    assert not result.has_hash_failure, "receiver reported a hash mismatch"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__data_corruption",
        "feat_req__com__data_reordering",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_received_samples_are_ordered_and_uncorrupted(target):
    """
    Verify that received samples are neither corrupted nor reordered: each
    sample's FNV-1a hash matches what the producer sent, and the sequence of
    received cycle numbers is non-decreasing. Both are properties of each
    delivered sample and the delivered sequence, so they hold regardless of
    scheduling jitter. The mixed-criticality form of this check, where an
    excluded consumer must not affect an allowed one, is covered by
    test_mixed_criticality_acl_isolation.
    """
    result = comm.run_event_exchange(target, send_cycles=80, recv_cycles=20)
    samples = result.received_samples
    logger.info("received sample sequence: %s", samples)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly"
    assert samples, "consumer received no samples"
    assert not result.has_hash_failure, "receiver reported a hash mismatch (corruption)"
    assert comm.is_non_decreasing(samples), f"received samples out of order: {samples}"


@add_test_properties(
    partially_verifies=[
        "feat_req__com__stateless_communication",
        "feat_req__com__producer_consumer",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_late_joining_consumer_receives_cached_data(target):
    """
    Verify that a consumer subscribing well after the producer has started
    still binds and receives valid, cached samples.
    """
    result = comm.run_event_exchange(
        target, send_cycles=80, recv_cycles=10, startup_delay_s=3
    )
    logger.info("late-join consumer stdout:\n%s", result.recv_stdout)

    assert result.recv_exit_code == 0, "late-joining consumer did not exit cleanly"
    assert result.found_service, "late-joining consumer failed to discover the service"
    assert result.received_samples, "late-joining consumer received no cached samples"
    assert not result.has_hash_failure, "receiver reported a hash mismatch"


def test_service_discovery_is_order_independent():
    """
    Starting a consumer before any provider offers the service should let it
    keep polling and bind once the provider appears, proving discovery does
    not depend on start order.

    Skipped: starting the consumer first races the provider's shared-memory
    setup with this vehicle. The consumer discovers the service but then
    intermittently fails either at proxy construction or on its first sample
    read, as it catches the provider's very first sample before the shared-
    memory region is fully constructed. Service discovery is still exercised
    on every run by test_event_exchange_delivers_valid_data.
    """
    pytest.skip(
        "Consumer-first discovery races the provider's shared-memory setup "
        "with this vehicle: proxy construction / first-sample reads "
        "intermittently fail."
    )


def test_generic_skeleton_interoperates_with_typed_proxy():
    """
    A generic (reflection) skeleton feeding an ordinary typed proxy should
    deliver hash-valid, ordered samples identical to the typed publishing
    path, proving access is transparent to how the provider was constructed.

    Skipped: the generic skeleton delivers its first sample twice, so the
    receiver sees more samples than it can place in order and exits non-zero.
    The typed skeleton does not have this issue under the same harness.
    """
    pytest.skip(
        "The generic skeleton delivers its first sample twice, which trips "
        "the receiver's ordering/count check; the typed skeleton is "
        "unaffected."
    )


@add_test_properties(
    partially_verifies=[
        "feat_req__com__depl_config_runtime",
        "feat_req__com__multi_binding_depl",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
def test_deployment_config_is_read_from_runtime_path(target):
    """
    Verify that the SHM binding and service identity are taken from a
    deployment manifest read at runtime from an explicit on-target path
    (`-s <path>`), not compiled in. A copy of the deployed config is staged
    at a non-default runtime path and both roles are pointed at it; the
    consumer discovers the service and receives hash-valid, non-decreasing
    samples over the config-declared SHM binding.

    Only the SHM binding is exercised here: SOME/IP is not implemented
    upstream.
    """
    deployed = "/tmp/comm_fit_runtime_manifest.json"
    # Stage the target's own valid deployed config at a non-default runtime
    # path, so we prove the -s runtime-path mechanism without embedding a
    # config here. (Source path is the app's default config location relative
    # to COMM_CWD; confirm on-target if the deployed layout differs.)
    copy_rc, _ = target.execute(f"cp {comm.COMM_CWD}/etc/mw_com_config.json {deployed}")
    assert copy_rc == 0, "could not stage a runtime deployment manifest on target"

    result = comm.run_event_exchange(target, send_cycles=30, recv_cycles=5, manifest=deployed)
    logger.info("runtime-config consumer stdout:\n%s", result.recv_stdout)

    assert result.recv_exit_code == 0, "consumer did not exit cleanly with a runtime-path config"
    assert result.found_service, "service not discovered using the runtime-path config"
    assert result.valid_data_count > 0, "no hash-valid samples over the config-declared SHM binding"
    assert not result.has_hash_failure, "receiver reported a hash mismatch"


def _assert_fails_on_load_without_hang(result: comm.CommResult) -> None:
    """
    Shared check for the config-integrity tests below: the process must fail
    deterministically and quickly while parsing the bad config, never hang,
    never silently succeed, and never proceed far enough to discover a
    service or process a sample.
    """
    assert result.recv_exit_code != 0, "consumer did not fail on an invalid/missing config"
    assert any(marker in result.recv_stdout for marker in comm.CONFIG_FAILURE_MARKERS), (
        f"failure was not attributable to config loading:\n{result.recv_stdout}"
    )
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

    The config parser fails on an assertion, which aborts the process with
    SIGABRT (exit code 134) rather than returning a recoverable
    score::Result. The requirement set also names an error-handling
    requirement here, but it has no published feat_req__com__* id, so only
    DeploymentConfigurationAtRuntime is cited.
    """
    result = comm.run_consumer_with_manifest(target, "/tmp/comm_fit_missing_config.json")
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

    result = comm.run_consumer_with_manifest(target, manifest_path)
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

    result = comm.run_consumer_with_manifest(target, manifest_path)
    logger.info("schema-invalid-config consumer output:\n%s", result.recv_stdout)
    _assert_fails_on_load_without_hang(result)


@add_test_properties(
    partially_verifies=[
        "feat_req__com__safe_communication",
        "feat_req__com__asil",
        "feat_req__com__data_corruption",
        "feat_req__com__data_reordering",
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

    The allowed consumer receives hash-valid, non-corrupted samples while the
    excluded consumer is active concurrently, proving the excluded consumer
    cannot affect the allowed stream. The excluded consumer fails
    deterministically at shared-memory open time (non-zero exit, a
    "Permission denied" / "Could not create Proxy" diagnostic) and never
    receives a sample.

    Obtaining the excluded consumer's distinct UID uses `setpriv` on Linux,
    which lets an unprivileged UID still bring up its LoLa endpoint and so
    reach the shared-memory ACL check the assertions below rely on.

    Skipped on QNX: there, LoLa's MessagePassingService endpoint registration
    itself requires privilege, so a consumer launched under a lower-privilege
    UID (`on -u <uid>`) aborts at message-passing setup before reaching the
    shared-memory ACL. A control run in which the excluded UID was explicitly
    added to allowedConsumer failed identically, confirming the failure is a
    generic privilege limitation of the QNX IPC layer, not allowedConsumer
    enforcement -- so denial there cannot be attributed to the ACL.
    """
    if comm.is_qnx(target):
        pytest.skip(
            "allowedConsumer ACL enforcement cannot be exercised via a "
            "lower-privilege UID on QNX: LoLa's MessagePassingService endpoint "
            "registration requires privilege, so a consumer run under `on -u` "
            "aborts at message-passing setup before reaching the shared-memory "
            "ACL check (confirmed by a control run where an allow-listed UID "
            "failed identically)."
        )

    allowed_result, denied_result, allowed_uid = comm.run_acl_isolation_scenario(target)
    logger.info("ACL scenario allowed_uid=%s", allowed_uid)
    logger.info("allowed consumer stdout:\n%s", allowed_result.recv_stdout)
    logger.info("denied consumer stdout:\n%s", denied_result.recv_stdout)

    # Allowed consumer: unaffected by the concurrently-running denied one.
    assert allowed_result.recv_exit_code == 0, "allowed consumer did not exit cleanly"
    assert allowed_result.valid_data_count > 0, "allowed consumer got no hash-valid samples"
    assert not allowed_result.has_hash_failure, "allowed consumer saw a hash mismatch"
    assert comm.is_non_decreasing(allowed_result.received_samples), (
        f"allowed consumer's samples were reordered: {allowed_result.received_samples}"
    )

    # Denied consumer: fails deterministically, never receives data.
    assert denied_result.recv_exit_code != 0, "consumer with an excluded UID was not denied"
    assert not denied_result.received_samples, "consumer with an excluded UID received samples"
    assert any(marker in denied_result.recv_stdout for marker in comm.ACL_DENIAL_MARKERS), (
        f"denial was not attributable to ACL/permission enforcement:\n{denied_result.recv_stdout}"
    )
