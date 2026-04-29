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
use test_scenarios_rust::scenario::{Scenario, ScenarioGroup, ScenarioGroupImpl};

fn parse_params(input: &str) -> Result<KvsParameters, String> {
    let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
    KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())
}

/// Set a single value and flush. Python reads the snapshot bytes and the hash
/// file, verifying adler32(snapshot) equals the hash written by KVS — exercising
/// feat_req__persistency__integrity_check alongside feat_req__persistency__store_data.
struct Checksum;

impl Scenario for Checksum {
    fn name(&self) -> &str {
        "checksum"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;
        kvs.set_value("checksum_test_key", 1.0).map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}

/// Open KVS with three default keys, override ONLY the middle key, flush.
/// Python verifies the snapshot contains exactly the one overridden key
/// (others were never explicitly written so they remain absent from storage).
/// Combines feat_req__persistency__default_values,
/// feat_req__persistency__default_value_file, and
/// feat_req__persistency__store_data in one observable storage outcome.
struct PartialOverride;

impl Scenario for PartialOverride {
    fn name(&self) -> &str {
        "partial_override"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;
        // Override only the middle key; key_0 and key_2 are intentionally left at defaults.
        kvs.set_value("partial_key_1", 999.0_f64)
            .map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}

/// Open KVS with a defaults file containing one key. Call get_value on that key
/// without ever calling set_value, write the retrieved value to a probe key, flush.
/// Python verifies the probe key equals the expected default, confirming that
/// feat_req__persistency__default_value_get is satisfied.
struct GetDefaultValue;

impl Scenario for GetDefaultValue {
    fn name(&self) -> &str {
        "get_default_value"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;
        // Read the default — this key has a default value but was never explicitly set.
        let default_val: f64 = kvs
            .get_value_as("default_probe_key")
            .map_err(|e| format!("Failed to read default value: {e:?}"))?;
        // Persist the retrieved value to a probe key so Python can verify it.
        kvs.set_value("result_key", default_val).map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}

/// Override all six keys, then call reset_key on even-indexed keys (0, 2, 4),
/// flush. Python verifies even-indexed keys are absent from the snapshot
/// (reverted to in-memory defaults) while odd-indexed keys (1, 3, 5) remain
/// with their override values — combining feat_req__persistency__reset_to_default,
/// feat_req__persistency__default_values, feat_req__persistency__default_value_file,
/// and feat_req__persistency__store_data in one observable storage outcome.
struct SelectiveReset;

impl Scenario for SelectiveReset {
    fn name(&self) -> &str {
        "selective_reset"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let num_keys = 6usize;
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;

        let mut keys = Vec::new();
        for i in 0..num_keys {
            let key = format!("sel_key_{i}");
            kvs.set_value(key.clone(), 100.0 * (i + 1) as f64)
                .map_err(|e| format!("{e:?}"))?;
            keys.push(key);
        }
        kvs.flush().map_err(|e| format!("{e:?}"))?;

        // Reset even-indexed keys (0, 2, 4); odd-indexed keep their overrides.
        for i in (0..num_keys).step_by(2) {
            kvs.reset_key(&keys[i]).map_err(|e| format!("{e:?}"))?;
        }
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}

/// Write four initial keys and flush, then call reset() to clear all keys, then write
/// two new keys and flush again. Python verifies all four initial keys are absent and
/// both new keys are present with the correct values — proving reset() cleared the
/// entire storage and subsequent writes persist correctly.
/// This is the only FIT scenario that exercises the "all keys" variant of
/// feat_req__persistency__reset_to_default (as opposed to reset_key which is covered
/// by SelectiveReset). Combines with feat_req__persistency__default_values,
/// feat_req__persistency__default_value_file, and feat_req__persistency__store_data.
struct FullReset;

impl Scenario for FullReset {
    fn name(&self) -> &str {
        "full_reset"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;

        // Phase 1: write four initial keys and flush.
        for i in 0..4usize {
            kvs.set_value(format!("fr_key_{i}"), 100.0 * (i + 1) as f64)
                .map_err(|e| format!("{e:?}"))?;
        }
        kvs.flush().map_err(|e| format!("{e:?}"))?;

        // Phase 2: reset ALL keys, write two new keys, flush.
        kvs.reset().map_err(|e| format!("{e:?}"))?;
        kvs.set_value("fr_new_0", 10.0_f64).map_err(|e| format!("{e:?}"))?;
        kvs.set_value("fr_new_1", 20.0_f64).map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}

pub fn default_values_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "default_values",
        vec![
            Box::new(Checksum),
            Box::new(PartialOverride),
            Box::new(GetDefaultValue),
            Box::new(SelectiveReset),
            Box::new(FullReset),
        ],
        vec![],
    ))
}
