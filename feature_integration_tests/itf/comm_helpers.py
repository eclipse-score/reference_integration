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
"""Helpers for the communication (LoLa / mw::com) ITF tests."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

FIT_SENDER_BIN = "/showcases/bin/fit_sender"
FIT_RECEIVER_BIN = "/showcases/bin/fit_receiver"
FIT_SENDER_CC_BIN = "/showcases/bin/fit_sender_cc"
FIT_RECEIVER_CC_BIN = "/showcases/bin/fit_receiver_cc"
COMM_CWD = "/showcases/data/comm"
DEFAULT_MANIFEST = "/showcases/data/comm/etc/mw_com_config.json"

RECV_SAMPLE_RE = re.compile(r"FIT_RECV seq=(\S+)")
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
        """Ordered sequence numbers received; non-integer tokens fail (corruption guard)."""
        tokens = RECV_SAMPLE_RE.findall(self.recv_stdout)
        for token in tokens:
            assert token.isdigit(), f"non-integer sequence token (corruption): {token!r} in {tokens}"
        return [int(token) for token in tokens]

    @property
    def found_service(self) -> bool:
        """True if service discovery located the offered instance."""
        return FOUND_SERVICE_MARKER in self.recv_stdout

    @property
    def completed(self) -> bool:
        """True if the receiver consumed all requested samples and exited cleanly."""
        return RECV_DONE_MARKER in self.recv_stdout



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
    instance_specifier: str | None = None,
    sender_bin: str | None = None,
    receiver_bin: str | None = None,
) -> CommResult:
    """Run one producer/consumer exchange on ``target`` and return parsed output."""
    manifest_path = manifest or DEFAULT_MANIFEST
    instance_arg = f" -i {instance_specifier}" if instance_specifier else ""
    sender = sender_bin or FIT_SENDER_BIN
    receiver = receiver_bin or FIT_RECEIVER_BIN
    send_log = "/tmp/fit_send.log"
    recv_log = "/tmp/fit_recv.log"

    command = (
        f"cd {COMM_CWD} && rm -f {send_log} {recv_log} && "
        f"{{ {sender} -n {send_cycles} -t {interval_ms} -s {manifest_path}{instance_arg} "
        f"> {send_log} 2>&1 & SEND_PID=$!; }} && "
        f"sleep {startup_delay_s} && "
        f"{receiver} -n {recv_cycles} -t {interval_ms} -s {manifest_path}{instance_arg} "
        f"> {recv_log} 2>&1 ; RECV_RC=$? ; "
        f"kill $SEND_PID 2>/dev/null ; wait $SEND_PID 2>/dev/null ; "
        f"echo RECV_EXIT=$RECV_RC"
    )
    logger.info("running command:\n%s", command)
    _, out = target.execute(command)
    recv_exit_code = _shell_exit_marker(out.decode(errors="replace"))

    _, recv_bytes = target.execute(f"cat {recv_log}")
    _, send_bytes = target.execute(f"cat {send_log}")

    return CommResult(
        recv_exit_code=recv_exit_code,
        recv_stdout=recv_bytes.decode(errors="replace"),
        send_stdout=send_bytes.decode(errors="replace"),
    )


TRUNCATED_CONFIG_JSON = '{ "serviceTypes": [ { "serviceTypeName"'
SCHEMA_INVALID_CONFIG_JSON = "{}"
# Distinct instance specifier so a misconfigured receiver cannot latch onto leftover SHM state.
NEGATIVE_CONFIG_INSTANCE_SPECIFIER = "/Vehicle/ServiceNegativeConfigTest/Instance"


def write_remote_file(target, path: str, content: str) -> None:
    """Write ``content`` to ``path`` on the target via a quoted heredoc."""
    heredoc = f"cat > {path} <<'COMM_FIT_EOF'\n{content}\nCOMM_FIT_EOF\n"
    logger.info("writing remote file: %s", path)
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
    instance_specifier: str = NEGATIVE_CONFIG_INSTANCE_SPECIFIER,
    receiver_bin: str | None = None,
) -> CommResult:
    """Run only the receiver against ``manifest_path``; no producer started (negative-config scenarios)."""
    receiver = receiver_bin or FIT_RECEIVER_BIN
    recv_log = "/tmp/fit_recv_negative.log"
    command = (
        f"cd {COMM_CWD} && rm -f {recv_log} && "
        f"timeout {timeout_s} {receiver} -n {cycles} -t {interval_ms} "
        f"--max-polls {max_polls} -s {manifest_path} -i {instance_specifier} "
        f"> {recv_log} 2>&1 ; echo RECV_EXIT=$?"
    )
    logger.info("running command:\n%s", command)
    _, out = target.execute(command)
    recv_exit_code = _shell_exit_marker(out.decode(errors="replace"))
    _, recv_bytes = target.execute(f"cat {recv_log}")
    return CommResult(
        recv_exit_code=recv_exit_code,
        recv_stdout=recv_bytes.decode(errors="replace"),
        send_stdout="",
    )


ASILB_INSTANCE_SPECIFIER = "/Vehicle/ServiceAcl/Instance"

# ACL denial surfaces as a panic in the generated bindings (ProxyCreationFailed),
# not as an Err from build() — so we match LoLa's own log strings, not just exit code.
ACL_DENIAL_MARKERS = (
    "FIT_RECV_PROXY_BUILD_ERROR",
    "Could not create Proxy",
    "ProxyCreationFailed",
)
DENIED_CONSUMER_UID = 64000

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
  "global": {{"applicationID": 4099, "asil-level": "B"}},
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
    logger.info("running command:\n%s", command)
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
