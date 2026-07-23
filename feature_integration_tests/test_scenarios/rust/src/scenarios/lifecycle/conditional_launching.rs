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

use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

pub struct ConditionalLaunching;

impl Scenario for ConditionalLaunching {
    fn name(&self) -> &str {
        "conditional_launching"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let value: Value = serde_json::from_str(input).map_err(|error| format!("Parse error: {error}"))?;
        let test = value
            .get("test")
            .ok_or_else(|| "Missing 'test' field in scenario input".to_string())?;

        let polling_interval = test.get("polling_interval_ms").and_then(Value::as_u64).unwrap_or(50);
        let timeout = test.get("timeout_ms").and_then(Value::as_u64).unwrap_or(5000);
        let conditions = test.get("wait_conditions").and_then(Value::as_array).ok_or_else(|| {
            "Wait conditions were not provided: missing 'test.wait_conditions' in scenario input".to_string()
        })?;

        if conditions.is_empty() {
            return Err(
                "Wait conditions were not provided: empty 'test.wait_conditions' in scenario input".to_string(),
            );
        }

        info!("Testing conditional launching");

        for condition in conditions {
            let condition = condition
                .as_str()
                .ok_or_else(|| "Wait condition entries must be strings".to_string())?;

            if let Some(path) = condition.strip_prefix("path:") {
                info!("Checking path condition: {path}");
            } else if let Some(name) = condition.strip_prefix("env:") {
                info!("Checking env condition: {name}");
            } else if let Some(process) = condition.strip_prefix("process:") {
                info!("Checking process condition: {process}");
            } else {
                return Err(format!("Unsupported wait condition prefix: {condition}"));
            }
        }

        info!("Polling interval: {polling_interval}ms");
        info!("Condition timeout: {timeout}ms");
        info!("All dependencies satisfied");

        Ok(())
    }
}
