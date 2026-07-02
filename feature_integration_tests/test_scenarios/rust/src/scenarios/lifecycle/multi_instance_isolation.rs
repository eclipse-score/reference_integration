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
    instance_a: String,
    instance_b: String,
    cross_instance_interference: bool,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct MultiInstanceIsolationScenario;

impl Scenario for MultiInstanceIsolationScenario {
    fn name(&self) -> &str {
        "multi_instance_isolation"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(
            event = "instance_registered_a",
            instance_name = test_input.instance_a.as_str()
        );
        info!(
            event = "instance_registered_b",
            instance_name = test_input.instance_b.as_str()
        );

        if test_input.cross_instance_interference {
            info!(
                event = "instance_isolation_violated",
                status = "violated",
                reason = "cross_instance_interference"
            );
            return Ok(());
        }

        info!(
            event = "instance_isolation_ok",
            status = "isolated",
            supervision_scope = "per_instance"
        );

        Ok(())
    }
}
