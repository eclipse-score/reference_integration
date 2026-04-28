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
use crate::internals::persistency::{kvs_instance::kvs_instance, kvs_parameters::KvsParameters};
use rust_kvs::prelude::KvsApi;
use serde::Deserialize;
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

#[derive(Deserialize, Debug)]
pub struct TestInput {
    keys: Vec<String>,
    override_values: Vec<f64>,
    default_values: Vec<f64>,
}

impl TestInput {
    pub fn from_json(input: &str) -> Result<Self, String> {
        let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(v["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct ResetToDefault;

impl Scenario for ResetToDefault {
    fn name(&self) -> &str {
        "reset_to_default"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        // Parse parameters
        let v: Value = serde_json::from_str(input).expect("Failed to parse input string");
        let params = KvsParameters::from_value(&v["kvs_parameters_1"]).expect("Failed to parse parameters");
        let test_input = TestInput::from_json(input).expect("Failed to parse test input");

        {
            // Create KVS with Optional mode - defaults should be loaded
            let kvs = kvs_instance(params.clone()).expect("Failed to create KVS instance");

            // Verify all keys start with default values
            for (i, key) in test_input.keys.iter().enumerate() {
                let default_value: f64 = kvs.get_value_as(key).expect("Failed to get default value");

                if (default_value - test_input.default_values[i]).abs() > 1e-9 {
                    return Err(format!(
                        "Initial value mismatch for {}: expected {}, got {}",
                        key, test_input.default_values[i], default_value
                    ));
                }
            }

            // Override all keys with new values
            for (i, key) in test_input.keys.iter().enumerate() {
                kvs.set_value(key, test_input.override_values[i])
                    .expect("Failed to override value");

                let is_default = kvs.is_value_default(key).expect("Failed to check is_value_default");

                info!(
                    operation = format!("override_{}", key).as_str(),
                    key = key.as_str(),
                    value = test_input.override_values[i],
                    is_default = is_default.to_string().as_str(),
                    "Overridden value"
                );
            }

            // Reset key2 (index 1) using remove_key
            let key_to_reset = &test_input.keys[1];
            kvs.remove_key(key_to_reset).expect("Failed to remove key");

            // Check key2 after reset - should be back to default
            let reset_value: f64 = kvs.get_value_as(key_to_reset).expect("Failed to get value after reset");

            let is_default_after = kvs
                .is_value_default(key_to_reset)
                .expect("Failed to check is_value_default after reset");

            info!(
                operation = format!("after_reset_{}", key_to_reset).as_str(),
                key = key_to_reset.as_str(),
                value = reset_value,
                is_default = is_default_after.to_string().as_str(),
                "Value after reset"
            );

            // Verify reset_value matches default
            if (reset_value - test_input.default_values[1]).abs() > 1e-9 {
                return Err(format!(
                    "Reset value mismatch: expected {}, got {}",
                    test_input.default_values[1], reset_value
                ));
            }

            // Check other keys are still overridden
            for (i, key) in test_input.keys.iter().enumerate() {
                if i == 1 {
                    continue; // Skip key2 which we just reset
                }

                let current_value: f64 = kvs.get_value_as(key).expect("Failed to get value");

                let is_default = kvs.is_value_default(key).expect("Failed to check is_value_default");

                info!(
                    operation = format!("check_{}_after_reset", key).as_str(),
                    key = key.as_str(),
                    value = current_value,
                    is_default = is_default.to_string().as_str(),
                    "Other key after reset"
                );

                if (current_value - test_input.override_values[i]).abs() > 1e-9 {
                    return Err(format!(
                        "Other key was affected by reset: {} expected {}, got {}",
                        key, test_input.override_values[i], current_value
                    ));
                }
            }

            // Flush to storage
            kvs.flush().expect("Failed to flush KVS");
        }

        Ok(())
    }
}
