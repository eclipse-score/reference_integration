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
mod multiple_kvs_per_app;

use multiple_kvs_per_app::MultipleKvsPerApp;
use test_scenarios_rust::scenario::{ScenarioGroup, ScenarioGroupImpl};

pub fn persistency_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "persistency",
        vec![Box::new(MultipleKvsPerApp)],
        vec![],
    ))
}
