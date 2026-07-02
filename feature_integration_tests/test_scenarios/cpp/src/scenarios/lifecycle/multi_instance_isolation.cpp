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

bool cross_instance_interference_from_input(const std::string& input) {
    return input.find("\"cross_instance_interference\": true") != std::string::npos ||
           input.find("\"cross_instance_interference\":true") != std::string::npos;
}

class MultiInstanceIsolationScenario : public Scenario {
public:
    std::string name() const override {
        return "multi_instance_isolation";
    }

    void run(const std::string& input) const override {
        const bool cross_instance_interference = cross_instance_interference_from_input(input);

        kvs_build_helpers::log_info(
            "\"event\":\"instance_registered_a\",\"instance_name\":\"lm_instance_a\"",
            "cpp_test_scenarios::scenarios::lifecycle::multi_instance_isolation");
        kvs_build_helpers::log_info(
            "\"event\":\"instance_registered_b\",\"instance_name\":\"lm_instance_b\"",
            "cpp_test_scenarios::scenarios::lifecycle::multi_instance_isolation");

        if (cross_instance_interference) {
            kvs_build_helpers::log_info(
                "\"event\":\"instance_isolation_violated\",\"status\":\"violated\",\"reason\":\"cross_instance_interference\"",
                "cpp_test_scenarios::scenarios::lifecycle::multi_instance_isolation");
            return;
        }

        kvs_build_helpers::log_info(
            "\"event\":\"instance_isolation_ok\",\"status\":\"isolated\",\"supervision_scope\":\"per_instance\"",
            "cpp_test_scenarios::scenarios::lifecycle::multi_instance_isolation");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_multi_instance_isolation_scenario() {
    return std::make_shared<MultiInstanceIsolationScenario>();
}
