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

bool control_request_valid_from_input(const std::string& input) {
    return input.find("\"control_request_valid\": true") != std::string::npos ||
           input.find("\"control_request_valid\":true") != std::string::npos;
}

bool query_target_reachable_from_input(const std::string& input) {
    return input.find("\"query_target_reachable\": true") != std::string::npos ||
           input.find("\"query_target_reachable\":true") != std::string::npos;
}

class IpcControlInterfaceScenario : public Scenario {
public:
    std::string name() const override {
        return "ipc_controlif";
    }

    void run(const std::string& input) const override {
        const bool control_request_valid = control_request_valid_from_input(input);
        const bool query_target_reachable = query_target_reachable_from_input(input);

        kvs_build_helpers::log_info(
            "\"event\":\"controlif_ready\",\"status\":\"active\",\"control_target\":\"comm_control_router\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_controlif");

        if (control_request_valid) {
            kvs_build_helpers::log_info(
                "\"event\":\"control_route\",\"status\":\"routed\",\"reason\":\"valid_request\"",
                "cpp_test_scenarios::scenarios::lifecycle::ipc_controlif");
        } else {
            kvs_build_helpers::log_info(
                "\"event\":\"control_route_rejected\",\"status\":\"rejected\",\"reason\":\"invalid_request\"",
                "cpp_test_scenarios::scenarios::lifecycle::ipc_controlif");
        }

        if (query_target_reachable) {
            kvs_build_helpers::log_info(
                "\"event\":\"query_route\",\"status\":\"routed\",\"reason\":\"target_reachable\"",
                "cpp_test_scenarios::scenarios::lifecycle::ipc_controlif");
            return;
        }

        kvs_build_helpers::log_info(
            "\"event\":\"query_route_failed\",\"status\":\"failed\",\"reason\":\"target_unreachable\"",
            "cpp_test_scenarios::scenarios::lifecycle::ipc_controlif");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_ipc_controlif_scenario() {
    return std::make_shared<IpcControlInterfaceScenario>();
}
