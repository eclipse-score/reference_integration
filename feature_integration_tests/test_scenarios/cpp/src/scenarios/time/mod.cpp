/********************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

#include <scenario.hpp>

#include <vector>

Scenario::Ptr make_system_clock_now_scenario();
Scenario::Ptr make_steady_clock_now_scenario();
Scenario::Ptr make_high_res_steady_clock_now_scenario();

ScenarioGroup::Ptr time_scenario_group() {
    return std::make_shared<ScenarioGroupImpl>(
        "time",
        std::vector<Scenario::Ptr>{
            make_system_clock_now_scenario(),
            make_steady_clock_now_scenario(),
            make_high_res_steady_clock_now_scenario(),
        },
        std::vector<ScenarioGroup::Ptr>{});
}
