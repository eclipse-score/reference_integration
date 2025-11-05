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
use crate::internals::runtime_helper::Runtime;
use test_scenarios_rust::scenario::Scenario;
use tracing::info;

pub struct OnlyShutdownSequence;

/// Checks (almost) empty program with only shutdown
impl Scenario for OnlyShutdownSequence {
    fn name(&self) -> &str {
        "only_shutdown"
    }

    fn run(&self, input: &str) -> Result<(), String> {
        let mut rt = Runtime::from_json(input)?.build();

        rt.block_on(async move {
            info!("Program entered engine");
            // TODO: Create a program with only shutdown sequence once it is supported.
            info!("Program execution finished");
        });

        Ok(())
    }
}
