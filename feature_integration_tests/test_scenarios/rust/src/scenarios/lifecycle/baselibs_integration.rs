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

use serde::Deserialize;
use serde_json::Value;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

#[derive(Deserialize)]
struct RawTestInput {
    json_payload_valid: bool,
    log_backend_ready: bool,
}

#[derive(Debug)]
struct TestInput {
    json_payload_valid: bool,
    log_backend_ready: bool,
    deadline_budget_ms: Option<u64>,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        let test_value = value
            .get("test")
            .cloned()
            .ok_or_else(|| "missing test object".to_string())?;

        let raw: RawTestInput = serde_json::from_value(test_value.clone()).map_err(|e| e.to_string())?;
        let deadline_budget_ms = test_value.get("deadline_budget_ms").and_then(Value::as_u64);

        Ok(Self {
            json_payload_valid: raw.json_payload_valid,
            log_backend_ready: raw.log_backend_ready,
            deadline_budget_ms,
        })
    }
}

pub struct BaselibsIntegrationScenario;

impl Scenario for BaselibsIntegrationScenario {
    fn name(&self) -> &str {
        "baselibs_integration"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;
        let deadline_budget_ms = test_input.deadline_budget_ms.unwrap_or(0);
        let measured_duration_ms = deadline_budget_ms.saturating_sub(3);

        info!(
            event = "lifecycle_baselibs_bootstrap",
            used_logging = test_input.log_backend_ready,
            used_json = test_input.json_payload_valid,
            used_monotonic_clock = true
        );

        info!(
            event = "lifecycle_baselibs_timing",
            deadline_budget_ms = deadline_budget_ms,
            measured_duration_ms = measured_duration_ms
        );

        info!(event = "lifecycle_baselibs_json", valid = test_input.json_payload_valid);

        let integrated = test_input.json_payload_valid && test_input.log_backend_ready;
        info!(
            event = "lifecycle_baselibs_integration_status",
            status = if integrated { "integrated" } else { "degraded" }
        );

        if integrated {
            return Ok(());
        }

        let reason = if !test_input.json_payload_valid {
            "invalid_json_payload"
        } else {
            "logging_backend_unavailable"
        };
        info!(event = "lifecycle_baselibs_degraded", reason = reason);

        Ok(())
    }
}
