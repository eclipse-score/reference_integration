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
    key: String,
    override_value: f64,
}

impl TestInput {
    pub fn from_json(input: &str) -> Result<Self, String> {
        let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(v["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct DefaultValuesIgnored;

impl Scenario for DefaultValuesIgnored {
    fn name(&self) -> &str {
        "default_values_ignored"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        // Parse parameters
        let v: Value = serde_json::from_str(input).expect("Failed to parse input string");
        let params = KvsParameters::from_value(&v["kvs_parameters_1"]).expect("Failed to parse parameters");
        let test_input = TestInput::from_json(input).expect("Failed to parse test input");

        // Create KVS with Ignored mode - defaults file exists but should not be loaded
        let kvs = kvs_instance(params).expect("Failed to create KVS instance");

        // In Ignored mode, getting a non-existent key should fail (no defaults loaded)
        let result: Result<f64, _> = kvs.get_value_as(&test_input.key);
        if result.is_ok() {
            return Err("Expected get_value to fail with Ignored mode, but it succeeded".to_string());
        }

        // Set explicit value and flush to storage. Python reads the snapshot
        // and verifies the explicitly set value is persisted.
        kvs.set_value(&test_input.key, test_input.override_value)
            .expect("Failed to set value");
        kvs.flush().expect("Failed to flush KVS");

        Ok(())
    }
}
