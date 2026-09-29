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
Helpers and base scenario classes for lifecycle feature integration tests.

``LifecycleScenario`` is a ``FitScenario`` subclass that supplies the shared
``temp_dir`` fixture so individual test classes do not have to duplicate it.

``RetryDaemonScenario`` provides the equivalent class-scoped-fixture convention
for the flaky-retry daemon tests, which don't fit ``FitScenario`` (no scenario
binary, `command`, or `version` parametrization involved).
"""

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, temp_dir_common


class LifecycleScenario(FitScenario):
    """
    Base class for lifecycle feature integration tests.

    Provides the ``temp_dir`` fixture shared by all lifecycle test classes.
    """

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        """
        Provide a temporary working directory for the lifecycle tests.

        Parameters
        ----------
        tmp_path_factory : pytest.TempPathFactory
            Built-in pytest factory for temporary directories.
        version : str
            Parametrized scenario version (``"rust"`` or ``"cpp"``).
        """
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)


class RetryDaemonScenario:
    """
    Base class for flaky-retry launch_manager daemon lifecycle tests.

    Subclasses set ``crashes_before_success``; the
    ``retry_daemon`` fixture starts one launch_manager instance per test class
    against `flaky_startup_app` and tears it down afterwards.
    """

    crashes_before_success: int

    @pytest.fixture(scope="class")
    def retry_daemon(self, tmp_path_factory: pytest.TempPathFactory) -> Generator[dict[str, Any], None, None]:
        from daemon_helpers import start_flaky_retry_daemon, stop_flaky_retry_daemon

        daemon_info = start_flaky_retry_daemon(tmp_path_factory, self.crashes_before_success)
        try:
            yield daemon_info
        finally:
            stop_flaky_retry_daemon(daemon_info)
