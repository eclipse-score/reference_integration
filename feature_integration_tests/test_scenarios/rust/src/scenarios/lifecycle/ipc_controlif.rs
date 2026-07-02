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
    control_request_valid: bool,
    query_target_reachable: bool,
    control_target: String,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct IpcControlInterfaceScenario;

impl Scenario for IpcControlInterfaceScenario {
    fn name(&self) -> &str {
        "ipc_controlif"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(
            event = "controlif_ready",
            status = "active",
            control_target = test_input.control_target.as_str()
        );

        if test_input.control_request_valid {
            info!(event = "control_route", status = "routed", reason = "valid_request");
        } else {
            info!(
                event = "control_route_rejected",
                status = "rejected",
                reason = "invalid_request"
            );
        }

        if test_input.query_target_reachable {
            info!(event = "query_route", status = "routed", reason = "target_reachable");
        } else {
            info!(
                event = "query_route_failed",
                status = "failed",
                reason = "target_unreachable"
            );
        }

        Ok(())
    }
}
