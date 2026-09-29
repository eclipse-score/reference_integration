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
Base classes for lifecycle FITs.

``LifecycleScenario``: ``FitScenario`` base for the scenario-binary tests
(test_conditional_launching_scenario.py); adds the class-scoped ``temp_dir`` fixture.

``RetryDaemonScenario``: base for the flaky-retry daemon tests (test_retry_exhaustion.py),
which run no scenario binary; adds the class-scoped ``retry_daemon`` fixture.
"""

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fit_scenario import FitScenario, temp_dir_common


class LifecycleScenario(FitScenario):
    """Base for lifecycle scenario-binary test classes; provides ``temp_dir``."""

    @pytest.fixture(scope="class")
    def temp_dir(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        version: str,
    ) -> Generator[Path, None, None]:
        """
        Per-class, per-version temporary directory for the scenario run.

        Parameters
        ----------
        tmp_path_factory : pytest.TempPathFactory
            Built-in pytest factory for temporary directories.
        version : str
            Parametrized scenario version (``"rust"`` or ``"cpp"``).
        """
        yield from temp_dir_common(tmp_path_factory, self.__class__.__name__, version)


class RetryDaemonScenario:
    """Base for flaky-retry daemon test classes.

    Subclasses set ``crashes_before_success``; ``retry_daemon`` starts one launch_manager per
    class via ``daemon_helpers.start_flaky_retry_daemon`` and tears it down afterwards.
    """

    crashes_before_success: int

    @pytest.fixture(scope="class")
    def retry_daemon(self, tmp_path_factory: pytest.TempPathFactory) -> Generator[dict[str, Any], None, None]:
        # Lazy import: the scenario-lifecycle targets import this module without shipping daemon_helpers.py.
        from daemon_helpers import start_flaky_retry_daemon, stop_flaky_retry_daemon

        daemon_info = start_flaky_retry_daemon(tmp_path_factory, self.crashes_before_success)
        try:
            yield daemon_info
        finally:
            stop_flaky_retry_daemon(daemon_info)
