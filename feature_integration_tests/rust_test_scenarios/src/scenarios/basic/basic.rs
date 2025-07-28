use crate::internals::helpers::runtime_helper::Runtime;
use crate::internals::scenario::Scenario;

use foundation::prelude::*;
use orchestration::{
    api::{Orchestration, design::Design},
    common::DesignConfig,
    prelude::{Invoke, SequenceBuilder, UserErrValue},
};
use rust_kvs::Kvs;
use rust_kvs::kvs_api::KvsApi;
use rust_kvs::kvs_api::{InstanceId, OpenNeedDefaults, OpenNeedKvs};
use rust_kvs::kvs_value::KvsValue;

use tracing::info;

fn kvs_save_cycle_number() -> Result<(), UserErrValue> {
    let kvs: Kvs = KvsApi::open(
        InstanceId::new(0),
        OpenNeedDefaults::Required,
        OpenNeedKvs::Optional,
        Some("/app/test_data".to_string()),
    )
    .expect("Failed to open KVS");

    let key = "cycle_counter".to_string();
    let last_cycle = kvs
        .get_value_as::<f64>(&key)
        .expect("Failed to get value from KVS");
    let current_cycle = last_cycle as u32 + 1;

    kvs.set_value(key, KvsValue::Number(current_cycle.into()))
        .expect("Failed to set value in KVS");

    Ok(())
}

fn single_sequence_design() -> Result<Design, CommonErrors> {
    let mut design = Design::new("SingleSequence".into(), DesignConfig::default());
    let kvs_cycle_tag =
        design.register_invoke_fn("KVS save cycle".into(), kvs_save_cycle_number)?;

    // Create a program with actions
    design.add_program(file!(), move |_design_instance, builder| {
        builder.with_run_action(
            SequenceBuilder::new()
                .with_step(Invoke::from_tag(&kvs_cycle_tag))
                .build(),
        );

        Ok(())
    });

    Ok(design)
}

pub struct CycleCounter;

/// Scenario that runs a cycle to increment counter stored by Persistency
impl Scenario for CycleCounter {
    fn get_name(&self) -> &'static str {
        "cycle_counter"
    }

    fn run(&self, input: Option<String>) -> Result<(), String> {
        let mut runtime = Runtime::new(&input).build();

        // Create orchestration
        let orch = Orchestration::new()
            .add_design(single_sequence_design().expect("Failed to create design"))
            .design_done();

        // Create programs
        let mut programs = orch.create_programs().unwrap();

        // Put programs into runtime and run them
        let _ = runtime.block_on(async move {
            let _ = programs.programs.pop().unwrap().run_n(1).await;
            info!("Program finished running.");
            Ok(0)
        });
        Ok(())
    }
}
