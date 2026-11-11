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
to DLT through the datarouter, and so does the launch manager. This test
records that DLT traffic on the host while the showcase runs and analyzes the
recording afterwards. The recording is kept as ``platform_run.dlt`` in the
test's undeclared outputs.
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

# Launch manager components (launch_manager_config.json) that must run to completion.
TEST_APPS = [
    "logging_app",
    "dlt_generator",
    "log_builtin",
    "log_custom",
    "log_cpp_init",
    "kyron_safety_task",
    "kyron_main_macro",
    "com_api_example",
    "platform_info_consumer",
]

# (app id, context id, payload pattern) that every run must put on DLT.
EXPECTED_DLT = [
    ("DR", "DFLT", r"successfully completed initialization"),
    ("EXA", "DFLT", r"Logging Application DoLogging"),
    ("LGGG", "LOGG", r"DLT generator finished"),
    ("PINC", "PINF", r"platform_info_consumer: S-CORE version check passed"),
    ("LM", "LM", r"Completed the request for Run Target\s+PlatformRun"),
]
# The launch manager logs these at debug level, which showcases/platform_run/logging.json enables for DLT.
for _app in TEST_APPS:
    EXPECTED_DLT += [
        ("LM", "LM", rf"Starting process\s*\(\s*{_app}\s*\)"),
        ("LM", "LM", rf"Process\s+{_app}\s+\(\s*pid\s+\d+\s*\)\s+terminated with status\s+0\b"),
    ]

# (app id, context id, payload pattern) that no run may put on DLT: launch manager warnings.
FORBIDDEN_DLT = [
    ("LM", "LM", r"unexpected termination of process"),
    ("LM", "LM", r"Problem discovered"),
    ("LM", "LM", r"did not meet its ready condition"),
]


def analyze_dlt(record) -> list[str]:
    """Findings in the recorded DLT traffic: every expected message is present
    and no forbidden one."""
    findings = []
    for apid, ctid, pattern in EXPECTED_DLT:
        query = {"apid": apid, "ctid": ctid, "payload_decoded": re.compile(pattern)}
        if not record.find(query=query, full_match=False):
            findings.append(f"no DLT message {apid}/{ctid} matching '{pattern}'")
    for apid, ctid, pattern in FORBIDDEN_DLT:
        query = {"apid": apid, "ctid": ctid, "payload_decoded": re.compile(pattern)}
        for msg in record.find(query=query, full_match=True):
            findings.append(f"DLT message {apid}/{ctid}: {msg.payload}")
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

    findings = analyze_dlt(window.record())
    assert not findings, "\n".join(findings) + f"\n\nConsole output:\n{output}"
