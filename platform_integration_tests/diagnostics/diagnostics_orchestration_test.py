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

# unittest is used so this test can run without pytest; it tests private helpers directly.
# ruff: noqa: PT027, SLF001

import http.server
import json
import threading
import unittest
from unittest import mock

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


class DiagnosticsOrchestrationTest(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.apps = b'["sovd2uds", "score-diagnostics"]'
        self.authorization = b'{"access_token":"test-token"}'
        owner = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                owner.requests.append(("POST", self.path, body, self.headers.get("Content-Type")))
                self.respond(owner.authorization)

            def do_GET(self):
                owner.requests.append(("GET", self.path, self.headers.get("Authorization")))
                self.respond(owner.apps)

            def respond(self, body):
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.thread.join)
        self.addCleanup(self.server.shutdown)
        self.port = mock.patch.object(diagnostics, "_GATEWAY_PORT", self.server.server_port)
        self.port.start()
        self.addCleanup(self.port.stop)

    def test_coexistence_uses_network_before_and_after_platform_run(self):
        target = _Target()
        diagnostics.test_diagnostics_and_platform_run_coexist(target)

        assert target.commands[0] == (diagnostics._SERVICE, ["--if-not-running"])
        assert "S-CORE Platform Run" in target.commands[1]
        assert len(self.requests) == 4
        for post, get in zip(self.requests[::2], self.requests[1::2], strict=True):
            assert post[:2] == ("POST", "/sovd/v1/authorize")
            assert json.loads(post[2]) == {"client_id": "diagnostics-check", "client_secret": "test"}
            assert post[3] == "application/json"
            assert get == ("GET", "/sovd/v1/apps", "Bearer test-token")
        assert target.process.stopped

    def test_bad_platform_verdict_still_stops_service(self):
        target = _Target()
        target.platform_output = b"Example 'S-CORE Platform Run' finished successfully\nS-CORE platform run: FAILED\n"
        with self.assertRaises(AssertionError), self.assertLogs(diagnostics._LOGGER, level="ERROR") as logs:
            diagnostics.test_diagnostics_and_platform_run_coexist(target)
        assert target.process.stopped
        assert "service log" in "\n".join(logs.output)

    def test_missing_cda_app_times_out(self):
        self.apps = b'["score-diagnostics"]'
        with self.assertRaisesRegex(AssertionError, "gateway apps returned HTTP 200"):
            diagnostics._wait_for_gateway("127.0.0.1", _Process(), timeout=0)

    def test_gateway_retries_connection_failure(self):
        with (
            mock.patch.object(
                diagnostics, "_check_gateway", side_effect=[OSError("connection refused"), None]
            ) as check,
            mock.patch.object(diagnostics.time, "sleep") as sleep,
        ):
            diagnostics._wait_for_gateway("127.0.0.1", _Process())
        assert check.call_count == 2
        sleep.assert_called_once_with(1)

    def test_invalid_authorization_response_times_out(self):
        self.authorization = b"[]"
        with self.assertRaisesRegex(AssertionError, "no access token"):
            diagnostics._wait_for_gateway("127.0.0.1", _Process(), timeout=0)

    def test_exited_service_fails_without_network_access(self):
        process = _Process()
        process.running = False
        with self.assertRaisesRegex(AssertionError, "service log"):
            diagnostics._wait_for_gateway("127.0.0.1", process, timeout=0)
        assert self.requests == []

    def test_service_exiting_during_platform_run_fails(self):
        target = _Target()
        run = target.execute

        def execute(command):
            result = run(command)
            target.process.running = False
            return result

        target.execute = execute
        with self.assertRaisesRegex(AssertionError, "service log"), self.assertLogs(diagnostics._LOGGER, level="ERROR"):
            diagnostics.test_diagnostics_and_platform_run_coexist(target)
        assert not target.process.stopped
        assert len(self.requests) == 2


if __name__ == "__main__":
    unittest.main()
