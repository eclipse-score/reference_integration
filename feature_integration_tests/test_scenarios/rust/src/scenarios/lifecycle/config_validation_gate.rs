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
    config_schema_valid: bool,
    dependencies_consistent: bool,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct ConfigValidationGateScenario;

impl Scenario for ConfigValidationGateScenario {
    fn name(&self) -> &str {
        "config_validation_gate"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;
        let valid = test_input.config_schema_valid && test_input.dependencies_consistent;

        info!(
            event = "offline_config_validation",
            schema_valid = test_input.config_schema_valid,
            dependencies_consistent = test_input.dependencies_consistent,
            status = if valid { "accepted" } else { "rejected" }
        );

        if valid {
            info!(event = "lifecycle_config_executable", status = "executable");
            return Ok(());
        }

        let reason = if !test_input.config_schema_valid {
            "invalid_schema"
        } else {
            "inconsistent_dependencies"
        };
        info!(
            event = "lifecycle_config_rejected",
            status = "rejected",
            reason = reason
        );

        Ok(())
    }
}
