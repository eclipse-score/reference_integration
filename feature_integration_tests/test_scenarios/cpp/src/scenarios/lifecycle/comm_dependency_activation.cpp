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

bool dependency_available_from_input(const std::string& input) {
    return input.find("\"dependency_available\": true") != std::string::npos ||
           input.find("\"dependency_available\":true") != std::string::npos;
}

bool dependency_executable_from_input(const std::string& input) {
    return input.find("\"dependency_executable\": true") != std::string::npos ||
           input.find("\"dependency_executable\":true") != std::string::npos;
}

class CommDependencyActivationScenario : public Scenario {
public:
    std::string name() const override {
        return "comm_dependency_activation";
    }

    void run(const std::string& input) const override {
        const bool dependency_available = dependency_available_from_input(input);
        const bool dependency_executable = dependency_executable_from_input(input);

        kvs_build_helpers::log_info(
            "\"component\":\"launch_manager\",\"state\":\"running\",\"api\":\"dependency_if\"",
            "cpp_test_scenarios::scenarios::lifecycle::comm_dependency_activation");
        kvs_build_helpers::log_info(
            "\"event\":\"dependency_check\",\"component\":\"comm_router\",\"available\":" +
                std::string(dependency_available ? "true" : "false"),
            "cpp_test_scenarios::scenarios::lifecycle::comm_dependency_activation");
        kvs_build_helpers::log_info(
            "\"event\":\"dependency_exec_check\",\"component\":\"comm_router\",\"executable\":" +
                std::string(dependency_executable ? "true" : "false"),
            "cpp_test_scenarios::scenarios::lifecycle::comm_dependency_activation");

        if (dependency_available && dependency_executable) {
            kvs_build_helpers::log_info(
                "\"event\":\"comm_activation\",\"component\":\"comm_router\",\"status\":\"activated\",\"reason\":\"dependency_ready\"",
                "cpp_test_scenarios::scenarios::lifecycle::comm_dependency_activation");
            return;
        }

        const std::string reason = !dependency_available ? "dependency_missing" : "dependency_not_executable";
        kvs_build_helpers::log_info(
            "\"event\":\"comm_activation_blocked\",\"component\":\"comm_router\",\"status\":\"blocked\",\"reason\":\"" +
                reason + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::comm_dependency_activation");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_comm_dependency_activation_scenario() {
    return std::make_shared<CommDependencyActivationScenario>();
}
