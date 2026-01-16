//
// Copyright (c) 2025 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// <https://www.apache.org/licenses/LICENSE-2.0>
//
// SPDX-License-Identifier: Apache-2.0
//
use crate::internals::kyron::runtime_helper::Runtime;
use kyron_foundation::containers::Vector;
use kyron_foundation::prelude::CommonErrors;
use orchestration::prelude::*;
use orchestration::{
    api::{design::Design, Orchestration},
    common::DesignConfig,
};
use rust_kvs::prelude::{InstanceId, KvsDefaults, KvsLoad, KvsMap, KvsValue};
use rust_kvs::{kvs_api::KvsApi, Kvs, KvsBuilder};
use serde_json::Value;
use std::{sync::Arc, vec};
use test_scenarios_rust::scenario::Scenario;
use tracing::{field, info};

use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct TestInput {
    run_count: usize,
    kvs_path: String,
}

impl TestInput {
    pub fn new(input: &str) -> Self {
        let v: Value = serde_json::from_str(input).expect("Failed to parse input string");
        serde_json::from_value(v["test"].clone()).expect("Failed to parse \"test\" field")
    }
}

fn create_kvs(instance_id: usize, path: String) -> Arc<Kvs> {
    let builder = KvsBuilder::new(InstanceId(instance_id))
        .defaults(KvsDefaults::Optional)
        .dir(path.clone())
        .kvs_load(KvsLoad::Optional)
        .snapshot_max_count(3);

    let kvs = builder.build().expect("Failed to build KVS instance");
    Arc::new(kvs)
}

macro_rules! persistency_cycle_task {
    ($kvs:expr) => {{
        let kvs = Arc::clone(&$kvs);
        move || kvs_save_cycle_number(Arc::clone(&kvs))
    }};
}

async fn kvs_save_cycle_number(kvs: Arc<Kvs>) -> Result<(), UserErrValue> {
    let key = "run_cycle_number";
    let last_cycle_number: u32 = kvs.get_value_as::<u32>(key).unwrap_or_else(|_| 0_u32);

    kvs.set_value(key, last_cycle_number + 1)
        .expect("Failed to set value");
    let value_read = kvs.get_value_as::<u32>(key).expect("Failed to read value");

    kvs.flush().expect("Failed to flush KVS");

    info!(
        kvs_instance_id = field::debug(kvs.parameters().instance_id),
        run_cycle_number = value_read
    );

    Ok(())
}

macro_rules! persistency_save_task {
    ($kvs:expr) => {{
        let kvs = Arc::clone(&$kvs);
        move || kvs_save_data(Arc::clone(&kvs))
    }};
}

async fn kvs_save_data(kvs: Arc<Kvs>) -> Result<(), UserErrValue> {
    // i32
    kvs.set_value("key_i32_min", i32::MIN)
        .expect("Failed to set value");
    kvs.set_value("key_i32_max", i32::MAX)
        .expect("Failed to set value");
    // u32
    kvs.set_value("key_u32_min", u32::MIN)
        .expect("Failed to set value");
    kvs.set_value("key_u32_max", u32::MAX)
        .expect("Failed to set value");
    // i64
    kvs.set_value("key_i64_min", i64::MIN)
        .expect("Failed to set value");
    kvs.set_value("key_i64_max", i64::MAX)
        .expect("Failed to set value");
    // u64
    kvs.set_value("key_u64_min", u64::MIN)
        .expect("Failed to set value");
    kvs.set_value("key_u64_max", u64::MAX)
        .expect("Failed to set value");
    // f64
    kvs.set_value("key_f64", 1.2345_f64)
        .expect("Failed to set value");
    // bool
    kvs.set_value("key_bool", true)
        .expect("Failed to set value");
    // String
    kvs.set_value("key_String", "TestString".to_string())
        .expect("Failed to set value");
    // Null
    kvs.set_value("key_Null", KvsValue::Null)
        .expect("Failed to set value");
    // Array
    kvs.set_value(
        "key_Array",
        vec![
            KvsValue::from(1i32),
            KvsValue::from(2i32),
            KvsValue::from(3i32),
        ],
    )
    .expect("Failed to set value");
    // Map
    let mut map = KvsMap::new();
    map.insert("inner_key".to_string(), KvsValue::from(1i32));
    kvs.set_value("key_Map", map).expect("Failed to set value");

    kvs.flush().expect("Failed to flush KVS");

    Ok(())
}

fn single_sequence_design(kvs_path: String) -> Result<Design, CommonErrors> {
    let mut design = Design::new("SingleSequence".into(), DesignConfig::default());
    let kvs = create_kvs(1, kvs_path);
    let kvs_cycle_tag =
        design.register_invoke_async("KVS save cycle".into(), persistency_cycle_task!(kvs))?;

    design.add_program(file!(), move |_design_instance, builder| {
        builder.with_run_action(
            SequenceBuilder::new()
                .with_step(Invoke::from_tag(&kvs_cycle_tag, _design_instance.config()))
                .build(),
        );
        Ok(())
    });

    Ok(design)
}

