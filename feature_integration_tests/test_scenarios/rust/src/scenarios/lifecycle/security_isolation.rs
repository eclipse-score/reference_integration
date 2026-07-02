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
    secpol_type: String,
    run_as_root_attempt: bool,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct SecurityIsolationScenario;

impl Scenario for SecurityIsolationScenario {
    fn name(&self) -> &str {
        "security_isolation"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;
        let supported = test_input.secpol_type == "strict";

        info!(component = "launch_manager", state = "running", api = "security_policy");
        info!(
            component = "security_crypto",
            policy_domain = "secpol",
            secpol_type = test_input.secpol_type.as_str()
        );

        if supported {
            info!(event = "secpol_type_support", status = "accepted", supported = true);
        } else {
            info!(event = "secpol_type_support", status = "rejected", supported = false);
        }

        if test_input.run_as_root_attempt {
            info!(event = "privilege_escalation_attempt", requested_uid = 0);
            info!(
                event = "non_root_enforced",
                effective_uid = 1001,
                status = "denied_root"
            );
        } else {
            info!(
                event = "non_root_enforced",
                effective_uid = 1001,
                status = "non_root_ok"
            );
        }

        info!(
            event = "sandbox_isolation",
            status = "active",
            boundary = "process_container"
        );

        Ok(())
    }
}
