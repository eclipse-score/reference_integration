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

#[derive(Deserialize, Debug)]
struct TestInput {
    run_target_switch_success: bool,
    orchestrator_state_synced: bool,
    from_target: String,
    to_target: String,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct OrchestratorSyncScenario;

impl Scenario for OrchestratorSyncScenario {
    fn name(&self) -> &str {
        "orchestrator_sync"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(event = "run_target_support", status = "enabled");

        if test_input.run_target_switch_success {
            info!(
                event = "run_target_switched",
                from_target = test_input.from_target.as_str(),
                to_target = test_input.to_target.as_str()
            );
        } else {
            info!(event = "run_target_switch_failed", reason = "switch_rejected");
        }

        if test_input.run_target_switch_success && test_input.orchestrator_state_synced {
            info!(event = "orchestrator_state_sync_consistent", status = "consistent");
            return Ok(());
        }

        let reason = if !test_input.run_target_switch_success {
            "run_target_switch_failed"
        } else {
            "orchestrator_state_desync"
        };
        info!(
            event = "orchestrator_state_sync_inconsistent",
            status = "inconsistent",
            reason = reason
        );

        Ok(())
    }
}
