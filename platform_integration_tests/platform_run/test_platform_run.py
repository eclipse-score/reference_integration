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
"""Platform integration test for the S-CORE platform run.

The ``S-CORE Platform Run`` showcase (``showcases/platform_run``) hands control
to the deployed launch manager: it starts the platform daemons first and then
every test application, and only reaches the ``PlatformRun`` run target once
each test application has exited successfully. The applications log via mw::log
to DLT through the datarouter. This test records that DLT traffic on the host
while the showcase runs and analyzes the recording and the console output
afterwards. The recording is kept as ``platform_run.dlt`` in the test's
undeclared outputs.
"""

import os
import re
from pathlib import Path

from attribute_plugin import add_test_properties
from score.itf.plugins.dlt.dlt_receive import Protocol
from score.itf.plugins.dlt.dlt_window import DltWindow
from showcase_runner import run_showcases

SHOWCASE = "S-CORE Platform Run"

# Routes DLT multicast out of the container to the host-side dlt-receive.
_MULTICAST_ROUTE_CMD = "ip route add 224.0.0.0/4 dev eth0 2>/dev/null || true"

# (app id, context id, payload pattern) that every run must put on DLT.
EXPECTED_DLT = [
    ("DR", "DFLT", r"successfully completed initialization"),
    ("EXA", "DFLT", r"Logging Application DoLogging"),
    ("LGGG", "LOGG", r"DLT generator finished"),
]

# Verdicts of test applications that only print to the console.
EXPECTED_CONSOLE = [
    "platform_info_consumer: S-CORE version check passed",
]


def analyze_console(output: str) -> list[str]:
    """Findings in the console output, up to the verdict of the run.

    The launch manager starts before the datarouter, so its own messages are
    only on the console, not on DLT.
    """
    findings = []
    run, verdict, _ = output.partition("S-CORE platform run: PASSED")
    if not verdict:
        findings.append("the run did not report PASSED")
    if not re.search(r"Completed the request for Run Target PlatformRun", run):
        findings.append("the launch manager did not reach the PlatformRun run target")
    for problem in ("unexpected termination of process", "Problem discovered", "timeout for process"):
        if problem in run:
            findings.append(f"the launch manager reported '{problem}'")
    for expected in EXPECTED_CONSOLE:
        if expected not in run:
            findings.append(f"missing on the console: '{expected}'")
    return findings


def analyze_dlt(record) -> list[str]:
    """Findings in the recorded DLT traffic: every expected message is present."""
    findings = []
    for apid, ctid, pattern in EXPECTED_DLT:
        query = dict(apid=apid, ctid=ctid, payload_decoded=re.compile(pattern))
        if not record.find(query=query, full_match=False):
            findings.append(f"no DLT message {apid}/{ctid} matching '{pattern}'")
    return findings


@add_test_properties(
    partially_verifies=[
        "stkh_req__execution_model__processes",
        "stkh_req__dev_experience__logging_support",
    ],
    test_type="interface-test",
    derivation_technique="requirements-analysis",
)
def test_platform_run(target, dlt_config):
    """The launch manager starts the logging daemon and then the test
    applications, each of which exits successfully; their mw::log output
    reaches the host as DLT through the datarouter."""

    target.execute(_MULTICAST_ROUTE_CMD)
    with DltWindow(
        protocol=Protocol.UDP,
        host_ip=dlt_config.host_ip,
        multicast_ips=dlt_config.multicast_ips,
        print_to_stdout=False,
        binary_path=dlt_config.dlt_receive_path,
        file_name=str(Path(os.environ["TEST_UNDECLARED_OUTPUTS_DIR"]) / "platform_run.dlt"),
    ) as window:
        output = run_showcases(target, SHOWCASE)

    findings = analyze_console(output) + analyze_dlt(window.record())
    assert not findings, "\n".join(findings) + f"\n\nConsole output:\n{output}"
