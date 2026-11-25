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
"""Platform integration test for the diagnostics stack.

The platform deploys the OpenSOVD gateway and the classic diagnostic adapter (CDA) in
``/usr/bin/diagnostics`` (``//deploy/diagnostics``). The ``Diagnostics Stack`` showcase starts
both with the ECU databases of the showcases, so it only passes against a platform that deploys
working binaries.
"""

import shlex

from showcase_runner import run_showcases


def _platform_run_passed(output: str) -> bool:
    # The CLI echoes the wrapper command, which contains a FAILED message.
    lines = output.splitlines()
    return "S-CORE platform run: PASSED" in lines and not any(
        line.startswith("S-CORE platform run: FAILED") for line in lines
    )


def test_platform_run_verdict():
    echoed_command = "App 1: spawned command echo 'S-CORE platform run: FAILED (timeout)'\n"
    assert _platform_run_passed(echoed_command + "S-CORE platform run: PASSED\n")
    assert not _platform_run_passed(echoed_command)
    assert not _platform_run_passed(echoed_command + "S-CORE platform run: FAILED (timeout)\n")
    assert not _platform_run_passed("S-CORE platform run: PASSED\nS-CORE platform run: FAILED\n")
    assert not _platform_run_passed("echo 'S-CORE platform run: PASSED'\n")


def test_diagnostics_stack(target):
    """The gateway listens on 127.0.0.1:7690, the CDA loads the ECU databases and reports ready."""

    output = run_showcases(target, "Diagnostics Stack")
    assert "diagnostics_check: PASSED" in output, f"The diagnostics stack did not start:\n{output}"
    assert "diagnostics_check: FAILED" not in output, output


def test_diagnostics_and_platform_run_coexist(target):
    """The boot-time diagnostics manager and Platform Run share the same /tmp."""
    script = r"""
set -eu
log=$(mktemp)
/showcases/data/diagnostics/service.sh >"$log" 2>&1 &
diagnostics_pid=$!
cleanup() {
    status=$?
    kill -s TERM "$diagnostics_pid" 2>/dev/null || true
    wait "$diagnostics_pid" 2>/dev/null || true
    if [ "$status" -ne 0 ]; then cat "$log"; fi
    rm -f "$log"
    exit "$status"
}
trap cleanup EXIT

# Wait for the existing gateway before invoking check.sh, so the check does
# not start a second service while this one is still coming up.
ready=
for _ in $(seq 1 120); do
    kill -0 "$diagnostics_pid"
    if timeout 3 bash -c '
        exec 3<>/dev/tcp/127.0.0.1/7690
        printf "GET /sovd/v1/version-info HTTP/1.0\r\nHost: localhost\r\n\r\n" >&3
        read -r status <&3
        [[ "$status" == HTTP/* ]]
    ' 2>/dev/null; then
        ready=1
        break
    fi
    sleep 1
done
[ -n "$ready" ]
/showcases/data/diagnostics/check.sh
kill -0 "$diagnostics_pid"
/showcases/bin/cli --examples='S-CORE Platform Run'
kill -0 "$diagnostics_pid"
/showcases/data/diagnostics/check.sh
kill -0 "$diagnostics_pid"
"""
    exit_code, out = target.execute(f"bash -c {shlex.quote(script)}")
    output = out.decode(errors="replace")
    assert exit_code == 0, f"Coexistence check failed ({exit_code}):\n{output}"
    assert _platform_run_passed(output), output
    assert output.count("diagnostics_check: PASSED") == 2, output
    assert "diagnostics_check: FAILED" not in output, output
