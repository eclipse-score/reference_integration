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
use rust_kvs::prelude::*;
use serde_json::Value;
use std::path::{Path, PathBuf};
use test_scenarios_rust::scenario::{Scenario, ScenarioGroup, ScenarioGroupImpl};
use tracing::info;

fn to_str<T: core::fmt::Debug>(value: &T) -> String {
    format!("{value:?}")
}

fn kvs_hash_paths(working_dir: &Path, instance_id: InstanceId, snapshot_id: SnapshotId) -> (PathBuf, PathBuf) {
    let kvs_path = working_dir.join(format!("kvs_{instance_id}_{snapshot_id}.json"));
    let hash_path = working_dir.join(format!("kvs_{instance_id}_{snapshot_id}.hash"));
    (kvs_path, hash_path)
}

fn parse_params(input: &str) -> Result<KvsParameters, String> {
    let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
    KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())
}

struct DefaultValues;

impl Scenario for DefaultValues {
    fn name(&self) -> &str {
        "default_values"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let key = "test_number";
        let params = parse_params(input)?;

        {
            let kvs = kvs_instance(params.clone())
                .unwrap_or_else(|e| panic!("Failed to create KVS instance: {e:?}"));

            let value_is_default = to_str(&kvs.is_value_default(key));
            let default_value = to_str(&kvs.get_default_value(key));
            let current_value = to_str(&kvs.get_value(key));

            info!(key, value_is_default, default_value, current_value);

            kvs.set_value(key, 432.1).expect("Failed to set value");
            kvs.flush().expect("Failed to flush");
        }

        {
            let kvs = kvs_instance(params).unwrap_or_else(|e| panic!("Failed to create KVS instance: {e:?}"));

            let value_is_default = to_str(&kvs.is_value_default(key));
            let default_value = to_str(&kvs.get_default_value(key));
            let current_value = to_str(&kvs.get_value(key));

            info!(key, value_is_default, default_value, current_value);
        }

        Ok(())
    }
}

struct RemoveKey;

impl Scenario for RemoveKey {
    fn name(&self) -> &str {
        "remove_key"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let key = "test_number";
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).unwrap_or_else(|e| panic!("Failed to create KVS instance: {e:?}"));

        let value_is_default = to_str(&kvs.is_value_default(key));
        let default_value = to_str(&kvs.get_default_value(key));
        let current_value = to_str(&kvs.get_value(key));
        info!(key, value_is_default, default_value, current_value);

        kvs.set_value(key, 432.1).expect("Failed to set value");

        let value_is_default = to_str(&kvs.is_value_default(key));
        let default_value = to_str(&kvs.get_default_value(key));
        let current_value = to_str(&kvs.get_value(key));
        info!(key, value_is_default, default_value, current_value);

        kvs.remove_key(key).expect("Failed to remove key");
        let value_is_default = to_str(&kvs.is_value_default(key));
        let default_value = to_str(&kvs.get_default_value(key));
        let current_value = to_str(&kvs.get_value(key));
        info!(key, value_is_default, default_value, current_value);

        Ok(())
    }
}

struct ResetAllKeys;

impl Scenario for ResetAllKeys {
    fn name(&self) -> &str {
        "reset_all_keys"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let num_values = 5;
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).unwrap_or_else(|e| panic!("Failed to create KVS instance: {e:?}"));

        let mut key_values = Vec::new();
        for i in 0..num_values {
            let key = format!("test_number_{i}");
            let value = 123.4 * i as f64;
            key_values.push((key, value));
        }

        for (key, value) in key_values.iter() {
            let value_is_default = kvs.is_value_default(key).expect("Failed to check if default value");
            let current_value = kvs.get_value_as::<f64>(key).expect("Failed to read value");
            info!(key = key, value_is_default, current_value);

            kvs.set_value(key.clone(), *value).expect("Failed to set value");

            let value_is_default = kvs.is_value_default(key).expect("Failed to check if default value");
            let current_value = kvs.get_value_as::<f64>(key).expect("Failed to read value");
            info!(key, value_is_default, current_value);
        }

        kvs.reset().expect("Failed to reset KVS instance");

        for (key, _) in key_values.iter() {
            let value_is_default = kvs.is_value_default(key).expect("Failed to check if default value");
            let current_value = kvs.get_value_as::<f64>(key).expect("Failed to read value");
            info!(key, value_is_default, current_value);
        }

        Ok(())
    }
}

struct ResetSingleKey;

impl Scenario for ResetSingleKey {
    fn name(&self) -> &str {
        "reset_single_key"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let num_values = 5;
        let reset_index = 2;
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).unwrap_or_else(|e| panic!("Failed to create KVS instance: {e:?}"));

        let mut key_values = Vec::new();
        for i in 0..num_values {
            let key = format!("test_number_{i}");
            let value = 123.4 * i as f64;
            key_values.push((key, value));
        }

        for (key, value) in key_values.iter() {
            let value_is_default = kvs.is_value_default(key).expect("Failed to check if default value");
            let current_value = kvs.get_value_as::<f64>(key).expect("Failed to read value");
            info!(key = key, value_is_default, current_value);

            kvs.set_value(key.clone(), *value).expect("Failed to set value");

            let value_is_default = kvs.is_value_default(key).expect("Failed to check if default value");
            let current_value = kvs.get_value_as::<f64>(key).expect("Failed to read value");
            info!(key, value_is_default, current_value);
        }

        kvs.reset_key(&key_values[reset_index].0)
            .expect("Failed to reset key");

        for (key, _) in key_values.iter() {
            let value_is_default = kvs.is_value_default(key).expect("Failed to check if default value");
            let current_value = kvs.get_value_as::<f64>(key).expect("Failed to read value");
            info!(key, value_is_default, current_value);
        }

        Ok(())
    }
}

struct Checksum;

impl Scenario for Checksum {
    fn name(&self) -> &str {
        "checksum"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let params = parse_params(input)?;
        let working_dir = params.dir.clone().expect("Working directory must be set");
        let kvs_path;
        let hash_path;
        {
            let kvs = kvs_instance(params.clone())
                .unwrap_or_else(|e| panic!("Failed to create KVS instance: {e:?}"));
            kvs.flush().expect("Failed to flush");
            (kvs_path, hash_path) = kvs_hash_paths(&working_dir, params.instance_id, SnapshotId(0));
        }
        info!(
            kvs_path = kvs_path.display().to_string(),
            hash_path = hash_path.display().to_string()
        );

        Ok(())
    }
}

pub fn default_values_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "default_values",
        vec![
            Box::new(DefaultValues),
            Box::new(RemoveKey),
            Box::new(ResetAllKeys),
            Box::new(ResetSingleKey),
            Box::new(Checksum),
        ],
        vec![],
    ))
}
