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

// The normal FIT binary builds the full scenario tree, which includes persistency
// scenarios and their transitive dependencies.
#[cfg(not(lifecycle_only))]
mod internals;
#[cfg(not(lifecycle_only))]
mod scenarios;
// The lifecycle-only build reuses this same entrypoint but limits compilation to
// lifecycle scenarios. This is needed because the conditional-launching FIT only
// exercises lifecycle behavior, while the full Rust FIT binary currently pulls in
// score_persistency/rust_kvs where ScoreDebug-related path logging compilation
// issues are still unresolved upstream.
#[cfg(lifecycle_only)]
#[path = "scenarios/lifecycle/mod.rs"]
mod lifecycle;

use test_scenarios_rust::cli::run_cli_app;
use test_scenarios_rust::test_context::TestContext;

#[cfg(lifecycle_only)]
use crate::lifecycle::lifecycle_group;
#[cfg(lifecycle_only)]
use test_scenarios_rust::scenario::{ScenarioGroup, ScenarioGroupImpl};
// The default build keeps the existing root scenario registration for the full FIT suite.
#[cfg(not(lifecycle_only))]
use crate::scenarios::root_scenario_group;
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::Level;
use tracing_subscriber::fmt::time::FormatTime;
use tracing_subscriber::FmtSubscriber;

struct NumericUnixTime;

impl FormatTime for NumericUnixTime {
    fn format_time(&self, w: &mut tracing_subscriber::fmt::format::Writer<'_>) -> std::fmt::Result {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default();
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

    tracing::subscriber::set_global_default(subscriber).expect("Setting default subscriber failed!");
}

// In lifecycle-only mode we construct a reduced root group from the same main.rs
// entrypoint instead of introducing a second Rust binary entry source. This keeps
// the folder layout and normal FIT execution unchanged while providing a stable
// workaround until the ScoreDebug issue is fixed in score_persistency.
#[cfg(lifecycle_only)]
fn root_scenario_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new("root", vec![], vec![lifecycle_group()]))
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
