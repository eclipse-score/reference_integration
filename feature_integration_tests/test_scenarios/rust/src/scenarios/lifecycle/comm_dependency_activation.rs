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
    dependency_available: bool,
    dependency_executable: bool,
    component: String,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct CommDependencyActivationScenario;

impl Scenario for CommDependencyActivationScenario {
    fn name(&self) -> &str {
        "comm_dependency_activation"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(component = "launch_manager", state = "running", api = "dependency_if");
        info!(
            event = "dependency_check",
            component = test_input.component.as_str(),
            available = test_input.dependency_available
        );
        info!(
            event = "dependency_exec_check",
            component = test_input.component.as_str(),
            executable = test_input.dependency_executable
        );

        if test_input.dependency_available && test_input.dependency_executable {
            info!(
                event = "comm_activation",
                component = test_input.component.as_str(),
                status = "activated",
                reason = "dependency_ready"
            );
            return Ok(());
        }

        let reason = if !test_input.dependency_available {
            "dependency_missing"
        } else {
            "dependency_not_executable"
        };

        info!(
            event = "comm_activation_blocked",
            component = test_input.component.as_str(),
            status = "blocked",
            reason = reason
        );

        Ok(())
    }
}
