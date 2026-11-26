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
"""Exercise the host-side diagnostics checks without a platform image."""

# These tests exercise the host-side helpers directly.
# ruff: noqa: SLF001

import http.server
import json
import threading
from types import SimpleNamespace
from unittest import mock

import pytest
import test_diagnostics_showcase as diagnostics


class _Process:
    def __init__(self):
        self.running = True
        self.stopped = False

    def is_running(self):
        return self.running

    def stop(self):
        self.stopped = True
        self.running = False

    def get_output(self):
        return "service log"


class _Target:
    def __init__(self):
        self.process = _Process()
        self.commands = []
        self.platform_output = b"Example 'S-CORE Platform Run' finished successfully\nS-CORE platform run: PASSED\n"

    def get_ip(self):
        return "127.0.0.1"

    def execute_async(self, binary_path, args=None):
        self.commands.append((binary_path, args))
        return self.process

    def execute(self, command):
        self.commands.append(command)
        return 0, self.platform_output


@pytest.fixture
def gateway(monkeypatch):
    state = SimpleNamespace(
        requests=[],
        apps=b'["sovd2uds", "score-diagnostics"]',
        authorization=b'{"access_token":"test-token"}',
    )

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            state.requests.append(("POST", self.path, body, self.headers.get("Content-Type")))
            self.respond(state.authorization)

        def do_GET(self):
            state.requests.append(("GET", self.path, self.headers.get("Authorization")))
            self.respond(state.apps)

        def respond(self, body):
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(diagnostics, "_GATEWAY_PORT", server.server_port)
    try:
        yield state
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_coexistence_uses_network_before_and_after_platform_run(gateway):
    target = _Target()
    diagnostics.test_diagnostics_and_platform_run_coexist(target)

    assert target.commands[0] == (diagnostics._SERVICE, ["--if-not-running"])
    assert "S-CORE Platform Run" in target.commands[1]
    assert len(gateway.requests) == 4
    for post, get in zip(gateway.requests[::2], gateway.requests[1::2], strict=True):
        assert post[:2] == ("POST", "/sovd/v1/authorize")
        assert json.loads(post[2]) == {"client_id": "diagnostics-check", "client_secret": "test"}
        assert post[3] == "application/json"
        assert get == ("GET", "/sovd/v1/apps", "Bearer test-token")
    assert target.process.stopped


@pytest.mark.usefixtures("gateway")
def test_bad_platform_verdict_still_stops_service(caplog):
    target = _Target()
    target.platform_output = b"Example 'S-CORE Platform Run' finished successfully\nS-CORE platform run: FAILED\n"
    with pytest.raises(AssertionError), caplog.at_level("ERROR", logger=diagnostics._LOGGER.name):
        diagnostics.test_diagnostics_and_platform_run_coexist(target)
    assert target.process.stopped
    assert "service log" in caplog.text


def test_missing_cda_app_times_out(gateway):
    gateway.apps = b'["score-diagnostics"]'
    with pytest.raises(AssertionError, match="gateway apps returned HTTP 200"):
        diagnostics._wait_for_gateway("127.0.0.1", _Process(), timeout=0)


def test_gateway_retries_connection_failure():
    with (
        mock.patch.object(diagnostics, "_check_gateway", side_effect=[OSError("connection refused"), None]) as check,
        mock.patch.object(diagnostics.time, "sleep") as sleep,
    ):
        diagnostics._wait_for_gateway("127.0.0.1", _Process())
    assert check.call_count == 2
    sleep.assert_called_once_with(1)


def test_invalid_authorization_response_times_out(gateway):
    gateway.authorization = b"[]"
    with pytest.raises(AssertionError, match="no access token"):
        diagnostics._wait_for_gateway("127.0.0.1", _Process(), timeout=0)


def test_exited_service_fails_without_network_access(gateway):
    process = _Process()
    process.running = False
    with pytest.raises(AssertionError, match="service log"):
        diagnostics._wait_for_gateway("127.0.0.1", process, timeout=0)
    assert gateway.requests == []


def test_service_exiting_during_platform_run_fails(gateway, caplog):
    target = _Target()
    run = target.execute

    def execute(command):
        result = run(command)
        target.process.running = False
        return result

    target.execute = execute
    with pytest.raises(AssertionError, match="service log"), caplog.at_level("ERROR", logger=diagnostics._LOGGER.name):
        diagnostics.test_diagnostics_and_platform_run_coexist(target)
    assert not target.process.stopped
    assert "service log" in caplog.text
    assert len(gateway.requests) == 2
