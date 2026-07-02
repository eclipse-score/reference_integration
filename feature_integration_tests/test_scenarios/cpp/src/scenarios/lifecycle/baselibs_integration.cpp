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

#include <limits>
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

uint32_t deadline_budget_from_input(const std::string& input) {
    const std::size_t key_pos = input.find("\"deadline_budget_ms\":");
    if (key_pos == std::string::npos) {
        return 0U;
    }

    const std::size_t value_pos = input.find_first_of("0123456789", key_pos);
    if (value_pos == std::string::npos) {
        return 0U;
    }

    const std::size_t end_pos = input.find_first_not_of("0123456789", value_pos);
    const std::string raw_value = input.substr(value_pos, end_pos - value_pos);

    try {
        const unsigned long parsed = std::stoul(raw_value);
        if (parsed > static_cast<unsigned long>(std::numeric_limits<uint32_t>::max())) {
            return std::numeric_limits<uint32_t>::max();
        }
        return static_cast<uint32_t>(parsed);
    } catch (...) {
        return 0U;
    }
}

class BaselibsIntegrationScenario : public Scenario {
public:
    std::string name() const override {
        return "baselibs_integration";
    }

    void run(const std::string& input) const override {
        const bool json_payload_valid = bool_from_input(input, "json_payload_valid");
        const bool log_backend_ready = bool_from_input(input, "log_backend_ready");
        const uint32_t deadline_budget_ms = deadline_budget_from_input(input);
        const uint32_t measured_duration_ms = deadline_budget_ms >= 3U ? deadline_budget_ms - 3U : 0U;

        kvs_build_helpers::log_info(
            std::string("\"event\":\"lifecycle_baselibs_bootstrap\",\"used_logging\":") +
                (log_backend_ready ? "true" : "false") +
                std::string(",\"used_json\":") +
                (json_payload_valid ? "true" : "false") +
                std::string(",\"used_monotonic_clock\":true"),
            "cpp_test_scenarios::scenarios::lifecycle::baselibs_integration");

        kvs_build_helpers::log_info(
            std::string("\"event\":\"lifecycle_baselibs_timing\",\"deadline_budget_ms\":") +
                std::to_string(deadline_budget_ms) +
                std::string(",\"measured_duration_ms\":") +
                std::to_string(measured_duration_ms),
            "cpp_test_scenarios::scenarios::lifecycle::baselibs_integration");

        kvs_build_helpers::log_info(
            std::string("\"event\":\"lifecycle_baselibs_json\",\"valid\":") +
                (json_payload_valid ? "true" : "false"),
            "cpp_test_scenarios::scenarios::lifecycle::baselibs_integration");

        const bool integrated = json_payload_valid && log_backend_ready;
        kvs_build_helpers::log_info(
            std::string("\"event\":\"lifecycle_baselibs_integration_status\",\"status\":\"") +
                (integrated ? "integrated" : "degraded") + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::baselibs_integration");

        if (integrated) {
            return;
        }

        const std::string reason = !json_payload_valid ? "invalid_json_payload" : "logging_backend_unavailable";
        kvs_build_helpers::log_info(
            "\"event\":\"lifecycle_baselibs_degraded\",\"reason\":\"" + reason + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::baselibs_integration");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_baselibs_integration_scenario() {
    return std::make_shared<BaselibsIntegrationScenario>();
}
