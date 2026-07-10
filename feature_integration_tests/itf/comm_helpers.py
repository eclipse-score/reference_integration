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
Helpers for the communication (LoLa / mw::com) feature integration tests.

The checks in this module are derived from observable data produced by the
deployed ipc_bridge example, not from strings the application echoes about
its own configuration. The ipc_bridge receiver:

  * prints ``<instance>: Received sample: <x>`` for every sample it consumes,
    where ``x`` is the producer's monotonically increasing cycle counter;
  * prints ``<instance>: Proxy received valid data`` when the per-sample
    FNV-1a hash recomputed by the receiver matches the transmitted hash; and
  * prints ``... hash comparison failed ...`` when it does not.

These give us independent oracles for delivery, ordering and integrity that a
regression in the middleware would actually break.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

# Deployment layout of the communication showcase inside the reference image
# (matches feature_integration_tests/itf/test_showcases.py and
# showcases/standalone/{BUILD,com.score.json}).
IPC_BRIDGE_BIN = "/showcases/bin/ipc_bridge_cpp"
COMM_CWD = "/showcases/data/comm"

# Hard-coded in the ipc_bridge (score/mw/com/example/ipc_bridge/main.cpp).
INSTANCE_SPECIFIER = "score/cp60/MapApiLanesStamped"

# Oracle strings emitted by score/mw/com/example/ipc_bridge/sample_sender_receiver.cpp
RECEIVED_SAMPLE_RE = re.compile(r"Received sample:\s*(\d+)")
VALID_DATA_MARKER = "Proxy received valid data"
HASH_FAILURE_MARKER = "hash comparison failed"
FOUND_SERVICE_MARKER = "Found service"


@dataclass
class CommResult:
    """Captured output of one producer/consumer exchange."""

    recv_exit_code: int
    recv_stdout: str
    send_stdout: str

    # --- oracles ---------------------------------------------------------
    @property
    def received_samples(self) -> List[int]:
        """Ordered list of the producer cycle numbers the consumer received."""
        return [int(m.group(1)) for m in RECEIVED_SAMPLE_RE.finditer(self.recv_stdout)]

    @property
    def valid_data_count(self) -> int:
        """How many times the receiver confirmed a hash-valid sample cycle."""
        return self.recv_stdout.count(VALID_DATA_MARKER)

    @property
    def has_hash_failure(self) -> bool:
        """True if the receiver detected corrupted (hash-mismatched) data."""
        return HASH_FAILURE_MARKER in self.recv_stdout

    @property
    def found_service(self) -> bool:
        """True if service discovery located the offered instance."""
        return FOUND_SERVICE_MARKER in self.recv_stdout


