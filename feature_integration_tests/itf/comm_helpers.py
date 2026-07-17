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


# --------------------------------------------------------------------------
# Deployment-configuration integrity (negative scenarios)
# --------------------------------------------------------------------------
#
# fit_receiver's own contract (fit_receiver.rs) is: a config that cannot be
# loaded or resolves to no service instances must never let the process hang
# or silently look like success -- it must exit non-zero, bounded in time,
# and never reach FIT_FOUND_SERVICE. That is what these tests check. Unlike
# the removed ipc_bridge example (whose C++ config parser used assert() and
# so failed via SIGABRT), the exact underlying failure mode of the Rust
# `com_api` runtime builder is intentionally NOT asserted on here -- only the
# black-box contract is.

# Deliberately malformed: not valid JSON at all.
TRUNCATED_CONFIG_JSON = '{ "serviceTypes": [ { "serviceTypeName"'

# Deliberately incomplete: valid JSON, but missing the required
# "serviceTypes"/"serviceInstances" structure the schema demands.
SCHEMA_INVALID_CONFIG_JSON = "{}"


def write_remote_file(target, path: str, content: str) -> None:
    """Write ``content`` to ``path`` on the target via a quoted heredoc."""
    heredoc = f"cat > {path} <<'COMM_FIT_EOF'\n{content}\nCOMM_FIT_EOF\n"
    exit_code, out = target.execute(heredoc)
    if exit_code != 0:
        raise AssertionError(f"Failed to write {path} on target: {out!r}")


def run_receiver_with_manifest(
    target,
    manifest_path: str,
    cycles: int = 3,
    interval_ms: int = 100,
    max_polls: int = 10,
    timeout_s: int = 10,
) -> CommResult:
    """
    Run only the receiver against ``manifest_path``, bounded by a shell
    ``timeout`` so an unexpected hang while loading the config cannot block the
    test suite. Used for negative config scenarios where no producer is
    started -- the receiver is expected to fail before ever discovering a
    service.
    """
    recv_log = "/tmp/fit_recv_negative.log"
    command = (
        f"cd {COMM_CWD} && rm -f {recv_log} && "
        f"timeout {timeout_s} {FIT_RECEIVER_BIN} -n {cycles} -t {interval_ms} "
        f"--max-polls {max_polls} -s {manifest_path} > {recv_log} 2>&1 ; echo RECV_EXIT=$?"
    )
    _, out = target.execute(command)
    recv_exit_code = _shell_exit_marker(out.decode(errors="replace"))
    _, recv_bytes = target.execute(f"cat {recv_log}")
    return CommResult(
        recv_exit_code=recv_exit_code,
        recv_stdout=recv_bytes.decode(errors="replace"),
        send_stdout="",
    )


# --------------------------------------------------------------------------
# Mixed-criticality safety & isolation (ASIL-B ACL enforcement)
# --------------------------------------------------------------------------
#
# LoLa's `allowedConsumer`/`allowedProvider` ACLs are enforced via POSIX ACLs
# on the shared-memory objects the provider creates, gated by the real
# process UID of the consumer/provider -- this is the same enforcement point
# already exercised (and documented) for the now-removed ipc_bridge example:
#
#   1. It is the PROVIDER's config that is authoritative (its allowedConsumer
#      list decides who may open the SHM object) -- a consumer's own config
#      does not self-restrict what it may read.
#   2. Enforcement requires distinct real UIDs -- running "denied" and
#      "allowed" consumers under the same UID proves nothing, because the
#      excluded UID is never actually attempted.
#
# fit_receiver's discover_consumer() swallows a denied proxy-construction
# error into a retry-then-give-up loop (see fit_receiver.rs), so a denied
# consumer surfaces identically to "no service found": non-zero exit,
# FIT_FOUND_SERVICE never printed, no samples received. That is what is
# asserted here; the exact underlying error text is not, since it depends on
# the Rust `com_api` FFI error formatting.
#
# Getting a second real UID needs `on -u <uid>:<gid>` on QNX (no /etc/passwd
# entry required) or `setpriv --reuid=<uid> --regid=<uid>` on Linux (needs
# root or CAP_SETUID, i.e. it works if the ITF target container already runs
# as root, mirroring how test_remote_logging.py starts datarouter without
# invoking sudo).
#
# This SHM-open denial signature is only reachable on Linux. On QNX, a
# consumer launched under a lower-privilege UID aborts earlier, at
# MessagePassingService endpoint registration ("Failed to start listening ...
# Operation not permitted"), because that registration itself requires
# privilege -- so an excluded UID never reaches the SHM-open ACL. The
# isolation test therefore skips on QNX (see is_qnx()), matching the
# limitation already documented and observed for ipc_bridge.

ASILB_INSTANCE_SPECIFIER = "/Vehicle/ServiceAcl/Instance"
DENIED_CONSUMER_UID = 64000

