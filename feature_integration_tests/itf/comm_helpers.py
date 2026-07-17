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
Helpers for the communication (LoLa / mw::com) ITF tests.

Upstream replaced the two-process ``ipc_bridge`` example with the
single-process ``com-api-example`` demo, which cannot act as separate
producer/consumer processes. Per the maintainer's guidance we therefore ship
our own sender/receiver scenario (``showcases/standalone/comm_fit``): two
distinct binaries that offer and subscribe to the same ``VehicleInterface``
service instance over real shared memory.

The checks here are derived from observable data the receiver produces, not
from strings the app echoes about its own configuration. ``fit_sender``
publishes ``left_tire`` samples whose payload carries a monotonically
increasing sequence number; ``fit_receiver`` prints one ``FIT_RECV seq=<n>``
line per consumed sample. That gives independent oracles for delivery,
ordering and value-integrity that a middleware regression would break.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Deployment layout of the communication FIT binaries inside the reference
# image (see showcases/standalone/comm_fit/BUILD and showcases/BUILD). The
# deployment manifest is the one deployed by the com-api-example bundle
# (showcases/standalone/BUILD), which fit_sender/fit_receiver reuse.
FIT_SENDER_BIN = "/showcases/bin/fit_sender"
FIT_RECEIVER_BIN = "/showcases/bin/fit_receiver"
COMM_CWD = "/showcases/data/comm"
DEFAULT_MANIFEST = "/showcases/data/comm/etc/mw_com_config.json"

# Oracle strings emitted by fit_sender / fit_receiver.
RECV_SAMPLE_RE = re.compile(r"FIT_RECV seq=(\d+)")
FOUND_SERVICE_MARKER = "FIT_FOUND_SERVICE"
RECV_DONE_MARKER = "FIT_RECV_DONE"


@dataclass
class CommResult:
    """Captured output of one producer/consumer exchange."""

    recv_exit_code: int
    recv_stdout: str
    send_stdout: str

    # --- oracles ---------------------------------------------------------
    @property
    def received_samples(self) -> list[int]:
        """Ordered list of the producer sequence numbers the consumer received."""
        return [int(m.group(1)) for m in RECV_SAMPLE_RE.finditer(self.recv_stdout)]

    @property
    def found_service(self) -> bool:
        """True if service discovery located the offered instance."""
        return FOUND_SERVICE_MARKER in self.recv_stdout

    @property
    def completed(self) -> bool:
        """True if the receiver consumed all requested samples and exited cleanly."""
        return RECV_DONE_MARKER in self.recv_stdout


def is_non_decreasing(seq: list[int]) -> bool:
    """No reordering: each received sequence number is >= the previous one."""
    return all(b >= a for a, b in zip(seq, seq[1:]))


def samples_are_intact(seq: list[int], send_cycles: int) -> bool:
    """
    Value-integrity: every received sequence number is one the sender actually
    produced (0 .. send_cycles-1). A corrupted payload would decode to a value
    outside that range.
    """
    return all(0 <= s < send_cycles for s in seq)


def _shell_exit_marker(out: str, marker: str = "RECV_EXIT") -> int:
    """Extract ``<marker>=<int>`` printed by the exchange command."""
    m = re.search(rf"{marker}=(-?\d+)", out)
    if m is None:
        raise AssertionError(f"Could not find {marker}= in command output:\n{out}")
    return int(m.group(1))


def run_event_exchange(
    target,
    send_cycles: int = 50,
    recv_cycles: int = 10,
    interval_ms: int = 100,
    startup_delay_s: int = 1,
    manifest: str | None = None,
) -> CommResult:
    """
    Run one producer/consumer exchange on ``target`` and return parsed output.

    The producer (fit_sender) is started first in the background with enough
    cycles to outlast the consumer (fit_receiver). The consumer retries service
    discovery, so start order is not critical, but starting the producer first
    keeps the run bounded by ``recv_cycles`` and the receiver's ``--max-polls``.
    The producer's PID is captured and killed once the consumer finishes so it
    never leaks onto the shared target and collides with the next test (two
    providers offering the same instance would make the next consumer hang).

    ``manifest`` points both roles at a deployment config via ``-s``; when
    ``None`` the deployed default (``DEFAULT_MANIFEST``) is used.
    """
    manifest_path = manifest or DEFAULT_MANIFEST
    send_log = "/tmp/fit_send.log"
    recv_log = "/tmp/fit_recv.log"

    command = (
        f"cd {COMM_CWD} && rm -f {send_log} {recv_log} && "
        f"{{ {FIT_SENDER_BIN} -n {send_cycles} -t {interval_ms} -s {manifest_path} "
        f"> {send_log} 2>&1 & SEND_PID=$!; }} && "
        f"sleep {startup_delay_s} && "
        f"{FIT_RECEIVER_BIN} -n {recv_cycles} -t {interval_ms} -s {manifest_path} "
        f"> {recv_log} 2>&1 ; RECV_RC=$? ; "
        f"kill $SEND_PID 2>/dev/null ; wait $SEND_PID 2>/dev/null ; "
        f"echo RECV_EXIT=$RECV_RC"
    )
    _, out = target.execute(command)
    recv_exit_code = _shell_exit_marker(out.decode(errors="replace"))

    _, recv_bytes = target.execute(f"cat {recv_log}")
    _, send_bytes = target.execute(f"cat {send_log}")

    return CommResult(
        recv_exit_code=recv_exit_code,
        recv_stdout=recv_bytes.decode(errors="replace"),
        send_stdout=send_bytes.decode(errors="replace"),
    )
