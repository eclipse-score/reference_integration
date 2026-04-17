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

#include "../../framework/scenario_framework.h"

#include <memory>

std::shared_ptr<Scenario> make_multiple_kvs_per_app_scenario();

std::shared_ptr<ScenarioGroup> persistency_scenario_group() {
    auto group = std::make_shared<ScenarioGroup>("persistency");
    group->add_scenario("multiple_kvs_per_app", make_multiple_kvs_per_app_scenario());
    return group;
}
