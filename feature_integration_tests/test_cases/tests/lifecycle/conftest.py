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
"""Shared fixtures for lifecycle daemon tests."""

from __future__ import annotations

from typing import Any

import pytest
from daemon_helpers import start_launch_manager_daemon, stop_launch_manager_daemon


@pytest.fixture(scope="class")
def launch_manager_daemon(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """One launch_manager (with both supervised apps running) per test class and `version`
    param; see `daemon_helpers.start_launch_manager_daemon`. Tests using it must not start
    another daemon."""
    daemon_info = start_launch_manager_daemon(tmp_path_factory)
    try:
        yield daemon_info
    finally:
        stop_launch_manager_daemon(daemon_info)
