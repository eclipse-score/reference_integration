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

class ApplicationInterfaceScenario : public Scenario {
public:
    std::string name() const override {
        return "application_if";
    }

    void run(const std::string& input) const override {
        const bool daemon_enabled = bool_from_input(input, "daemon_enabled");
        const std::string signal_name = string_from_input(input, "signal_name", "SIGUSR1");

        kvs_build_helpers::log_info(
            "\"component\":\"launch_manager\",\"state\":\"running\",\"api\":\"application_if\"",
            "cpp_test_scenarios::scenarios::lifecycle::application_if");
        kvs_build_helpers::log_info(
            "\"component\":\"score_application\",\"state\":\"state_reported\",\"api\":\"lifecycle_if\"",
            "cpp_test_scenarios::scenarios::lifecycle::application_if");

        if (daemon_enabled) {
            kvs_build_helpers::log_info(
                "\"component\":\"control_daemon\",\"state\":\"running\"",
                "cpp_test_scenarios::scenarios::lifecycle::application_if");
            kvs_build_helpers::log_info(
                "\"event\":\"signal_dispatched\",\"condition\":\"daemon_running\",\"signal_name\":\"" +
                    signal_name + "\",\"target_process\":\"score_application\"",
                "cpp_test_scenarios::scenarios::lifecycle::application_if");
            return;
        }

        kvs_build_helpers::log_info(
            "\"event\":\"signal_skipped\",\"condition\":\"daemon_not_running\",\"signal_name\":\"" +
                signal_name + "\",\"target_process\":\"score_application\"",
            "cpp_test_scenarios::scenarios::lifecycle::application_if");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_application_if_scenario() {
    return std::make_shared<ApplicationInterfaceScenario>();
}
