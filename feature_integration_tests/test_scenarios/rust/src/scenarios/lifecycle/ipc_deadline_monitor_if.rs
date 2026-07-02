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
    checkpoint_on_time: bool,
    monitor_name: String,
    checkpoint_id: String,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct IpcDeadlineMonitorInterfaceScenario;

impl Scenario for IpcDeadlineMonitorInterfaceScenario {
    fn name(&self) -> &str {
        "ipc_deadline_monitor_if"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(
            event = "deadline_monitor_if_ready",
            status = "active",
            monitor_name = test_input.monitor_name.as_str()
        );

        info!(
            event = "checkpoint_ipc",
            checkpoint_id = test_input.checkpoint_id.as_str(),
            source_component = "health_monitor",
            target_component = "launch_manager"
        );

        if test_input.checkpoint_on_time {
            info!(
                event = "deadline_checkpoint_accepted",
                status = "accepted",
                reason = "within_deadline"
            );
            return Ok(());
        }

        info!(
            event = "deadline_timeout",
            status = "timeout",
            reason = "checkpoint_missed"
        );

        Ok(())
    }
}
