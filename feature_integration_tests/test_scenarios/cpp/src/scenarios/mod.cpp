// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************

#include <scenario.hpp>

#include <vector>

Scenario::Ptr make_multiple_kvs_per_app_scenario();

ScenarioGroup::Ptr persistency_scenario_group() {
    return std::make_shared<ScenarioGroupImpl>(
        "persistency",
        std::vector<Scenario::Ptr>{make_multiple_kvs_per_app_scenario()},
        std::vector<ScenarioGroup::Ptr>{});
}

ScenarioGroup::Ptr root_scenario_group() {
    return std::make_shared<ScenarioGroupImpl>(
        "root",
        std::vector<Scenario::Ptr>{},
        std::vector<ScenarioGroup::Ptr>{persistency_scenario_group()});
}
