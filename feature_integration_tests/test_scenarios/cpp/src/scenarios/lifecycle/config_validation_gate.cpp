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

bool config_schema_valid_from_input(const std::string& input) {
    return input.find("\"config_schema_valid\": true") != std::string::npos ||
           input.find("\"config_schema_valid\":true") != std::string::npos;
}

bool dependencies_consistent_from_input(const std::string& input) {
    return input.find("\"dependencies_consistent\": true") != std::string::npos ||
           input.find("\"dependencies_consistent\":true") != std::string::npos;
}

class ConfigValidationGateScenario : public Scenario {
public:
    std::string name() const override {
        return "config_validation_gate";
    }

    void run(const std::string& input) const override {
        const bool config_schema_valid = config_schema_valid_from_input(input);
        const bool dependencies_consistent = dependencies_consistent_from_input(input);
        const bool valid = config_schema_valid && dependencies_consistent;

        kvs_build_helpers::log_info(
            std::string("\"event\":\"offline_config_validation\",\"schema_valid\":") +
                (config_schema_valid ? "true" : "false") +
                std::string(",\"dependencies_consistent\":") +
                (dependencies_consistent ? "true" : "false") +
                std::string(",\"status\":\"") +
                (valid ? "accepted" : "rejected") + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::config_validation_gate");

        if (valid) {
            kvs_build_helpers::log_info(
                "\"event\":\"lifecycle_config_executable\",\"status\":\"executable\"",
                "cpp_test_scenarios::scenarios::lifecycle::config_validation_gate");
            return;
        }

        const std::string reason = !config_schema_valid ? "invalid_schema" : "inconsistent_dependencies";
        kvs_build_helpers::log_info(
            "\"event\":\"lifecycle_config_rejected\",\"status\":\"rejected\",\"reason\":\"" + reason + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::config_validation_gate");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_config_validation_gate_scenario() {
    return std::make_shared<ConfigValidationGateScenario>();
}
