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

use serde_json::Value;
use std::fs;
use std::path::Path;
use std::time::{Duration, Instant};
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

pub struct ConditionalLaunching;

fn path_condition_met(path: &str) -> bool {
    Path::new(path).exists()
}

fn env_condition_met(name: &str) -> bool {
    std::env::var_os(name).is_some()
}

/// Best-effort check whether a process matching `process_name` is currently running, by
/// scanning /proc/<pid>/comm (kernel-truncated to 15 chars) and /proc/<pid>/cmdline (full
/// argv[0], which covers names `comm` truncates).
fn process_condition_met(process_name: &str) -> bool {
    let Ok(entries) = fs::read_dir("/proc") else {
        return false;
    };

    for entry in entries.flatten() {
        let pid = entry.file_name();
        let Some(pid) = pid.to_str() else { continue };
        if !pid.chars().all(|c| c.is_ascii_digit()) {
            continue;
        }

        if let Ok(comm) = fs::read_to_string(entry.path().join("comm")) {
            if comm.trim_end() == process_name {
                return true;
            }
        }

        if let Ok(cmdline) = fs::read(entry.path().join("cmdline")) {
            let argv0 = cmdline.split(|&b| b == 0).next().unwrap_or(&[]);
            if let Ok(argv0) = std::str::from_utf8(argv0) {
                // Compare the basename only: a raw suffix match on the full path would also
                // accept e.g. "/usr/bin/oversleep" as satisfying process_name="sleep".
                let basename = argv0.rsplit('/').next().unwrap_or(argv0);
                if basename == process_name {
                    return true;
                }
            }
        }
    }
    false
}

impl Scenario for ConditionalLaunching {
    fn name(&self) -> &str {
        "conditional_launching"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let value: Value = serde_json::from_str(input).map_err(|error| format!("Parse error: {error}"))?;
        let test = value
            .get("test")
            .ok_or_else(|| "Missing 'test' field in scenario input".to_string())?;

        let polling_interval = test.get("polling_interval_ms").and_then(Value::as_u64).unwrap_or(50);
        let timeout = test.get("timeout_ms").and_then(Value::as_u64).unwrap_or(5000);
        let conditions = test.get("wait_conditions").and_then(Value::as_array).ok_or_else(|| {
            "Wait conditions were not provided: missing 'test.wait_conditions' in scenario input".to_string()
        })?;

        if conditions.is_empty() {
            return Err(
                "Wait conditions were not provided: empty 'test.wait_conditions' in scenario input".to_string(),
            );
        }

        info!("Testing conditional launching");

        let conditions: Vec<&str> = conditions
            .iter()
            .map(|condition| {
                condition
                    .as_str()
                    .ok_or_else(|| "Wait condition entries must be strings".to_string())
            })
            .collect::<Result<_, _>>()?;

        for condition in &conditions {
            if !condition.starts_with("path:") && !condition.starts_with("env:") && !condition.starts_with("process:") {
                return Err(format!("Unsupported wait condition prefix: {condition}"));
            }
        }

        info!("Polling interval: {polling_interval}ms");
        info!("Condition timeout: {timeout}ms");

        let deadline = Instant::now() + Duration::from_millis(timeout);
        let mut satisfied = vec![false; conditions.len()];

        loop {
            let mut all_satisfied = true;
            for (index, condition) in conditions.iter().enumerate() {
                if satisfied[index] {
                    continue;
                }

                let met = if let Some(path) = condition.strip_prefix("path:") {
                    path_condition_met(path)
                } else if let Some(name) = condition.strip_prefix("env:") {
                    env_condition_met(name)
                } else {
                    process_condition_met(condition.strip_prefix("process:").expect("checked above"))
                };

                if met {
                    satisfied[index] = true;
                    info!("Condition satisfied: {condition}");
                } else {
                    all_satisfied = false;
                }
            }

            if all_satisfied {
                break;
            }

            if Instant::now() >= deadline {
                let unmet = conditions
                    .iter()
                    .zip(&satisfied)
                    .filter(|(_, met)| !**met)
                    .map(|(condition, _)| *condition)
                    .collect::<Vec<&str>>()
                    .join(", ");
                return Err(format!("Timed out after {timeout}ms waiting for condition(s): {unmet}"));
            }

            std::thread::sleep(Duration::from_millis(polling_interval));
        }

        info!("All dependencies satisfied");

        Ok(())
    }
}
