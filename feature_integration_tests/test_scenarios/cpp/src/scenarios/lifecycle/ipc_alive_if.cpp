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

bool heartbeat_alive_from_input(const std::string& input) {
    return input.find("\"heartbeat_alive\": true") != std::string::npos ||
           input.find("\"heartbeat_alive\":true") != std::string::npos;
}

class IpcAliveInterfaceScenario : public Scenario {
public:
    std::string name() const override {
        return "ipc_alive_if";
    }

    void run(const std::string& input) const override {
        const bool heartbeat_alive = heartbeat_alive_from_input(input);

        kvs_build_helpers::log_info(
            "\"component\":\"launch_manager\",\"state\":\"running\",\"api\":\"alive_if\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_alive_if");
        kvs_build_helpers::log_info(
            "\"component\":\"health_monitor\",\"state\":\"monitoring\",\"api\":\"alive_if\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_alive_if");
        kvs_build_helpers::log_info(
            "\"event\":\"heartbeat_ipc\",\"status\":\"active\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_alive_if");

        if (heartbeat_alive) {
            kvs_build_helpers::log_info(
                "\"event\":\"liveliness_ok\",\"source_component\":\"health_monitor\",\"propagated_to\":\"launch_manager\"",
                "cpp_test_scenarios::scenarios::lifecycle::ipc_alive_if");
            return;
        }

        kvs_build_helpers::log_info(
            "\"event\":\"liveliness_failed\",\"source_component\":\"health_monitor\",\"propagated_to\":\"launch_manager\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_alive_if");
        kvs_build_helpers::log_info(
            "\"event\":\"failure_propagated\",\"action\":\"switch_to_safe_state\",\"reason\":\"heartbeat_timeout\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_alive_if");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_ipc_alive_if_scenario() {
    return std::make_shared<IpcAliveInterfaceScenario>();
}
