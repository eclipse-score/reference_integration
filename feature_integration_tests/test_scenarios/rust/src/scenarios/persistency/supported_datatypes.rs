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
use serde_json::{json, Map, Value as JsonValue};
use std::collections::HashMap;
use test_scenarios_rust::scenario::{Scenario, ScenarioGroup, ScenarioGroupImpl};
use tracing::info;

fn kvs_value_tag(value: &KvsValue) -> &'static str {
    match value {
        KvsValue::I32(_) => "i32",
        KvsValue::U32(_) => "u32",
        KvsValue::I64(_) => "i64",
        KvsValue::U64(_) => "u64",
        KvsValue::F64(_) => "f64",
        KvsValue::Boolean(_) => "bool",
        KvsValue::String(_) => "str",
        KvsValue::Null => "null",
        KvsValue::Array(_) => "arr",
        KvsValue::Object(_) => "obj",
    }
}

fn kvs_value_to_tagged_json(value: &KvsValue) -> JsonValue {
    match value {
        KvsValue::I32(v) => json!({"t": "i32", "v": v}),
        KvsValue::U32(v) => json!({"t": "u32", "v": v}),
        KvsValue::I64(v) => json!({"t": "i64", "v": v}),
        KvsValue::U64(v) => json!({"t": "u64", "v": v}),
        KvsValue::F64(v) => json!({"t": "f64", "v": v}),
        KvsValue::Boolean(v) => json!({"t": "bool", "v": v}),
        KvsValue::String(v) => json!({"t": "str", "v": v}),
        KvsValue::Null => json!({"t": "null", "v": JsonValue::Null}),
        KvsValue::Array(values) => {
            let tagged: Vec<JsonValue> = values.iter().map(kvs_value_to_tagged_json).collect();
            json!({"t": "arr", "v": tagged})
        }
        KvsValue::Object(values) => {
            let mut map = Map::new();
            for (key, entry) in values.iter() {
                map.insert(key.clone(), kvs_value_to_tagged_json(entry));
            }
            json!({"t": "obj", "v": JsonValue::Object(map)})
        }
    }
}

struct SupportedDatatypesKeys;

impl Scenario for SupportedDatatypesKeys {
    fn name(&self) -> &str {
        "keys"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: JsonValue = serde_json::from_str(input).map_err(|e| e.to_string())?;
        let params = KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())?;
        let kvs = kvs_instance(params).map_err(|e| format!("Failed to create KVS instance: {e:?}"))?;

        // Set key-value pairs. Unit type is used for value - only key is used later on.
        let keys_to_check = vec![
            String::from("example"),
            String::from("emoji ✅❗😀"),
            String::from("greek ημα"),
        ];
        for key in keys_to_check {
            kvs.set_value(key, ()).map_err(|e| format!("{e:?}"))?;
        }

        let keys_in_kvs = kvs.get_all_keys().map_err(|e| format!("{e:?}"))?;
        for key in keys_in_kvs {
            info!(key);
        }

        Ok(())
    }
}

struct SupportedDatatypesValues {
    value: KvsValue,
}

impl Scenario for SupportedDatatypesValues {
    fn name(&self) -> &str {
        kvs_value_tag(&self.value)
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: JsonValue = serde_json::from_str(input).map_err(|e| e.to_string())?;
        let params = KvsParameters::from_value(&v["kvs_parameters_1"]).map_err(|e| e.to_string())?;
        let kvs = kvs_instance(params).map_err(|e| format!("Failed to create KVS instance: {e:?}"))?;

        kvs.set_value(self.name(), self.value.clone())
            .map_err(|e| format!("{e:?}"))?;

        let kvs_value = kvs.get_value(self.name()).map_err(|e| format!("{e:?}"))?;
        let json_value = kvs_value_to_tagged_json(&kvs_value);
        let json_str = serde_json::to_string(&json_value).map_err(|e| e.to_string())?;

        info!(key = self.name(), value = json_str);

        Ok(())
    }
}

fn supported_datatypes_i32() -> Box<dyn Scenario> {
    Box::new(SupportedDatatypesValues {
        value: KvsValue::I32(-321),
    })
}

fn supported_datatypes_u32() -> Box<dyn Scenario> {
    Box::new(SupportedDatatypesValues {
        value: KvsValue::U32(1234),
    })
}

fn supported_datatypes_i64() -> Box<dyn Scenario> {
    Box::new(SupportedDatatypesValues {
        value: KvsValue::I64(-123456789),
    })
}

fn supported_datatypes_u64() -> Box<dyn Scenario> {
    Box::new(SupportedDatatypesValues {
        value: KvsValue::U64(123456789),
    })
}

fn supported_datatypes_f64() -> Box<dyn Scenario> {
    Box::new(SupportedDatatypesValues {
        value: KvsValue::F64(-5432.1),
    })
}

fn supported_datatypes_bool() -> Box<dyn Scenario> {
    Box::new(SupportedDatatypesValues {
        value: KvsValue::Boolean(true),
    })
}

fn supported_datatypes_string() -> Box<dyn Scenario> {
    Box::new(SupportedDatatypesValues {
        value: KvsValue::String("example".to_string()),
    })
}

fn supported_datatypes_array() -> Box<dyn Scenario> {
    let hashmap = HashMap::from([("sub-number".to_string(), KvsValue::from(789.0))]);
    let array = vec![
        KvsValue::from(321.5),
        KvsValue::from(false),
        KvsValue::from("hello".to_string()),
        KvsValue::from(()),
        KvsValue::from(vec![]),
        KvsValue::from(hashmap),
    ];
    Box::new(SupportedDatatypesValues {
        value: KvsValue::Array(array),
    })
}

fn supported_datatypes_object() -> Box<dyn Scenario> {
    let hashmap = HashMap::from([("sub-number".to_string(), KvsValue::from(789.0))]);
    Box::new(SupportedDatatypesValues {
        value: KvsValue::Object(hashmap),
    })
}

fn value_types_group() -> Box<dyn ScenarioGroup> {
    let group = ScenarioGroupImpl::new(
        "values",
        vec![
            supported_datatypes_i32(),
            supported_datatypes_u32(),
            supported_datatypes_i64(),
            supported_datatypes_u64(),
            supported_datatypes_f64(),
            supported_datatypes_bool(),
            supported_datatypes_string(),
            supported_datatypes_array(),
            supported_datatypes_object(),
        ],
        vec![],
    );
    Box::new(group)
}

pub fn supported_datatypes_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "supported_datatypes",
        vec![Box::new(SupportedDatatypesKeys)],
        vec![value_types_group()],
    ))
}
