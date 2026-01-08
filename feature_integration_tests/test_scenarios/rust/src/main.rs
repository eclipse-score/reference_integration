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

mod internals;
mod scenarios;

use test_scenarios_rust::cli::run_cli_app;
use test_scenarios_rust::test_context::TestContext;

use crate::scenarios::root_scenario_group;
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::Level;
use tracing_subscriber::fmt::time::FormatTime;
use tracing_subscriber::FmtSubscriber;
struct NumericUnixTime;

impl FormatTime for NumericUnixTime {
    fn format_time(&self, w: &mut tracing_subscriber::fmt::format::Writer<'_>) -> std::fmt::Result {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default();
        write!(w, "{}", now.as_secs())
    }
}

fn init_tracing_subscriber() {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::TRACE)
        .with_thread_ids(true)
        .with_timer(NumericUnixTime)
        .json()
        .finish();

    tracing::subscriber::set_global_default(subscriber)
        .expect("Setting default subscriber failed!");
}

fn main() -> Result<(), String> {
    let raw_arguments: Vec<String> = std::env::args().collect();

    // Root group.
    let root_group = root_scenario_group();

    // Run.
    init_tracing_subscriber();
    let test_context = TestContext::new(root_group);
    run_cli_app(&raw_arguments, &test_context)
}