# Reuses the VehicleInterface service type (serviceId / event ids) that
# com-api-gen bakes in, so fit_sender/fit_receiver can still bind against it;
# only the service *instance* below is new, with a dedicated ASIL-B binding
# and a restrictive allowedConsumer/allowedProvider list.
ASILB_CONFIG_TEMPLATE = """{{
  "serviceTypes": [
    {{
      "serviceTypeName": "/bmw/adp/VehicleInterface",
      "version": {{"major": 1, "minor": 0}},
      "bindings": [
        {{
          "binding": "SHM",
          "serviceId": 6433,
          "events": [
            {{"eventName": "left_tire", "eventId": 1}},
            {{"eventName": "exhaust", "eventId": 2}}
          ]
        }}
      ]
    }}
  ],
  "global": {{"applicationID": 4099}},
  "serviceInstances": [
    {{
      "instanceSpecifier": "{instance_specifier}",
      "serviceTypeName": "/bmw/adp/VehicleInterface",
      "version": {{"major": 1, "minor": 0}},
      "instances": [
        {{
          "instanceId": 9,
          "allowedConsumer": {{"B": [{allowed_uid}], "QM": [{allowed_uid}]}},
          "allowedProvider": {{"B": [{allowed_uid}], "QM": [{allowed_uid}]}},
          "asil-level": "B",
          "binding": "SHM",
          "events": [
            {{"eventName": "left_tire", "numberOfSampleSlots": 30, "maxSubscribers": 5}},
            {{"eventName": "exhaust", "numberOfSampleSlots": 30, "maxSubscribers": 5}}
          ]
        }}
      ]
    }}
  ]
}}"""


def render_asilb_config(allowed_uid: int) -> str:
    """ASIL-B manifest granting only ``allowed_uid`` (not DENIED_CONSUMER_UID)."""
    return ASILB_CONFIG_TEMPLATE.format(
        instance_specifier=ASILB_INSTANCE_SPECIFIER,
        allowed_uid=allowed_uid,
    )


def discover_default_uid(target) -> int:
    """The real UID `target.execute` commands run as by default."""
    _, out = target.execute("id -u")
    return int(out.decode(errors="replace").strip())


def is_qnx(target) -> bool:
    """Same detection approach as test_remote_logging.py's `_is_qnx`."""
    _, out = target.execute("uname -s")
    return b"QNX" in out


def as_uid_prefix(target, uid: int) -> str:
    """
    Shell prefix that re-executes the following command under ``uid``.

    QNX: `on -u <uid>:<gid>` needs no /etc/passwd entry.
    Linux: `setpriv` needs CAP_SETUID (i.e. running as root), the same
    privilege level the Linux ITF container already runs at.
    """
    if is_qnx(target):
        return f"on -u {uid}:{uid} "
    return f"setpriv --reuid={uid} --regid={uid} --clear-groups "


def run_acl_isolation_scenario(
    target,
    send_cycles: int = 40,
    recv_cycles: int = 8,
    interval_ms: int = 150,
    startup_delay_s: int = 1,
):
    """
    Run an ASIL-B producer, one consumer with an allowed UID, and one
    consumer with a UID deliberately excluded from the ACL, all running
    concurrently against the same instance.

    Returns (allowed_result, denied_result, allowed_uid).
    """
    allowed_uid = discover_default_uid(target)
    manifest_path = "/tmp/comm_fit_asilb_config.json"
    write_remote_file(target, manifest_path, render_asilb_config(allowed_uid))

    send_log = "/tmp/fit_acl_send.log"
    allowed_log = "/tmp/fit_acl_recv_allowed.log"
    denied_log = "/tmp/fit_acl_recv_denied.log"
    denied_prefix = as_uid_prefix(target, DENIED_CONSUMER_UID)

    # As in run_event_exchange, capture the producer PID and kill it after both
    # consumers finish so it does not leak onto the shared target.
    command = (
        f"cd {COMM_CWD} && rm -f {send_log} {allowed_log} {denied_log} && "
        f"chmod 666 {manifest_path} && "
        f"{{ {FIT_SENDER_BIN} -n {send_cycles} -t {interval_ms} -s {manifest_path} "
        f"-i {ASILB_INSTANCE_SPECIFIER} > {send_log} 2>&1 & SEND_PID=$!; }} && "
        f"sleep {startup_delay_s} && "
        f"( {FIT_RECEIVER_BIN} -n {recv_cycles} -t {interval_ms} -s {manifest_path} "
        f"-i {ASILB_INSTANCE_SPECIFIER} > {allowed_log} 2>&1 & ALLOWED_PID=$! ; "
        f"{denied_prefix}timeout 8 {FIT_RECEIVER_BIN} -n {recv_cycles} -t {interval_ms} "
        f"--max-polls 20 -s {manifest_path} -i {ASILB_INSTANCE_SPECIFIER} "
        f"> {denied_log} 2>&1 ; DENIED_EXIT=$? ; "
        f"wait $ALLOWED_PID ; ALLOWED_EXIT=$? ; "
        f"echo ALLOWED_EXIT=$ALLOWED_EXIT ; echo DENIED_EXIT=$DENIED_EXIT ) ; "
        f"kill $SEND_PID 2>/dev/null ; wait $SEND_PID 2>/dev/null"
    )
    _, out = target.execute(command)
    decoded = out.decode(errors="replace")
    allowed_exit = _shell_exit_marker(decoded, "ALLOWED_EXIT")
    denied_exit = _shell_exit_marker(decoded, "DENIED_EXIT")

    _, allowed_bytes = target.execute(f"cat {allowed_log}")
    _, denied_bytes = target.execute(f"cat {denied_log}")

    allowed_result = CommResult(
        recv_exit_code=allowed_exit,
        recv_stdout=allowed_bytes.decode(errors="replace"),
        send_stdout="",
    )
    denied_result = CommResult(
        recv_exit_code=denied_exit,
        recv_stdout=denied_bytes.decode(errors="replace"),
        send_stdout="",
    )
    return allowed_result, denied_result, allowed_uid