pub struct OrchestrationWithPersistency;

impl Scenario for OrchestrationWithPersistency {
    fn name(&self) -> &str {
        "orchestration_with_persistency"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let logic = TestInput::new(input);
        let mut rt = Runtime::from_json(input)?.build();

        let orch = Orchestration::new()
            .add_design(single_sequence_design(logic.kvs_path).expect("Failed to create design"))
            .design_done();

        let mut program_manager = orch
            .into_program_manager()
            .expect("Failed to create programs");
        let mut programs = program_manager.get_programs();

        rt.block_on(async move {
            let mut program = programs.pop().expect("Failed to pop program");
            let _ = program.run_n(logic.run_count).await;
        });

        Ok(())
    }
}

fn concurrent_kvs_design(kvs_path: String) -> Result<Design, CommonErrors> {
    let mut design = Design::new("ConcurrentKvs".into(), DesignConfig::default());

    let kvs1 = create_kvs(1, kvs_path.clone());
    let kvs1_tag =
        design.register_invoke_async("KVS1 save cycle".into(), persistency_cycle_task!(kvs1))?;

    let kvs2 = create_kvs(2, kvs_path.clone());
    let kvs2_tag =
        design.register_invoke_async("KVS2 save cycle".into(), persistency_cycle_task!(kvs2))?;

    let kvs3 = create_kvs(3, kvs_path.clone());
    let kvs3_tag =
        design.register_invoke_async("KVS3 save cycle".into(), persistency_cycle_task!(kvs3))?;

    design.add_program(file!(), move |_design_instance, builder| {
        builder.with_run_action(
            ConcurrencyBuilder::new()
                .with_branch(Invoke::from_tag(&kvs1_tag, _design_instance.config()))
                .with_branch(Invoke::from_tag(&kvs2_tag, _design_instance.config()))
                .with_branch(Invoke::from_tag(&kvs3_tag, _design_instance.config()))
                .build(_design_instance),
        );
        Ok(())
    });

    Ok(design)
}

pub struct ConcurrentKvsOrchestrationWithPersistency;

impl Scenario for ConcurrentKvsOrchestrationWithPersistency {
    fn name(&self) -> &str {
        "concurrent_kvs"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let logic = TestInput::new(input);
        let mut rt = Runtime::from_json(input)?.build();

        let orch = Orchestration::new()
            .add_design(concurrent_kvs_design(logic.kvs_path).expect("Failed to create design"))
            .design_done();

        let mut program_manager = orch
            .into_program_manager()
            .expect("Failed to create programs");
        let mut programs = program_manager.get_programs();

        rt.block_on(async move {
            let mut program = programs.pop().expect("Failed to pop program");
            let _ = program.run_n(logic.run_count).await;
        });

        Ok(())
    }
}

fn multiple_kvs_design(kvs_path: String) -> Result<Design, CommonErrors> {
    let mut design = Design::new("ConcurrentKvs".into(), DesignConfig::default());

    let kvs1 = create_kvs(1, kvs_path.clone());
    let kvs1_tag =
        design.register_invoke_async("KVS1 save cycle".into(), persistency_cycle_task!(kvs1))?;

    let kvs2 = create_kvs(2, kvs_path.clone());
    let kvs2_tag =
        design.register_invoke_async("KVS2 save cycle".into(), persistency_save_task!(kvs2))?;

    design.add_program(file!(), move |_design_instance, builder| {
        builder.with_run_action(
            ConcurrencyBuilder::new()
                .with_branch(Invoke::from_tag(&kvs1_tag, _design_instance.config()))
                .with_branch(Invoke::from_tag(&kvs2_tag, _design_instance.config()))
                .build(_design_instance),
        );
        Ok(())
    });

    Ok(design)
}

pub struct MultipleKvsOrchestrationWithPersistency;

impl Scenario for MultipleKvsOrchestrationWithPersistency {
    fn name(&self) -> &str {
        "multiple_kvs"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let logic = TestInput::new(input);
        let mut rt = Runtime::from_json(input)?.build();

        let orch = Orchestration::new()
            .add_design(multiple_kvs_design(logic.kvs_path).expect("Failed to create design"))
            .design_done();

        let mut program_manager = orch
            .into_program_manager()
            .expect("Failed to create programs");
        let mut programs = program_manager.get_programs();

        rt.block_on(async move {
            let mut program = programs.pop().expect("Failed to pop program");
            let _ = program.run_n(logic.run_count).await;
        });

        Ok(())
    }
}
