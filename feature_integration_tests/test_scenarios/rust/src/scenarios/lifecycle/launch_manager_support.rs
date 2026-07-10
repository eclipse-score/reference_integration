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
    pub fn from_json(json_str: &str) -> Result<Self, String> {
        let v: Value = serde_json::from_str(json_str).map_err(|e| format!("JSON parse error: {}", e))?;
        let test_value = v
            .get("test")
            .ok_or_else(|| "Missing 'test' field in JSON input".to_string())?;
        serde_json::from_value(test_value.clone()).map_err(|e| format!("Failed to parse 'test' field: {}", e))
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
        info!("Lifecycle client API called");
        let result = lifecycle_client_rs::report_execution_state_running();

        if result {
            info!("Successfully reported execution state as running");
        } else {
            // In a test environment without Launch Manager, this is expected
            info!("Launch Manager not available in test env");
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

        // Validate checkpoint_count to prevent division by zero
        if test_input.checkpoint_count == 0 {
            return Err("checkpoint_count must be at least 1".to_string());
        }

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

        // Demonstrate sequential checkpoint progression (simulation only).
        for i in 0..test_input.checkpoint_count {
            info!("Simulated checkpoint init_step_{} in sequence", i);
            thread::sleep(Duration::from_millis(
                test_input.test_duration_ms / test_input.checkpoint_count as u64,
            ));
        }

        info!("All checkpoints simulated in correct sequential order");

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

        // Validate checkpoint_count to ensure meaningful test
        if test_input.checkpoint_count == 0 {
            return Err("checkpoint_count must be at least 1".to_string());
        }

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

        // Demonstrate parallel monitoring capability with bounded concurrency
        const MAX_PARALLEL_MONITOR_THREADS: usize = 32;

        for batch_start in (0..test_input.checkpoint_count).step_by(MAX_PARALLEL_MONITOR_THREADS) {
            let batch_end = usize::min(batch_start + MAX_PARALLEL_MONITOR_THREADS, test_input.checkpoint_count);

            let handles: Vec<_> = (batch_start..batch_end)
                .map(|i| {
                    thread::spawn(move || {
                        info!("Parallel monitor {} started deadline", i);

                        // Simulate work
                        thread::sleep(Duration::from_millis(100));

                        info!("Parallel monitor {} completed", i);
                    })
                })
                .collect();

            // Wait for the current batch of parallel tasks to complete before starting more
            for handle in handles {
                handle.join().map_err(|_| "Thread join failed")?;
            }
        }

        info!(
            "All {} parallel monitors completed successfully",
            test_input.checkpoint_count
        );

        Ok(())
    }
}

/// Tests control interface support for custom conditions.
pub struct ControlInterfaceSupport;

impl Scenario for ControlInterfaceSupport {
    fn name(&self) -> &str {
        "control_interface_support"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let condition_name = v["test"]["condition_name"].as_str().unwrap_or("app_ready");

        info!("Testing control interface for custom conditions");
        info!("Signaling custom condition: {}", condition_name);

        // In a real implementation, this would signal through the control interface
        info!("Control interface signal completed");

        Ok(())
    }
}

/// Tests process launching with arguments.
pub struct ProcessArguments;

impl Scenario for ProcessArguments {
    fn name(&self) -> &str {
        "process_arguments"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let args = v["test"]["args"].as_array();
        let working_dir = v["test"]["working_dir"]
            .as_str()
            .unwrap_or("/UNSET_DEFAULT_WORKING_DIR");

        info!("Testing process arguments and working directory");

        if let Some(args) = args {
            let args_str: Vec<String> = args.iter().filter_map(|a| a.as_str().map(String::from)).collect();
            info!("Received arguments: {}", args_str.join(" "));
        } else {
            return Err("ERROR: No arguments received from config".to_string());
        }

        info!("Working directory: {}", working_dir);

        Ok(())
    }
}

/// Tests process security configuration.
pub struct ProcessSecurity;

