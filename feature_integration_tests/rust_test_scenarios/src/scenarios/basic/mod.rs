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
use test_scenarios_rust::scenario::{ScenarioGroup, ScenarioGroupImpl};

mod orchestration_with_persistency;

pub fn basic_scenario_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "basic",
        vec![Box::new(
            orchestration_with_persistency::OrchestrationWithPersistency,
        )],
        vec![],
    ))
}
