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
    failure_detected: bool,
    daemon_timestamped_logs: bool,
    daemon_name: String,
}

impl TestInput {
    fn from_json(input: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(input).map_err(|e| e.to_string())?;
        serde_json::from_value(value["test"].clone()).map_err(|e| e.to_string())
    }
}

pub struct LoggingCorrelationScenario;

impl Scenario for LoggingCorrelationScenario {
    fn name(&self) -> &str {
        "logging_correlation"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let test_input = TestInput::from_json(input)?;

        info!(
            event = "process_logging_support",
            status = "enabled",
            daemon_name = test_input.daemon_name.as_str()
        );

        let timestamp_mode = if test_input.daemon_timestamped_logs {
            "timestamped"
        } else {
            "untimestamped"
        };

        info!(
            event = "daemon_log_timestamp",
            daemon_name = test_input.daemon_name.as_str(),
            timestamp_mode = timestamp_mode
        );

        if !test_input.failure_detected {
            info!(event = "failure_not_detected", action = "correlation_skipped");
            return Ok(());
        }

        if test_input.daemon_timestamped_logs {
            info!(
                event = "failure_diagnostic_correlated",
                status = "correlated",
                correlation_key = "pid:42@ts:1700000000"
            );
            return Ok(());
        }

        info!(
            event = "failure_diagnostic_correlation_failed",
            status = "uncorrelated",
            reason = "missing_timestamp"
        );

        Ok(())
    }
}
