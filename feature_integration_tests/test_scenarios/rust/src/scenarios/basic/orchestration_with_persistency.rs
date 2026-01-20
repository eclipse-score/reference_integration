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

use rust_kvs::json_backend::JsonBackendBuilder;
use rust_kvs::kvs_api::KvsApi;
use rust_kvs::prelude::{Kvs, KvsBuilder};
use serde_json::Value;

use test_scenarios_rust::scenario::Scenario;
use tracing::info;

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

use rust_kvs::prelude::{InstanceId, KvsDefaults, KvsLoad};
use std::path::PathBuf;
pub struct KvsParameters {
    pub instance_id: InstanceId,
    pub defaults: Option<KvsDefaults>,
    pub kvs_load: Option<KvsLoad>,
    pub dir: Option<PathBuf>,
    pub snapshot_max_count: Option<usize>,
}

macro_rules! persistency_task {
    ($path:expr) => {
        move || kvs_save_cycle_number($path.clone())
    };
}

async fn kvs_save_cycle_number(path: String) -> Result<(), UserErrValue> {
    let params = KvsParameters {
        instance_id: InstanceId(1),
        defaults: Some(KvsDefaults::Optional),
        kvs_load: Some(KvsLoad::Optional),
        dir: Some(PathBuf::from(path)),
        snapshot_max_count: Some(3),
    };

    // Set builder parameters.
    let mut builder = KvsBuilder::new(params.instance_id);
    if let Some(flag) = params.defaults {
        builder = builder.defaults(flag);
    }
    if let Some(flag) = params.kvs_load {
        builder = builder.kvs_load(flag);
    }
    if let Some(dir) = params.dir {
        // Use JsonBackendBuilder to configure directory (dir() method not available in Rust KvsBuilder)
        // change back to dir, if https://github.com/eclipse-score/persistency/issues/222 is resolved.
        let backend = JsonBackendBuilder::new()
            .working_dir(dir)
            .snapshot_max_count(params.snapshot_max_count.unwrap_or(1))
            .build();
        builder = builder.backend(Box::new(backend));
    } else if let Some(max_count) = params.snapshot_max_count {
        // Configure snapshot_max_count via backend even without custom dir
        let backend = JsonBackendBuilder::new()
            .snapshot_max_count(max_count)
            .build();
        builder = builder.backend(Box::new(backend));
    }

    // Create KVS.
    let kvs: Kvs = builder.build().expect("Failed to build KVS instance");

    // Simple set/get.
    let key = "run_cycle_number";
    let last_cycle_number: u32 = kvs.get_value_as::<u32>(key).unwrap_or_else(|_| 0_u32);

    kvs.set_value(key, last_cycle_number + 1)
        .expect("Failed to set value");
    let value_read = kvs.get_value_as::<u32>(key).expect("Failed to read value");

    kvs.flush().expect("Failed to flush KVS");

    info!(run_cycle_number = value_read);

    Ok(())
}

fn single_sequence_design(kvs_path: String) -> Result<Design, CommonErrors> {
    let mut design = Design::new("SingleSequence".into(), DesignConfig::default());
    let kvs_cycle_tag =
        design.register_invoke_async("KVS save cycle".into(), persistency_task!(kvs_path))?;

    // Create a program with actions
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
