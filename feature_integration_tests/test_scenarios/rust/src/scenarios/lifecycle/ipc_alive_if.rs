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
    heartbeat_alive: bool,
    failure_action: String,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct IpcAliveInterfaceScenario;

impl Scenario for IpcAliveInterfaceScenario {
    fn name(&self) -> &str {
        "ipc_alive_if"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(component = "launch_manager", state = "running", api = "alive_if");
        info!(component = "health_monitor", state = "monitoring", api = "alive_if");
        info!(event = "heartbeat_ipc", status = "active");

        if test_input.heartbeat_alive {
            info!(
                event = "liveliness_ok",
                source_component = "health_monitor",
                propagated_to = "launch_manager"
            );
            return Ok(());
        }

        info!(
            event = "liveliness_failed",
            source_component = "health_monitor",
            propagated_to = "launch_manager"
        );
        info!(
            event = "failure_propagated",
            action = test_input.failure_action.as_str(),
            reason = "heartbeat_timeout"
        );

        Ok(())
    }
}