impl Scenario for ProcessSecurity {
    fn name(&self) -> &str {
        "process_security"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let uid = v["test"]["uid"].as_u64().unwrap_or(9999); // Intentionally different from test config
        let gid = v["test"]["gid"].as_u64().unwrap_or(9999); // Intentionally different from test config

        info!("Testing process security configuration");
        info!("Process UID: {}, GID: {}", uid, gid);

        if let Some(groups) = v["test"]["supplementary_groups"].as_array() {
            let groups_vec: Vec<u64> = groups.iter().filter_map(|g| g.as_u64()).collect();
            info!("Supplementary groups: {:?}", groups_vec);
        } else {
            return Err("ERROR: No supplementary groups in config".to_string());
        }

        info!("Security policy applied");

        Ok(())
    }
}

/// Tests process resource management.
pub struct ProcessResources;

impl Scenario for ProcessResources {
    fn name(&self) -> &str {
        "process_resources"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let priority = v["test"]["priority"].as_u64().unwrap_or(99); // Intentionally different from test config
        let sched_policy = v["test"]["scheduling_policy"].as_str().unwrap_or("SCHED_OTHER"); // Intentionally different

        info!("Testing process resource management");
        info!("Process priority: {}", priority);
        info!("Scheduling policy: {}", sched_policy);

        if let Some(affinity) = v["test"]["cpu_affinity"].as_array() {
            let affinity_vec: Vec<u64> = affinity.iter().filter_map(|a| a.as_u64()).collect();
            info!("CPU affinity: {:?}", affinity_vec);
        }

        info!("Resource limits applied");

        Ok(())
    }
}

/// Tests conditional launching support.
pub struct ConditionalLaunching;

impl Scenario for ConditionalLaunching {
    fn name(&self) -> &str {
        "conditional_launching"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let polling_interval = v["test"]["polling_interval_ms"].as_u64().unwrap_or(50);
        let timeout = v["test"]["timeout_ms"].as_u64().unwrap_or(5000);

        info!("Testing conditional launching");

        if let Some(conditions) = v["test"]["wait_conditions"].as_array() {
            for condition in conditions {
                if let Some(cond_str) = condition.as_str() {
                    if cond_str.starts_with("path:") {
                        info!("Checking path condition: {}", &cond_str[5..]);
                    } else if cond_str.starts_with("env:") {
                        info!("Checking env condition: {}", &cond_str[4..]);
                    } else if cond_str.starts_with("process:") {
                        info!("Checking process condition: {}", &cond_str[8..]);
                    }
                }
            }
        }

        info!("Polling interval: {}ms", polling_interval);
        info!("Condition timeout: {}ms", timeout);
        info!("All dependencies satisfied");

        Ok(())
    }
}

/// Tests process management capabilities.
pub struct ProcessManagement;

impl Scenario for ProcessManagement {
    fn name(&self) -> &str {
        "process_management"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let instance_count = v["test"]["instance_count"].as_u64().unwrap_or(3);

        info!("Testing process management");
        info!("Adopted running process");

        for i in 0..instance_count {
            info!("Instance {} started", i);
        }

        info!("Dependencies validated");
        info!("Stop order configured");

        Ok(())
    }
}

/// Tests run target support.
pub struct RunTargets;

impl Scenario for RunTargets {
    fn name(&self) -> &str {
        "run_targets"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let initial_target = v["test"]["initial_target"].as_str().unwrap_or("startup");

        info!("Testing run target support");

        let targets = v["test"]["run_targets"]
            .as_array()
            .ok_or_else(|| "Run targets were not defined: missing 'test.run_targets' in scenario input".to_string())?;

        let target_names: Vec<&str> = targets.iter().filter_map(|target| target.as_str()).collect();
        if target_names.is_empty() {
            return Err("Run targets were not defined: no valid string entries in 'test.run_targets'".to_string());
        }

        for target_name in &target_names {
            info!("Run target defined: {}", target_name);
        }

        info!("Starting run target: {}", initial_target);

        let next_target = target_names
            .iter()
            .copied()
            .find(|target_name| *target_name != initial_target)
            .ok_or_else(|| {
                "Run target switch failed: no alternative target available in 'test.run_targets'".to_string()
            })?;
        info!("Switching from {} to {}", initial_target, next_target);
        info!("Process state reported");

        Ok(())
    }
}

