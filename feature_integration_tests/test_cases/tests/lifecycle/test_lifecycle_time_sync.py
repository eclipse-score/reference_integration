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

from typing import Any

import pytest
from fit_scenario import FitScenario
from test_properties import add_test_properties
from testing_utils import LogContainer

pytestmark = pytest.mark.parametrize("version", ["rust", "cpp"], scope="class")


@add_test_properties(
    partially_verifies=[
        "feat_req__lifecycle__log_timestamp",
        "feat_req__time__monotonic_clock",
    ],
    test_type="requirements-based",
    derivation_technique="requirements-analysis",
)
class TestLifecycleTimeSync(FitScenario):
    """Validate timestamp consistency between lifecycle events and system monotonic time."""

    @pytest.fixture(scope="class")
    def scenario_name(self) -> str:
        return "lifecycle.time_sync"

    @pytest.fixture(scope="class", params=[True, False])
    def event_order_monotonic(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class", params=[True, False])
    def timestamp_aligned(self, request: pytest.FixtureRequest) -> bool:
        return bool(request.param)

    @pytest.fixture(scope="class")
    def test_config(self, event_order_monotonic: bool, timestamp_aligned: bool) -> dict[str, Any]:
        return {
            "test": {
                "event_order_monotonic": event_order_monotonic,
                "timestamp_aligned": timestamp_aligned,
            }
        }

    def test_timestamp_logging_and_clock_source(self, version: str, logs_info_level: LogContainer) -> None:
        """Ensure lifecycle emits timestamped logs and monotonic clock metadata."""
        assert version in ("rust", "cpp")

        timestamp_log = logs_info_level.find_log("event", value="lifecycle_timestamp_emitted")
        assert timestamp_log is not None, "Missing lifecycle_timestamp_emitted event"
        assert timestamp_log.timestamp_field == "system_time"

        clock_log = logs_info_level.find_log("event", value="clock_source_selected")
        assert clock_log is not None, "Missing clock_source_selected event"
        assert clock_log.clock_source == "monotonic"

    def test_time_consistency_evaluation(
        self,
        version: str,
        event_order_monotonic: bool,
        timestamp_aligned: bool,
        logs_info_level: LogContainer,
    ) -> None:
        """Verify sync status when lifecycle timestamps are aligned with monotonic progression."""
        assert version in ("rust", "cpp")

        consistent = event_order_monotonic and timestamp_aligned
        if consistent:
            ok_log = logs_info_level.find_log("event", value="time_sync_consistent")
            assert ok_log is not None, "Expected time_sync_consistent event"
            assert ok_log.status == "consistent"
            assert ok_log.reference == "monotonic_clock"

            drift_log = logs_info_level.find_log("event", value="time_sync_inconsistent")
            assert drift_log is None, "time_sync_inconsistent must not be emitted for consistent state"
            return

        mismatch_log = logs_info_level.find_log("event", value="time_sync_inconsistent")
        assert mismatch_log is not None, "Expected time_sync_inconsistent event"
        assert mismatch_log.status == "inconsistent"

        if not event_order_monotonic:
            assert mismatch_log.reason == "non_monotonic_event_order"
            return

        assert mismatch_log.reason == "timestamp_drift"
