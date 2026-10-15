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
use crate::internals::persistency::{
    kvs_instance::{get_default_value_f64, kvs_instance},
    kvs_parameters::KvsParameters,
};
use rust_kvs::prelude::KvsApi;
use serde::Deserialize;
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

#[derive(Deserialize, Debug)]
pub struct TestInput {
    counter_key: String,
    #[serde(default)]
    set_keys: Vec<String>,
    #[serde(default)]
    set_values: Vec<f64>,
    #[serde(default)]
    reset_keys: Vec<String>,
    #[serde(default)]
    read_keys: Vec<String>,
}

impl TestInput {
    pub fn from_json(input: &str) -> Result<Self, String> {
        let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(v["test"].clone()).map_err(|e| e.to_string())
    }
}

/// One launch of a KVS-owning process, meant to be started repeatedly by Launch Manager.
///
/// Reads `counter_key` (0 when not stored), stores it incremented, applies `set_keys`/
/// `set_values`, calls `reset_key` on `reset_keys`, reads back each of `read_keys` and flushes.
/// A read-back logs the stored value (`source = "read_back"`) or, when the key has no stored
/// value (e.g. after `reset_key`), its default (`source = "read_back_default"`). Any read that
/// fails for another reason fails the scenario instead of falling back. The counter only equals
/// the number of launches if every launch loaded the state its predecessor flushed.
/// The snapshot is left in the native KVS format so the next launch can reload it.
pub struct RestartCounter;

impl Scenario for RestartCounter {
    fn name(&self) -> &str {
        "restart_counter"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        let params = KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())?;
        let test_input = TestInput::from_json(input)?;
        if test_input.set_keys.len() != test_input.set_values.len() {
            return Err("set_keys and set_values must have the same length".to_string());
        }

        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;

        let loaded = if kvs.key_exists(&test_input.counter_key).map_err(|e| format!("{e:?}"))? {
            kvs.get_value_as::<f64>(&test_input.counter_key)
                .map_err(|e| format!("{e:?}"))?
        } else {
            0.0
        };
        info!(key = test_input.counter_key, value = loaded, source = "loaded_on_open");

        kvs.set_value(&test_input.counter_key, loaded + 1.0)
            .map_err(|e| format!("{e:?}"))?;
        for (key, value) in test_input.set_keys.iter().zip(&test_input.set_values) {
            kvs.set_value(key, *value).map_err(|e| format!("{e:?}"))?;
        }
        for key in &test_input.reset_keys {
            kvs.reset_key(key).map_err(|e| format!("{e:?}"))?;
        }
        for key in &test_input.read_keys {
            if kvs.key_exists(key).map_err(|e| format!("{e:?}"))? {
                let value = kvs.get_value_as::<f64>(key).map_err(|e| format!("{e:?}"))?;
                info!(key = key.as_str(), value, source = "read_back");
            } else {
                let value = get_default_value_f64(&kvs, key).map_err(|e| format!("{e:?}"))?;
                info!(key = key.as_str(), value, source = "read_back_default");
            }
        }
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}
