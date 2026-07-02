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

bool failure_detected_from_input(const std::string& input) {
    return input.find("\"failure_detected\": true") != std::string::npos ||
           input.find("\"failure_detected\":true") != std::string::npos;
}

bool daemon_timestamped_logs_from_input(const std::string& input) {
    return input.find("\"daemon_timestamped_logs\": true") != std::string::npos ||
           input.find("\"daemon_timestamped_logs\":true") != std::string::npos;
}

class LoggingCorrelationScenario : public Scenario {
public:
    std::string name() const override {
        return "logging_correlation";
    }

    void run(const std::string& input) const override {
        const bool failure_detected = failure_detected_from_input(input);
        const bool daemon_timestamped_logs = daemon_timestamped_logs_from_input(input);

        kvs_build_helpers::log_info(
            "\"event\":\"process_logging_support\",\"status\":\"enabled\",\"daemon_name\":\"launch_manager_daemon\"",
            "cpp_test_scenarios::scenarios::lifecycle::logging_correlation");

        kvs_build_helpers::log_info(
            std::string("\"event\":\"daemon_log_timestamp\",\"daemon_name\":\"launch_manager_daemon\",\"timestamp_mode\":\"") +
                (daemon_timestamped_logs ? "timestamped" : "untimestamped") + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::logging_correlation");

        if (!failure_detected) {
            kvs_build_helpers::log_info(
                "\"event\":\"failure_not_detected\",\"action\":\"correlation_skipped\"",
                "cpp_test_scenarios::scenarios::lifecycle::logging_correlation");
            return;
        }

        if (daemon_timestamped_logs) {
            kvs_build_helpers::log_info(
                "\"event\":\"failure_diagnostic_correlated\",\"status\":\"correlated\",\"correlation_key\":\"pid:42@ts:1700000000\"",
                "cpp_test_scenarios::scenarios::lifecycle::logging_correlation");
            return;
        }

        kvs_build_helpers::log_info(
            "\"event\":\"failure_diagnostic_correlation_failed\",\"status\":\"uncorrelated\",\"reason\":\"missing_timestamp\"",
            "cpp_test_scenarios::scenarios::lifecycle::logging_correlation");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_logging_correlation_scenario() {
    return std::make_shared<LoggingCorrelationScenario>();
}
