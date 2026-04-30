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
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;

/// Write key_a to instance 1 and key_b to instance 2 within a shared directory.
///
/// Python verifies snapshot isolation: the snapshot of instance 1 contains
/// key_a but not key_b, and the snapshot of instance 2 contains key_b but
/// not key_a.  This proves that default values loaded for one KVS instance
/// do not leak into a second instance sharing the same working directory.
///
/// Partially verifies feat_req__persistency__default_values and
/// feat_req__persistency__multiple_kvs.
pub struct MultiInstanceIsolation;

impl Scenario for MultiInstanceIsolation {
    fn name(&self) -> &str {
        "multi_instance_isolation"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;

        let params1 =
            KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())?;
        let params2 =
            KvsParameters::from_value(&v["kvs_parameters_2"]).map_err(|e| e.to_string())?;

        // Write key_a exclusively to instance 1.
        let kvs1 = kvs_instance(params1).map_err(|e| format!("{e:?}"))?;
        kvs1.set_value("key_a", 11.0_f64)
            .map_err(|e| format!("Failed to set key_a: {e:?}"))?;
        kvs1.flush().map_err(|e| format!("Failed to flush instance 1: {e:?}"))?;

        // Write key_b exclusively to instance 2.
        let kvs2 = kvs_instance(params2).map_err(|e| format!("{e:?}"))?;
        kvs2.set_value("key_b", 22.0_f64)
            .map_err(|e| format!("Failed to set key_b: {e:?}"))?;
        kvs2.flush().map_err(|e| format!("Failed to flush instance 2: {e:?}"))?;

        Ok(())
    }
}
