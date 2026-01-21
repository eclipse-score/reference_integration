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

use std::path::PathBuf;
use std::time::Duration;

use kyron::runtime::*;
use kyron_foundation::prelude::*;
use logging_tracing::LogAndTraceBuilder;
use orchestration::{
    actions::{
        invoke::Invoke, sequence::SequenceBuilder, sync::SyncBuilder, trigger::TriggerBuilder,
    },
    api::{design::Design, Orchestration},
    common::DesignConfig,
    prelude::InvokeResult,
};

use rust_kvs::json_backend::JsonBackendBuilder;
use rust_kvs::prelude::*;

// Example Summary:
// This example demonstrates how to use the orchestration framework to coordinate two design programs:
// 1. Camera processing (simulates a camera producing images)
// 2. Object detection (simulates processing those images)
//
// The components communicate via events. The camera component triggers an event when an image is ready,
// which starts the object detection component. Persistency is demonstrated using a key-value store during shutdown.
// The orchestration is run using the Kyron async runtime, and the program chains are executed concurrently.

const CAMERA_IMG_READY: &str = "CameraImageReadyEvent";
const CAMERA_IMG_PROCESSED: &str = "CameraImageProcessedEvent";

async fn on_camera_image_ready() -> InvokeResult {
    info!("CAMERA LOGIC");
    // Simulate image processing
    Ok(())
}

async fn detect_objects() -> InvokeResult {
    info!("OBJECT DETECTION LOGIC!");
    // Simulate handling object detection
    Ok(())
}

async fn on_shutdown() -> InvokeResult {
    info!("Shutdown logic executed.");

    // Instance ID for KVS object instances.
    let instance_id = InstanceId(0);
    
    // Configure backend with directory path (workaround: KvsBuilder::dir() not available in Rust)
    // change back to dir, if https://github.com/eclipse-score/persistency/issues/222 is resolved.
    let backend = JsonBackendBuilder::new()
        .working_dir(PathBuf::from("./"))
        .build();
    
    let builder = KvsBuilder::new(instance_id)
        .backend(Box::new(backend))
        .kvs_load(KvsLoad::Optional);
    let kvs = builder.build().unwrap();

    kvs.set_value("number", 123.0).unwrap();
    kvs.set_value("bool", true).unwrap();

    kvs.flush().unwrap();

    Ok(())
}

fn camera_processing_component_design() -> Result<Design, CommonErrors> {
    let mut design = Design::new("CameraProcessingDesign".into(), DesignConfig::default());

    // Register events and invoke actions in design so it knows how to build task chains
    design.register_event(CAMERA_IMG_READY.into())?;
    design.register_event(CAMERA_IMG_PROCESSED.into())?;
    let on_camera_image_ready_tag =
        design.register_invoke_async("on_camera_image_ready".into(), on_camera_image_ready)?;

    // Create a program describing task chain
    design.add_program(
        "CameraProcessingProgram",
        move |design_instance, builder| {
            builder.with_run_action(
                SequenceBuilder::new()
                    .with_step(SyncBuilder::from_design(CAMERA_IMG_READY, design_instance))
                    .with_step(Invoke::from_tag(
                        &on_camera_image_ready_tag,
                        design_instance.config(),
                    ))
                    .with_step(TriggerBuilder::from_design(
                        CAMERA_IMG_PROCESSED,
                        design_instance,
                    ))
                    .build(),
            );
            Ok(())
        },
    );

    Ok(design)
}

fn detect_object_component_design() -> Result<Design, CommonErrors> {
    let mut design = Design::new("DetectObjectDesign".into(), DesignConfig::default());

    // Register events and invoke actions in design so it knows how to build task chains
    design.register_event(CAMERA_IMG_PROCESSED.into())?;
    let detect_objects_tag =
        design.register_invoke_async("detect_objects".into(), detect_objects)?;
    let on_shutdown_tag = design.register_invoke_async("on_shutdown".into(), on_shutdown)?;

    // Create a program describing task chain
    design.add_program("DetectObjectProgram", move |design_instance, builder| {
        builder
            .with_run_action(
                SequenceBuilder::new()
                    .with_step(SyncBuilder::from_design(
                        CAMERA_IMG_PROCESSED,
                        design_instance,
                    ))
                    .with_step(Invoke::from_tag(
                        &detect_objects_tag,
                        design_instance.config(),
                    ))
                    .build(),
            )
            .with_stop_action(
                Invoke::from_tag(&on_shutdown_tag, design_instance.config()),
                Duration::from_secs(2),
            );
        Ok(())
    });

    Ok(design)
}

fn main() {
    // Setup any logging framework you want to use.
    let _logger = LogAndTraceBuilder::new()
        .global_log_level(logging_tracing::Level::INFO)
        .enable_logging(true)
        .build();

    // Create runtime
    let (builder, _engine_id) = kyron::runtime::RuntimeBuilder::new().with_engine(
        ExecutionEngineBuilder::new()
            .task_queue_size(256)
            .workers(2),
    );
    let mut runtime = builder.build().unwrap();

    // Build Orchestration
    let mut orch = Orchestration::new()
        .add_design(
            camera_processing_component_design()
                .expect("Failed to create camera_processing_component_design"),
        )
        .add_design(
            detect_object_component_design()
                .expect("Failed to create detect_object_component_design"),
        )
        .design_done();

    // Specify deployment information, ie. which event is local, which timer etc
    orch.get_deployment_mut()
        .bind_events_as_local(&[CAMERA_IMG_PROCESSED.into()])
        .expect("Failed to specify event");

    orch.get_deployment_mut()
        .bind_events_as_timer(&[CAMERA_IMG_READY.into()], Duration::from_millis(30))
        .expect("Failed to specify event");

    // Create programs
    let mut program_manager = orch.into_program_manager().unwrap();
    let mut programs = program_manager.get_programs();

    // Put programs into runtime and run them
    runtime.block_on(async move {
        let mut program1 = programs.pop().unwrap();
        let mut program2 = programs.pop().unwrap();

        let h1 = kyron::spawn(async move {
            let _ = program1.run_n(3).await;
        });

        let h2 = kyron::spawn(async move {
            let _ = program2.run_n(3).await;
        });

        let _ = h1.await;
        let _ = h2.await;

        info!("Programs finished running");
    });
}