def is_non_decreasing(seq: List[int]) -> bool:
    """No reordering: each received cycle number is >= the previous one."""
    return all(b >= a for a, b in zip(seq, seq[1:]))


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
    cycle_time_ms: int = 100,
    startup_delay_s: int = 1,
    hash_check: bool = True,
    manifest: str | None = None,
) -> CommResult:
    """
    Run one producer/consumer exchange on ``target`` and return parsed output.

    The producer is started first (in the background) with enough cycles to
    outlast the consumer. The consumer's ``FindService`` *does* retry (a 500ms
    poll loop in ``GetHandleFromSpecifier``, sample_sender_receiver.cpp) but the
    producer is still started first so the consumer binds promptly and the run
    stays bounded by ``-n`` and the ITF execution timeout — so a delivery
    failure surfaces as a timeout rather than a silent under-count.

    ``manifest`` optionally points both roles at a deployment config at an
    explicit on-target path via ``-s``; when ``None`` the app resolves its
    default ``./etc/mw_com_config.json`` relative to ``COMM_CWD``.
    """
    send_log = "/tmp/comm_send.log"
    recv_log = "/tmp/comm_recv.log"
    recv_extra = "" if hash_check else " -d"
    manifest_arg = f" -s {manifest}" if manifest else ""

    command = (
        f"cd {COMM_CWD} && rm -f {send_log} {recv_log} && "
        f"( {IPC_BRIDGE_BIN} -n {send_cycles} -t {cycle_time_ms} -m send{manifest_arg} "
        f"> {send_log} 2>&1 & ) && "
        f"sleep {startup_delay_s} && "
        f"{IPC_BRIDGE_BIN} -n {recv_cycles} -t {cycle_time_ms} -m recv{recv_extra}{manifest_arg} "
        f"> {recv_log} 2>&1 ; echo RECV_EXIT=$?"
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
# A bad deployment config is not surfaced as a recoverable score::Result: the
# config parser (score/mw/com/impl/configuration/config_parser.cpp) uses
# `assert()` on parse/schema failure, which aborts the process with SIGABRT
# (shell-visible exit code 134) and a core dump -- for a missing file,
# truncated JSON, and a schema-invalid JSON alike.
#
# This is a fail-fast/terminate contract for config errors, distinct from the
# score::Result idiom used for runtime errors elsewhere in the API. These
# tests lock in that observed contract so a regression into an uncontrolled
# hang or a silent success would be caught.

# Deliberately malformed: not valid JSON at all.
TRUNCATED_CONFIG_JSON = '{ "serviceTypes": [ { "serviceTypeName"'

# Deliberately incomplete: valid JSON, but missing the required
# "serviceTypes"/"serviceInstances" structure the schema demands.
SCHEMA_INVALID_CONFIG_JSON = "{}"

# Markers observed in the actual fatal-log output for a config load failure
# (score/mw/com/impl/configuration/config_parser.cpp). Used as evidence that
# the process failed *because of the config*, not for some unrelated reason.
CONFIG_FAILURE_MARKERS = (
    "Parsing config file",
    "Invalid json encountered",
    "Configuration corrupted",
    "Assertion",
)

# Shell exit code for a process terminated by SIGABRT (128 + 6), as observed
# via `<cmd>; echo EXIT=$?` — consistent with how run_event_exchange() and
# the tests in this module capture exit codes.
SIGABRT_SHELL_EXIT_CODE = 134


def write_remote_file(target, path: str, content: str) -> None:
    """Write ``content`` to ``path`` on the target via a quoted heredoc."""
    heredoc = f"cat > {path} <<'COMM_FIT_EOF'\n{content}\nCOMM_FIT_EOF\n"
    exit_code, out = target.execute(heredoc)
    if exit_code != 0:
        raise AssertionError(f"Failed to write {path} on target: {out!r}")


def run_consumer_with_manifest(
    target,
    manifest_path: str,
    cycles: int = 3,
    cycle_time_ms: int = 100,
    timeout_s: int = 5,
) -> CommResult:
    """
    Run only the consumer role against ``manifest_path`` and return its
    output. Used for negative config scenarios where no producer should ever
    need to be reached (the process is expected to fail during config load,
    before service discovery).
    """
    recv_log = "/tmp/comm_recv_negative.log"
    command = (
        f"cd {COMM_CWD} && rm -f {recv_log} && "
        f"timeout {timeout_s} {IPC_BRIDGE_BIN} -n {cycles} -t {cycle_time_ms} "
        f"-m recv -s {manifest_path} > {recv_log} 2>&1 ; echo RECV_EXIT=$?"
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
# (score::os::Acl, score/mw/com/impl/bindings/lola/skeleton_memory_manager.cpp)
# on the shared-memory objects the provider creates, gated by the real
# process UID of the consumer/provider:
#
#   1. It is the PROVIDER's config that is authoritative (its allowedConsumer
#      list decides who may open the SHM object) — a consumer's own config
#      does not self-restrict what it may read.
#   2. Enforcement requires distinct real UIDs — running "denied" and
#      "allowed" consumers under the same UID (e.g. two configs differing
#      only in their allow-lists, run as one local user) proves nothing,
#      because the excluded UID is never actually attempted.
#
# Denial signature (uid excluded from allowedConsumer.B): exit code 1 (a
# controlled EXIT_FAILURE via the score::Result-mediated runtime error path,
# distinct from the assert()-based config-parse error path above), plus
# "Permission denied" opening the SHM object and "Unable to construct proxy:
# ... bailing!". Discovery still succeeds first ("Found service, instantiating
# proxy") -- the ACL is enforced at SHM-open time, not at discovery time.
#
# Getting a second real UID needs `on -u <uid>:<gid>` on QNX (no /etc/passwd
# entry required) or `setpriv --reuid=<uid> --regid=<uid>` on Linux (needs
# root or CAP_SETUID, i.e. it works if the ITF target container already runs
# as root, mirroring how test_remote_logging.py starts datarouter without
# invoking sudo).

DENIED_CONSUMER_UID = 64000

ASILB_CONFIG_TEMPLATE = """{{
  "serviceTypes": [
    {{
      "serviceTypeName": "/score/adp/MapApiLanesStamped",
      "version": {{"major": 1, "minor": 0}},
      "bindings": [
        {{
          "binding": "SHM",
          "serviceId": 6432,
          "events": [
            {{"eventName": "map_api_lanes_stamped", "eventId": 1}},
            {{"eventName": "dummy_data_stamped", "eventId": 2}}
          ]
        }}
      ]
    }}
  ],
  "serviceInstances": [
    {{
      "instanceSpecifier": "score/cp60/MapApiLanesStamped",
      "serviceTypeName": "/score/adp/MapApiLanesStamped",
      "version": {{"major": 1, "minor": 0}},
      "instances": [
        {{
          "instanceId": 1,
          "allowedConsumer": {{"B": [{allowed_uid}], "QM": [{allowed_uid}]}},
          "allowedProvider": {{"B": [{allowed_uid}], "QM": [{allowed_uid}]}},
          "asil-level": "B",
          "binding": "SHM",
          "events": [
            {{"eventName": "map_api_lanes_stamped", "numberOfSampleSlots": 30, "maxSubscribers": 5}}
          ]
        }}
      ]
    }}
  ],
  "global": {{"asil-level": "B"}}
}}"""

ACL_DENIAL_MARKERS = (
    "Permission denied",
    "Could not create Proxy",
    "Unable to construct proxy",
)


def render_asilb_config(allowed_uid: int) -> str:
    """ASIL-B manifest granting only ``allowed_uid`` (not DENIED_CONSUMER_UID)."""
    return ASILB_CONFIG_TEMPLATE.format(allowed_uid=allowed_uid)


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

    QNX: `on -u <uid>:<gid>` needs no /etc/passwd entry, matching the
    datarouter fixture in test_remote_logging.py which uses an unregistered
    1051:1091. This path has not yet been exercised on real QNX hardware.

    Linux: `setpriv` needs CAP_SETUID (i.e. running as root), the same
    privilege level test_remote_logging.py already assumes for the Linux ITF
    container (it starts datarouter and edits routes without invoking sudo).
    """
    if is_qnx(target):
        return f"on -u {uid}:{uid} "
    return f"setpriv --reuid={uid} --regid={uid} --clear-groups "


def run_acl_isolation_scenario(
    target,
    send_cycles: int = 40,
    recv_cycles: int = 8,
    cycle_time_ms: int = 150,
    startup_delay_s: int = 1,
):
    """
    Run an ASIL-B provider, one consumer with an allowed UID, and one
    consumer with a UID deliberately excluded from the ACL, all running
    concurrently against the same instance.

    Returns (allowed_result, denied_result, allowed_uid).
    """
    allowed_uid = discover_default_uid(target)
    manifest_path = "/tmp/comm_fit_asilb_config.json"
    write_remote_file(target, manifest_path, render_asilb_config(allowed_uid))

    send_log = "/tmp/comm_acl_send.log"
    allowed_log = "/tmp/comm_acl_recv_allowed.log"
    denied_log = "/tmp/comm_acl_recv_denied.log"
    denied_prefix = as_uid_prefix(target, DENIED_CONSUMER_UID)

    command = (
        f"cd {COMM_CWD} && rm -f {send_log} {allowed_log} {denied_log} && "
        f"chmod 666 {manifest_path} && "
        f"( {IPC_BRIDGE_BIN} -n {send_cycles} -t {cycle_time_ms} -m send -s {manifest_path} "
        f"> {send_log} 2>&1 & ) && "
        f"sleep {startup_delay_s} && "
        f"( {IPC_BRIDGE_BIN} -n {recv_cycles} -t {cycle_time_ms} -m recv -s {manifest_path} "
        f"> {allowed_log} 2>&1 & ALLOWED_PID=$! ; "
        f"{denied_prefix}timeout 8 {IPC_BRIDGE_BIN} -n {recv_cycles} -t {cycle_time_ms} -m recv "
        f"-s {manifest_path} > {denied_log} 2>&1 ; DENIED_EXIT=$? ; "
        f"wait $ALLOWED_PID ; ALLOWED_EXIT=$? ; "
        f"echo ALLOWED_EXIT=$ALLOWED_EXIT ; echo DENIED_EXIT=$DENIED_EXIT )"
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
