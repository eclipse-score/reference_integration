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

#include "../../internals/persistency/kvs_build_helpers.h"

#include <scenario.hpp>

#include <string>

namespace {

bool checkpoint_on_time_from_input(const std::string& input) {
    return input.find("\"checkpoint_on_time\": true") != std::string::npos ||
           input.find("\"checkpoint_on_time\":true") != std::string::npos;
}

class IpcDeadlineMonitorInterfaceScenario : public Scenario {
public:
    std::string name() const override {
        return "ipc_deadline_monitor_if";
    }

    void run(const std::string& input) const override {
        const bool checkpoint_on_time = checkpoint_on_time_from_input(input);

        kvs_build_helpers::log_info(
            "\"event\":\"deadline_monitor_if_ready\",\"status\":\"active\",\"monitor_name\":\"deadline_monitor\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_deadline_monitor_if");

        kvs_build_helpers::log_info(
            "\"event\":\"checkpoint_ipc\",\"checkpoint_id\":\"cp_01\",\"source_component\":\"health_monitor\",\"target_component\":\"launch_manager\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_deadline_monitor_if");

        if (checkpoint_on_time) {
            kvs_build_helpers::log_info(
                "\"event\":\"deadline_checkpoint_accepted\",\"status\":\"accepted\",\"reason\":\"within_deadline\"",
                "cpp_test_scenarios::scenarios::lifecycle::ipc_deadline_monitor_if");
            return;
        }

        kvs_build_helpers::log_info(
            "\"event\":\"deadline_timeout\",\"status\":\"timeout\",\"reason\":\"checkpoint_missed\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_deadline_monitor_if");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_ipc_deadline_monitor_if_scenario() {
    return std::make_shared<IpcDeadlineMonitorInterfaceScenario>();
}
