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

Upstream ships only the single-process ``com-api-example`` demo, which cannot
exercise producer/consumer as separate processes. Per the maintainer's
guidance these tests drive our own two-process scenario
(``showcases/standalone/comm_fit``: ``fit_sender`` + ``fit_receiver``) over
real shared memory and assert on the data the consumer actually observes --
sequence and value-integrity -- rather than on log strings the application
prints about its own configuration.

Scope is deliberately kept small and high-value (delivery, ordering,
integrity, service discovery, runtime deployment config, late join). Detailed
safety guarantees (ASIL-B/ACL isolation, bad-config fault handling) are
verified in the communication module's own unit/component tests and are not
re-derived here.
"""

import logging

import comm_helpers as comm
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
