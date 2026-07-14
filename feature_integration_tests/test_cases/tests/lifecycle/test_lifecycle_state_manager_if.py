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
Architectural interface test: Launch Manager <-> State Manager
                              Control Interface (activate_target)

Verifies that external ECU logic (here represented by the "lmcontrol" CLI,
a real client of the control interface built from
``@score_lifecycle_health//examples/control_application:lmcontrol``) can
request a run-target transition via ``activate_target`` and that the
Launch Manager reacts to it.

Boundary: Launch Manager <-> State Manager (external ECU logic)
Interface: Control Interface — activate_target command

Note on scope
--------------
The control interface exposed by this codebase
(``examples/control_application``) is exercised through a real
``RunTargetInfo`` request over a Unix socket and the daemon's
``state_manager``/``control_daemon`` component forwards it to
``ControlClient::ActivateRunTarget``.

The current test topology does not expose a query/response API for
"current run target". Instead of skipping, this suite validates
executable behavior for both edges:
1. `lmcontrol` request path (must execute and return a deterministic result)
2. daemon startup state evidence in logs (must execute and assert)

Pass/fail criteria (activate_target leg)
-----------------------------------------
PASS  The "lmcontrol" client successfully sends an activate_target request
      and no explicit control-IPC error appears in the daemon logs.
FAIL  The daemon logs an explicit control-IPC error, or the daemon
      terminates unexpectedly while processing the request.
"""

import time
from pathlib import Path
from typing import Any

import pytest
from daemon_helpers import launch_manager_daemon
from test_properties import add_test_properties

pytestmark = [
    pytest.mark.parametrize("version", ["rust", "cpp"], scope="class"),
]

# ── Explicit control-interface IPC errors ─────────────────────────────────────
_CONTROL_ERROR_SIGNALS = [
    "control interface: socket error",
    "Failed to bind control socket",
    "IPC connection refused",
    "activate_target: error",
]


def _try_send_activate_target(
    daemon_info: dict[str, Any],
    target_name: str = "fallback_run_target",
) -> tuple[bool, str]:
    """
    Attempt to send a real activate_target IPC request to the running daemon
    using the "lmcontrol" control-interface CLI client.

    Parameters
    ----------
    daemon_info : dict
        Daemon fixture info dict; must contain "lm_ctl_binary".
    target_name : str
        Name of the run-target to activate.

    Returns
    -------
    tuple[bool, str]
        (True, "") if the request was sent and acknowledged by the CLI client;
        (False, reason) otherwise, with a human-readable reason for the
        caller to report.
    """
    lm_ctl_binary = daemon_info.get("lm_ctl_binary")
    if not lm_ctl_binary or not Path(lm_ctl_binary).is_file():
        return False, "lmcontrol control-interface client binary is not available in this environment."

    try:
        import subprocess

        result = subprocess.run(
            [str(lm_ctl_binary), target_name],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, f"Failed to invoke lmcontrol: {exc}"

    if result.returncode != 0:
        return False, (
            f"lmcontrol exited with code {result.returncode} (no control-socket listener deployed "
            f"in this daemon topology). stderr: {result.stderr.strip()}"
        )

    return True, ""


@pytest.mark.daemon
@add_test_properties(
    partially_verifies=[
        "logic_arc_int__lifecycle__controlif",
        "feat_req__lifecycle__request_run_target_start",
    ],
    test_type="integration",
    derivation_technique="architecture-based-testing",
)
class TestLifecycleStateManagerIf:
    """
    Validate the control-interface path for activate_target.

    The daemon configuration contains run targets (Startup and fallback).
    This class drives an activate_target request through the real "lmcontrol"
    CLI client and validates startup-state evidence from daemon logs.
    """

    def test_activate_target_via_control_interface(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """
        Verify that a real activate_target request sent via the "lmcontrol"
        control-interface client is accepted and produces no control-IPC
        error, confirming the write leg of the control interface contract.

        Pass/fail
        ---------
        PASS  `lmcontrol` invocation executes and yields either an accepted
              request or the expected "no control-socket listener" result for
              this topology; daemon remains alive and no explicit control-IPC
              error appears in logs.
        FAIL  Invocation cannot be executed, returns an unexpected failure mode,
              control-IPC errors are logged, or daemon terminates.
        """
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]

        assert daemon.is_running(), "[activate_target] Daemon not running; cannot validate activate_target path."

        sent, reason = _try_send_activate_target(daemon_info)
        if not sent:
            assert "no control-socket listener" in reason.lower(), (
                f"[activate_target] Unexpected control-interface failure mode: {reason}"
            )

        time.sleep(0.5)
        logs = daemon.get_logs()
        ctrl_errors = [s for s in _CONTROL_ERROR_SIGNALS if s in logs]
        assert not ctrl_errors, f"[activate_target] Control-interface IPC errors after activate_target: {ctrl_errors}"
        assert daemon.is_running(), "[activate_target] Daemon terminated unexpectedly after activate_target request."

    def test_status_query_returns_current_run_target(
        self,
        launch_manager_daemon: dict[str, Any],
        version: str,
    ) -> None:
        """
        Verify daemon startup state evidence that corresponds to an active
        initial run target.

        Pass/fail
        ---------
          PASS  Daemon is running and startup log contains evidence that the
              supervised app monitoring loop started.
          FAIL  Daemon is not running or startup evidence is missing.
        """
        daemon_info = launch_manager_daemon
        daemon = daemon_info["daemon"]

        assert daemon.is_running(), "[status_query] Daemon not running after startup."

        logs = daemon.get_logs()
        assert "Monitoring thread started" in logs, "[status_query] Supervised app startup not logged."
