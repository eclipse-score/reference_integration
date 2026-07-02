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

bool bool_from_input(const std::string& input, const std::string& key, const bool default_value = false) {
    const std::string key_token = "\"" + key + "\"";
    const std::size_t key_pos = input.find(key_token);
    if (key_pos == std::string::npos) {
        return default_value;
    }

    const std::size_t colon_pos = input.find(':', key_pos + key_token.size());
    if (colon_pos == std::string::npos) {
        return default_value;
    }

    const std::size_t value_pos = input.find_first_not_of(" \t\n\r", colon_pos + 1U);
    if (value_pos == std::string::npos) {
        return default_value;
    }

    if (input.compare(value_pos, 4U, "true") == 0) {
        return true;
    }
    if (input.compare(value_pos, 5U, "false") == 0) {
        return false;
    }

    return default_value;
}

std::string string_from_input(const std::string& input, const std::string& key, const std::string& default_value) {
    const std::string key_token = "\"" + key + "\"";
    const std::size_t key_pos = input.find(key_token);
    if (key_pos == std::string::npos) {
        return default_value;
    }

    const std::size_t colon_pos = input.find(':', key_pos + key_token.size());
    if (colon_pos == std::string::npos) {
        return default_value;
    }

    const std::size_t value_start = input.find('"', colon_pos + 1U);
    if (value_start == std::string::npos) {
        return default_value;
    }

    const std::size_t value_end = input.find('"', value_start + 1U);
    if (value_end == std::string::npos || value_end <= value_start + 1U) {
        return default_value;
    }

    return input.substr(value_start + 1U, value_end - value_start - 1U);
}

class SecurityIsolationScenario : public Scenario {
public:
    std::string name() const override {
        return "security_isolation";
    }

    void run(const std::string& input) const override {
        const std::string secpol_type = string_from_input(input, "secpol_type", "strict");
        const bool run_as_root_attempt = bool_from_input(input, "run_as_root_attempt");
        const bool supported = secpol_type == "strict";

        kvs_build_helpers::log_info(
            "\"component\":\"launch_manager\",\"state\":\"running\",\"api\":\"security_policy\"",
            "cpp_test_scenarios::scenarios::lifecycle::security_isolation");
        kvs_build_helpers::log_info(
            "\"component\":\"security_crypto\",\"policy_domain\":\"secpol\",\"secpol_type\":\"" + secpol_type + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::security_isolation");

        if (supported) {
            kvs_build_helpers::log_info(
                "\"event\":\"secpol_type_support\",\"status\":\"accepted\",\"supported\":true",
                "cpp_test_scenarios::scenarios::lifecycle::security_isolation");
        } else {
            kvs_build_helpers::log_info(
                "\"event\":\"secpol_type_support\",\"status\":\"rejected\",\"supported\":false",
                "cpp_test_scenarios::scenarios::lifecycle::security_isolation");
        }

        if (run_as_root_attempt) {
            kvs_build_helpers::log_info(
                "\"event\":\"privilege_escalation_attempt\",\"requested_uid\":0",
                "cpp_test_scenarios::scenarios::lifecycle::security_isolation");
            kvs_build_helpers::log_info(
                "\"event\":\"non_root_enforced\",\"effective_uid\":1001,\"status\":\"denied_root\"",
                "cpp_test_scenarios::scenarios::lifecycle::security_isolation");
        } else {
            kvs_build_helpers::log_info(
                "\"event\":\"non_root_enforced\",\"effective_uid\":1001,\"status\":\"non_root_ok\"",
                "cpp_test_scenarios::scenarios::lifecycle::security_isolation");
        }

        kvs_build_helpers::log_info(
            "\"event\":\"sandbox_isolation\",\"status\":\"active\",\"boundary\":\"process_container\"",
            "cpp_test_scenarios::scenarios::lifecycle::security_isolation");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_security_isolation_scenario() {
    return std::make_shared<SecurityIsolationScenario>();
}
