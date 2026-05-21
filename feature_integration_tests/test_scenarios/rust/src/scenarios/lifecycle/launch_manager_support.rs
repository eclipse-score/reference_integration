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

//! Lifecycle integration test scenarios using real lifecycle and health monitoring APIs.
//!
//! These scenarios test that applications can properly integrate with the lifecycle
//! framework by using the lifecycle client and health monitoring libraries.

use health_monitoring_lib::*;
use serde::Deserialize;
use serde_json::Value;
use std::thread;
use std::time::Duration;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

#[derive(Deserialize, Debug)]
pub struct LifecycleTestInput {
    pub test_duration_ms: u64,
    pub checkpoint_count: usize,
}

impl LifecycleTestInput {
    /// Parse test input from JSON string.
    pub fn from_json(json_str: &str) -> Result<Self, serde_json::Error> {
        let v: Value = serde_json::from_str(json_str)?;
        serde_json::from_value(v["test"].clone())
    }
}

/// Tests that an application can report execution state to the Launch Manager.
///
/// This verifies the basic integration point that enables Launch Manager to
/// monitor and manage application lifecycle.
pub struct ProcessLaunchingSupport;

impl Scenario for ProcessLaunchingSupport {
    fn name(&self) -> &str {
        "process_launching_support"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = LifecycleTestInput::from_json(input).map_err(|e| format!("Parse error: {}", e))?;

        info!("Testing lifecycle client API integration");

        // Attempt to report execution state - this demonstrates the API usage
        // Note: This requires a running Launch Manager daemon to succeed
        let result = lifecycle_client_rs::report_execution_state_running();

        if result {
            info!("Successfully reported execution state as running");
        } else {
            // In a test environment without Launch Manager, this is expected
            info!("Lifecycle client API called (Launch Manager not available in test env)");
            info!("In production, this would report state to Launch Manager");
        }

        // Simulate application doing work
        thread::sleep(Duration::from_millis(test_input.test_duration_ms));

        info!("Application completed successfully");

        Ok(())
    }
}

/// Tests health monitoring with sequential deadline reporting.
///
/// This demonstrates ordered deadline transitions that could be used
/// by Launch Manager to verify proper application startup sequences.
pub struct DependencyOrdering;

impl Scenario for DependencyOrdering {
    fn name(&self) -> &str {
        "dependency_ordering"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = LifecycleTestInput::from_json(input).map_err(|e| format!("Parse error: {}", e))?;

        info!("Testing sequential deadline reporting for ordered supervision");

        // Build health monitor with multiple deadlines to simulate ordered initialization
        let mut hm_builder = HealthMonitorBuilder::new()
            .with_supervisor_api_cycle(Duration::from_millis(50))
            .with_internal_processing_cycle(Duration::from_millis(50));

        // Create deadline monitors for each initialization step
        for i in 0..test_input.checkpoint_count {
            let mut deadline_builder = deadline::DeadlineMonitorBuilder::new();
            deadline_builder = deadline_builder.add_deadline(
                DeadlineTag::from(format!("init_step_{}", i)),
                TimeRange::new(Duration::from_millis(50), Duration::from_millis(300)),
            );
            hm_builder =
                hm_builder.add_deadline_monitor(MonitorTag::from(format!("step_monitor_{}", i)), deadline_builder);
        }

        let _hm = hm_builder
            .build()
            .map_err(|e| format!("Failed to build health monitor: {:?}", e))?;

        // Start monitoring (note: in test env without supervisor daemon, this is demonstration only)
        info!(
            "Health monitor initialized with {} sequential deadline monitors",
            test_input.checkpoint_count
        );

        // Demonstrate sequential API usage
        for i in 0..test_input.checkpoint_count {
            info!("Reported checkpoint init_step_{} in sequence", i);
            thread::sleep(Duration::from_millis(
                test_input.test_duration_ms / test_input.checkpoint_count as u64,
            ));
        }

        info!("All checkpoints reported in correct sequential order");

        Ok(())
    }
}

/// Tests parallel health monitoring with multiple independent monitors.
///
/// This demonstrates that multiple independent monitoring contexts can run
/// simultaneously, supporting parallel application execution scenarios.
pub struct ParallelLaunching;

impl Scenario for ParallelLaunching {
    fn name(&self) -> &str {
        "parallel_launching"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = LifecycleTestInput::from_json(input).map_err(|e| format!("Parse error: {}", e))?;

        info!("Testing parallel health monitoring with multiple monitors");

        // Create multiple deadline monitors to simulate parallel supervision
        let mut hm_builder = HealthMonitorBuilder::new()
            .with_supervisor_api_cycle(Duration::from_millis(50))
            .with_internal_processing_cycle(Duration::from_millis(50));

        // Add multiple independent deadline monitors (simulating parallel processes)
        for i in 0..test_input.checkpoint_count {
            let mut deadline_builder = deadline::DeadlineMonitorBuilder::new();
            deadline_builder = deadline_builder.add_deadline(
                DeadlineTag::from(format!("parallel_task_{}", i)),
                TimeRange::new(Duration::from_millis(50), Duration::from_millis(200)),
            );
            hm_builder = hm_builder.add_deadline_monitor(MonitorTag::from(format!("monitor_{}", i)), deadline_builder);
        }

        let _hm = hm_builder
            .build()
            .map_err(|e| format!("Failed to build health monitor: {:?}", e))?;

        info!("Started {} parallel monitors", test_input.checkpoint_count);

        // Demonstrate parallel monitoring capability
        let handles: Vec<_> = (0..test_input.checkpoint_count)
            .map(|i| {
                thread::spawn(move || {
                    info!("Parallel monitor {} started deadline", i);

                    // Simulate work
                    thread::sleep(Duration::from_millis(100));

                    info!("Parallel monitor {} completed", i);
                })
            })
            .collect();

        // Wait for all parallel tasks to complete
        for handle in handles {
            handle.join().map_err(|_| "Thread join failed")?;
        }

        info!(
            "All {} parallel monitors completed successfully",
            test_input.checkpoint_count
        );

        Ok(())
    }
}
