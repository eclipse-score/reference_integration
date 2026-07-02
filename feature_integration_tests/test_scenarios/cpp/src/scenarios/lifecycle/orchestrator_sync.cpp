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

class OrchestratorSyncScenario : public Scenario {
public:
    std::string name() const override {
        return "orchestrator_sync";
    }

    void run(const std::string& input) const override {
        const bool run_target_switch_success = bool_from_input(input, "run_target_switch_success");
        const bool orchestrator_state_synced = bool_from_input(input, "orchestrator_state_synced");
        const std::string from_target = string_from_input(input, "from_target", "Startup");
        const std::string to_target = string_from_input(input, "to_target", "Nominal");

        kvs_build_helpers::log_info(
            "\"event\":\"run_target_support\",\"status\":\"enabled\"",
            "cpp_test_scenarios::scenarios::lifecycle::orchestrator_sync");

        if (run_target_switch_success) {
            kvs_build_helpers::log_info(
                "\"event\":\"run_target_switched\",\"from_target\":\"" + from_target +
                    "\",\"to_target\":\"" + to_target + "\"",
                "cpp_test_scenarios::scenarios::lifecycle::orchestrator_sync");
        } else {
            kvs_build_helpers::log_info(
                "\"event\":\"run_target_switch_failed\",\"reason\":\"switch_rejected\"",
                "cpp_test_scenarios::scenarios::lifecycle::orchestrator_sync");
        }

        if (run_target_switch_success && orchestrator_state_synced) {
            kvs_build_helpers::log_info(
                "\"event\":\"orchestrator_state_sync_consistent\",\"status\":\"consistent\"",
                "cpp_test_scenarios::scenarios::lifecycle::orchestrator_sync");
            return;
        }

        const std::string reason = !run_target_switch_success ? "run_target_switch_failed" : "orchestrator_state_desync";
        kvs_build_helpers::log_info(
            "\"event\":\"orchestrator_state_sync_inconsistent\",\"status\":\"inconsistent\",\"reason\":\"" + reason + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::orchestrator_sync");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_orchestrator_sync_scenario() {
    return std::make_shared<OrchestratorSyncScenario>();
}
