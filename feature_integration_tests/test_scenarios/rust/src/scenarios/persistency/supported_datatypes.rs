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
use serde_json::Value as JsonValue;
use std::collections::HashMap;
use test_scenarios_rust::scenario::{Scenario, ScenarioGroup, ScenarioGroupImpl};

/// Write all nine value types under ASCII key names in a single flush.
/// Python reads the snapshot and verifies every key is present with the correct
/// type tag and value — proving that primitive and composite types coexist
/// without interference in one atomic storage outcome.
/// Combines feat_req__persistency__support_datatype_value,
/// feat_req__persistency__support_datatype_keys, and
/// feat_req__persistency__store_data.
struct AllValueTypes;

impl Scenario for AllValueTypes {
    fn name(&self) -> &str {
        "all_value_types"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: JsonValue = serde_json::from_str(input).map_err(|e| e.to_string())?;
        let params = KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;

        let nested_obj = HashMap::from([("sub-number".to_string(), KvsValue::from(789.0))]);
        let array = vec![
            KvsValue::from(321.5),
            KvsValue::from(false),
            KvsValue::from("hello".to_string()),
            KvsValue::from(()),
            KvsValue::from(vec![]),
            KvsValue::from(nested_obj.clone()),
        ];

        kvs.set_value("i32_key", KvsValue::I32(-321))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("u32_key", KvsValue::U32(1234))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("i64_key", KvsValue::I64(-123456789))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("u64_key", KvsValue::U64(123456789))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("f64_key", KvsValue::F64(-5432.1))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("bool_key", KvsValue::Boolean(true))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("str_key", KvsValue::String("example".to_string()))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("arr_key", KvsValue::Array(array))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("obj_key", KvsValue::Object(nested_obj))
            .map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}

/// Write five values with mixed types under both ASCII and UTF-8 key names,
/// then flush. Python reads the single snapshot and verifies every key is
/// present with the correct type tag and value — combining key-encoding and
/// value-type requirements in one observable storage outcome.
struct AllTypesUtf8;

impl Scenario for AllTypesUtf8 {
    fn name(&self) -> &str {
        "all_types_utf8"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: JsonValue = serde_json::from_str(input).map_err(|e| e.to_string())?;
        let params = KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())?;
        let kvs = kvs_instance(params).map_err(|e| format!("{e:?}"))?;

        kvs.set_value("ascii_i32", KvsValue::I32(-321))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("emoji_f64 🎯", KvsValue::F64(3.14))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("greek_bool αβγ", KvsValue::Boolean(true))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("ascii_str", KvsValue::String("hello".to_string()))
            .map_err(|e| format!("{e:?}"))?;
        kvs.set_value("ascii_null", KvsValue::Null)
            .map_err(|e| format!("{e:?}"))?;
        kvs.flush().map_err(|e| format!("{e:?}"))?;
        Ok(())
    }
}

pub fn supported_datatypes_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "supported_datatypes",
        vec![Box::new(AllValueTypes), Box::new(AllTypesUtf8)],
        vec![],
    ))
}
