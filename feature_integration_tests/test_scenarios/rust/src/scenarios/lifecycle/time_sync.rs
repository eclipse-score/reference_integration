// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// <https://www.apache.org/licenses/LICENSE-2.0>
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************

use serde::Deserialize;
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

#[derive(Deserialize, Debug)]
struct TestInput {
    event_order_monotonic: bool,
    timestamp_aligned: bool,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct TimeSyncScenario;

impl Scenario for TimeSyncScenario {
    fn name(&self) -> &str {
        "time_sync"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(event = "lifecycle_timestamp_emitted", timestamp_field = "system_time");
        info!(event = "clock_source_selected", clock_source = "monotonic");

        if test_input.event_order_monotonic && test_input.timestamp_aligned {
            info!(
                event = "time_sync_consistent",
                status = "consistent",
                reference = "monotonic_clock"
            );
            return Ok(());
        }

        let reason = if !test_input.event_order_monotonic {
            "non_monotonic_event_order"
        } else {
            "timestamp_drift"
        };
        info!(
            event = "time_sync_inconsistent",
            status = "inconsistent",
            reason = reason
        );

        Ok(())
    }
}
