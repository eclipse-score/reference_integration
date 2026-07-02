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
    daemon_enabled: bool,
    signal_name: String,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct ApplicationInterfaceScenario;

impl Scenario for ApplicationInterfaceScenario {
    fn name(&self) -> &str {
        "application_if"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(component = "launch_manager", state = "running", api = "application_if");
        info!(
            component = "score_application",
            state = "state_reported",
            api = "lifecycle_if"
        );

        if test_input.daemon_enabled {
            info!(component = "control_daemon", state = "running");
            info!(
                event = "signal_dispatched",
                condition = "daemon_running",
                signal_name = test_input.signal_name.as_str(),
                target_process = "score_application"
            );
        } else {
            info!(
                event = "signal_skipped",
                condition = "daemon_not_running",
                signal_name = test_input.signal_name.as_str(),
                target_process = "score_application"
            );
        }

        Ok(())
    }
}
