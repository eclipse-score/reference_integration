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
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

fn parse_params(input: &str) -> Result<KvsParameters, String> {
    let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
    KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())
}

/// Open a KVS whose defaults file was created with printable-ASCII key names with spaces and punctuation.
/// Override only the punctuation key and flush. Python verifies:
/// - the punctuation key appears in the snapshot with the override value
/// - the plain and space keys are absent from the snapshot (never explicitly written)
///
/// Combines feat_req__persistency__support_datatype_keys,
/// feat_req__persistency__default_values, and
/// feat_req__persistency__default_value_file.
pub struct Utf8Defaults;

impl Scenario for Utf8Defaults {
    fn name(&self) -> &str {
        "utf8_defaults"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;

        // Override only the punctuation key; plain and space keys are intentionally left as defaults.
        kvs.set_value("ascii_punct_key !?", 777.0_f64)
            .map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        // Log default values for plain and space keys so Python can assert accessibility.
        let val_ascii: f64 = get_default_value_f64(&kvs, "utf8_ascii_key")
            .map_err(|e| format!("Failed to read default utf8_ascii_key: {e:?}"))?;
        let val_space: f64 = get_default_value_f64(&kvs, "ascii_space key")
            .map_err(|e| format!("Failed to read default ascii_space key: {e:?}"))?;
        info!(key = "utf8_ascii_key", value = val_ascii, source = "default");
        info!(key = "ascii_space key", value = val_space, source = "default");
        Ok(())
    }
}

/// Read a default value whose key is a punctuation string without ever calling
/// set_value on it. Write the retrieved value to an ASCII result key and flush.
/// Python verifies the result key equals the expected default, combining
/// feat_req__persistency__default_value_get with
/// feat_req__persistency__support_datatype_keys in one observable storage outcome.
pub struct Utf8DefaultValueGet;

impl Scenario for Utf8DefaultValueGet {
    fn name(&self) -> &str {
        "utf8_default_value_get"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let params = parse_params(input)?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;
        // Read the default value via a punctuation key — never explicitly set.
        let default_val: f64 = get_default_value_f64(&kvs, "probe key ~!")
            .map_err(|e| format!("Failed to read punctuation default value: {e:?}"))?;
        // Persist to an ASCII result key so Python can verify without special-character key lookup.
        kvs.set_value("result_key", default_val).map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}
