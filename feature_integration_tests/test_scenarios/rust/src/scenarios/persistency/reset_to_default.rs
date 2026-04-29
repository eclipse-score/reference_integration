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

        // Create KVS with Optional mode - defaults should be loaded
        let kvs = kvs_instance(params).expect("Failed to create KVS instance");

        // Override all keys with new values
        for (i, key) in test_input.keys.iter().enumerate() {
            kvs.set_value(key, test_input.override_values[i])
                .expect("Failed to override value");
        }

        // Reset key2 (index 1) using remove_key — reverts to default in memory
        kvs.remove_key(&test_input.keys[1]).expect("Failed to remove key");

        // Flush to persist the state: key1 and key3 with overrides, key2 absent
        kvs.flush().expect("Failed to flush KVS");

        Ok(())
    }
}
