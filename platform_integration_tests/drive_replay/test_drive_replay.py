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
"""Platform integration test for the drive replay demo.

The scripted showcase (``showcases/drive_replay``) runs a highway drive into the
forward collision warning under the launch manager, makes ``warn_app`` hang after
20 s and crashes it after 45 s, then stops the launch manager. The test records
the DLT traffic on the host and checks the whole chain: the drive and the warning
over mw::com, the health monitor detecting the hang, the launch manager switching
to the degraded Run Target, the state manager restoring ``Drive`` and the
restarted ``warn_app`` restoring its counters from the persistency KVS. The
recording is kept as ``drive_replay.dlt`` in the test's undeclared outputs.
"""

import os
import re
from pathlib import Path

from attribute_plugin import add_test_properties
from score.itf.plugins.dlt.dlt_receive import Protocol
from score.itf.plugins.dlt.dlt_window import DltWindow
from showcase_runner import run_showcases

SHOWCASE = "Drive Replay Demo (scripted, ~65 s)"

_MULTICAST_ROUTE_CMD = "ip route add 224.0.0.0/4 dev eth0 2>/dev/null || true"

_FAULT_INJECTED = ("FCW", "FCW", r"FAULT INJECTED")
_SUPERVISION_FAILED = ("LM", "LM", r"Alive Supervision\s*\(\s*warn_app\s*\)\s*switched to FAILED")

# (app id, context id, payload pattern, (min, max) count; max None = unbounded)
EXPECTED_DLT = [
    ("DR", "DFLT", r"successfully completed initialization", (1, None)),
    ("RPLY", "DRV", r"offering score/showcases/drive_replay/DriveData via mw::com", (1, 1)),
    ("RPLY", "DRV", r"lead vehicle brakes hard", (1, None)),
    ("FCW", "FCW", r"subscribed to frames", (3, 3)),
    ("FCW", "FCW", r"FORWARD COLLISION WARNING", (1, None)),
    ("FCW", "FCW", r"CRITICAL, brake now", (1, None)),
    (*_FAULT_INJECTED, (1, 1)),
    (*_SUPERVISION_FAILED, (1, None)),
    # one recovery for the hang, one for the crash; a spontaneous supervision failure adds a third
    ("LM", "LM", r"Completed the request for Run Target\s+fallback_run_target", (2, 2)),
    ("DSM", "SM", r"launch manager recovered a failure", (2, 2)),
    ("DSM", "SM", r"requesting Run Target 'Drive'", (2, 2)),
    ("LM", "LM", r"Completed the request for Run Target\s+Drive", (3, 3)),
    ("FCW", "FCW", r"started \(start #1\), restored warn_count=0 ", (1, 1)),
    ("FCW", "FCW", r"started \(start #3\), restored warn_count=[1-9]", (1, 1)),
]

FORBIDDEN_DLT = [
    ("LM", "LM", r"did not meet its ready condition"),
    ("DSM", "SM", r"Run Target request rejected"),
    ("FCW", "FCW", r"^cannot "),
    ("RPLY", "DRV", r"could not be sent"),
]


def _find(record, apid: str, ctid: str, pattern: str) -> list:
    return record.find(query={"apid": apid, "ctid": ctid, "payload_decoded": re.compile(pattern)}, full_match=True)


def analyze_dlt(record) -> list[str]:
    """Findings in the recorded DLT traffic: expected messages with their counts,
    no forbidden message, and no supervision failure before the injected hang."""
    findings = []
    for apid, ctid, pattern, (minimum, maximum) in EXPECTED_DLT:
        count = len(_find(record, apid, ctid, pattern))
        if count < minimum or (maximum is not None and count > maximum):
            expected = f"{minimum}..{'' if maximum is None else maximum}"
            findings.append(f"DLT {apid}/{ctid} '{pattern}': {count} message(s), expected {expected}")
    for apid, ctid, pattern in FORBIDDEN_DLT:
        for msg in _find(record, apid, ctid, pattern):
            findings.append(f"forbidden DLT message {apid}/{ctid}: {msg.payload}")

    injected = _find(record, *_FAULT_INJECTED)
    failures = _find(record, *_SUPERVISION_FAILED)
    if injected and failures and failures[0].epoch_time < injected[0].epoch_time:
        findings.append("warn_app supervision failed before the fault was injected (spontaneous failure)")
    return findings


@add_test_properties(
    partially_verifies=[
        "stkh_req__execution_model__processes",
        "stkh_req__dev_experience__logging_support",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_drive_replay(target, dlt_config):
    """The launch manager detects a hanging and a crashing supervised application,
    falls back to the degraded Run Target and the state manager restores the
    nominal one; the restarted application keeps its persisted state."""

    target.execute(_MULTICAST_ROUTE_CMD)
    with DltWindow(
        protocol=Protocol.UDP,
        host_ip=dlt_config.host_ip,
        multicast_ips=dlt_config.multicast_ips,
        print_to_stdout=False,
        binary_path=dlt_config.dlt_receive_path,
        file_name=str(Path(os.environ["TEST_UNDECLARED_OUTPUTS_DIR"]) / "drive_replay.dlt"),
    ) as window:
        output = run_showcases(target, SHOWCASE)

    findings = analyze_dlt(window.record())
    assert not findings, "\n".join(findings) + f"\n\nConsole output:\n{output}"