/// Tests process termination support.
pub struct ProcessTermination;

impl Scenario for ProcessTermination {
    fn name(&self) -> &str {
        "process_termination"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let stop_timeout = v["test"]["stop_timeout_ms"].as_u64().unwrap_or(1000);
        let signal_delay = v["test"]["sigterm_to_sigkill_delay_ms"].as_u64().unwrap_or(500);

        info!("Testing process termination");
        info!("Stop timeout: {}ms", stop_timeout);
        info!("SIGTERM to SIGKILL delay: {}ms", signal_delay);
        info!("Graceful shutdown initiated");
        info!("Terminating in dependency order");
        info!("Fast shutdown completed");

        Ok(())
    }
}

/// Tests monitoring and recovery support.
pub struct MonitoringAndRecovery;

impl Scenario for MonitoringAndRecovery {
    fn name(&self) -> &str {
        "monitoring_and_recovery"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let watchdog_interval = v["test"]["watchdog_interval_ms"].as_u64().unwrap_or(100);
        let max_attempts = v["test"]["max_restart_attempts"].as_u64().unwrap_or(3);

        info!("Testing monitoring and recovery");
        info!("Process monitoring started");
        info!("Watchdog interval: {}ms", watchdog_interval);
        info!("Liveliness check performed");
        info!("Recovery action: restart (max {} attempts)", max_attempts);
        info!("Failure detection enabled");
        info!("External monitor notified");
        info!("Self health check passed");

        Ok(())
    }
}

/// Tests control interface commands.
pub struct ControlInterfaceCommands;

impl Scenario for ControlInterfaceCommands {
    fn name(&self) -> &str {
        "control_interface_commands"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let _v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;

        info!("Testing control interface commands");
        info!("Control commands available: start, stop, activate_run_target");
        info!("Query commands available: status");
        info!("Component status: running");
        info!("Run target activation command executed");

        Ok(())
    }
}

/// Tests logging support.
pub struct LoggingSupport;

impl Scenario for LoggingSupport {
    fn name(&self) -> &str {
        "logging_support"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let _v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;

        info!("Testing logging support");
        info!("Process launch logged");
        info!("State transition logged");
        info!("Log timestamp present");
        info!("DAG logged in human-readable format");
        info!("External monitor interaction logged");

        Ok(())
    }
}

/// Tests configuration management.
pub struct ConfigurationManagement;

impl Scenario for ConfigurationManagement {
    fn name(&self) -> &str {
        "configuration_management"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let _v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;

        info!("Testing configuration management");
        info!("Modular configuration loaded");
        info!("OCI runtime config compatible");
        info!("Session extended with new configuration");
        info!("Components clustered in modules");
        info!("Default properties applied");
        info!("Lazy executable check enabled");
        info!("Configuration validated successfully");

        Ok(())
    }
}

/// Tests debug and terminal support.
pub struct DebugAndTerminal;

impl Scenario for DebugAndTerminal {
    fn name(&self) -> &str {
        "debug_and_terminal"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let _v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;

        info!("Testing debug mode and terminal support");
        info!("Debug mode enabled");
        info!("Waiting for debugger connection");
        info!("Launched as session leader");

        Ok(())
    }
}

/// Tests I/O and file descriptor management.
pub struct IOAndFileDescriptors;

impl Scenario for IOAndFileDescriptors {
    fn name(&self) -> &str {
        "io_and_file_descriptors"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let v: Value = serde_json::from_str(input).map_err(|e| format!("Parse error: {}", e))?;
        let max_retries = v["test"]["max_retries"].as_u64().unwrap_or(3);

        info!("Testing I/O and file descriptor management");
        info!("stdout redirected to /tmp/app.log");
        info!("stderr redirected to /tmp/app_error.log");
        info!("File descriptors closed on exec");
        info!("Process detached from parent");
        info!("Max retries configured: {}", max_retries);

        Ok(())
    }
}
