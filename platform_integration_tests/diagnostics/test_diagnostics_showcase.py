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

import http.client
import json
import logging
import time

from showcase_runner import run_showcases

_LOGGER = logging.getLogger(__name__)
_GATEWAY_PORT = 7690
_SERVICE = "/showcases/data/diagnostics/service.sh"


def _request(host: str, method: str, path: str, body: bytes | None = None, token: str = "") -> tuple[int, bytes]:
    headers = {}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    connection = http.client.HTTPConnection(host, _GATEWAY_PORT, timeout=5)
    try:
        connection.request(method, f"/sovd/v1/{path}", body=body, headers=headers)
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()


def _check_gateway(host: str) -> None:
    """Check authentication and forwarding to the CDA over the target network."""
    status, body = _request(
        host,
        "POST",
        "authorize",
        b'{"client_id":"diagnostics-check","client_secret":"test"}',
    )
    if status != 200:
        raise ValueError(f"authorization returned HTTP {status}")
    authorization = json.loads(body)
    token = authorization.get("access_token") if isinstance(authorization, dict) else None
    if not isinstance(token, str) or not token:
        raise ValueError("authorization returned no access token")
    status, body = _request(host, "GET", "apps", token=token)
    if status != 200 or b'"sovd2uds"' not in body or b'"score-diagnostics"' not in body:
        raise ValueError(f"gateway apps returned HTTP {status}: {body!r}")


def _wait_for_gateway(host, process, timeout=120):
    deadline = time.monotonic() + timeout
    error = "no response"
    while True:
        assert process.is_running(), f"Diagnostics service exited:\n{process.get_output()}"
        try:
            _check_gateway(host)
            assert process.is_running(), f"Diagnostics service exited:\n{process.get_output()}"
            return
        except (OSError, http.client.HTTPException, ValueError) as exc:
            error = str(exc)
        if time.monotonic() >= deadline:
            raise AssertionError(f"Diagnostics gateway at {host}:{_GATEWAY_PORT} was not ready: {error}")
        time.sleep(1)


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
    host = target.get_ip()
    process = target.execute_async(_SERVICE, args=["--if-not-running"])
    failed = True
    try:
        _wait_for_gateway(host, process)
        output = run_showcases(target, "S-CORE Platform Run")
        assert _platform_run_passed(output), output
        _wait_for_gateway(host, process)
        failed = False
    finally:
        if process.is_running():
            process.stop()
        if failed:
            _LOGGER.error("Diagnostics service output:\n%s", process.get_output())
