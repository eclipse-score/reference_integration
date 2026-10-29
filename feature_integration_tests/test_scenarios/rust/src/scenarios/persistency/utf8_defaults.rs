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
use rust_kvs::prelude::{ErrorCode, KvsApi};
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;

fn parse_params(input: &str) -> Result<KvsParameters, String> {
    let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
    KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())
}

/// Open a KVS whose defaults file contains keys with non-ASCII UTF-8
/// characters. KVS keys must be printable ASCII, so opening must fail with
/// InvalidKey; the scenario fails if the KVS accepts the file or fails for
/// another reason. Python verifies the scenario
/// succeeded and that no snapshot was written.
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
        match kvs_instance(params) {
            Ok(_) => Err("KVS accepted a defaults file with non-ASCII keys".to_string()),
            Err(ErrorCode::InvalidKey) => Ok(()),
            Err(e) => Err(format!("Expected InvalidKey, got {e:?}")),
        }
    }
}

/// Read a default value whose key uses printable ASCII punctuation and a space
/// (the edges of the allowed key characters) without ever calling set_value on
/// it. Write the retrieved value to an ASCII result key and flush.
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
        let default_val: f64 =
            get_default_value_f64(&kvs, "probe ~!#$%").map_err(|e| format!("Failed to read default value: {e:?}"))?;
        // Persist to a plain result key so Python can verify it independently.
        kvs.set_value("result_key", default_val).map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}
