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

bool event_order_monotonic_from_input(const std::string& input) {
    return input.find("\"event_order_monotonic\": true") != std::string::npos ||
           input.find("\"event_order_monotonic\":true") != std::string::npos;
}

bool timestamp_aligned_from_input(const std::string& input) {
    return input.find("\"timestamp_aligned\": true") != std::string::npos ||
           input.find("\"timestamp_aligned\":true") != std::string::npos;
}

class TimeSyncScenario : public Scenario {
public:
    std::string name() const override {
        return "time_sync";
    }

    void run(const std::string& input) const override {
        const bool event_order_monotonic = event_order_monotonic_from_input(input);
        const bool timestamp_aligned = timestamp_aligned_from_input(input);

        kvs_build_helpers::log_info(
            "\"event\":\"lifecycle_timestamp_emitted\",\"timestamp_field\":\"system_time\"",
            "cpp_test_scenarios::scenarios::lifecycle::time_sync");
        kvs_build_helpers::log_info(
            "\"event\":\"clock_source_selected\",\"clock_source\":\"monotonic\"",
            "cpp_test_scenarios::scenarios::lifecycle::time_sync");

        if (event_order_monotonic && timestamp_aligned) {
            kvs_build_helpers::log_info(
                "\"event\":\"time_sync_consistent\",\"status\":\"consistent\",\"reference\":\"monotonic_clock\"",
                "cpp_test_scenarios::scenarios::lifecycle::time_sync");
            return;
        }

        const std::string reason = !event_order_monotonic ? "non_monotonic_event_order" : "timestamp_drift";
        kvs_build_helpers::log_info(
            "\"event\":\"time_sync_inconsistent\",\"status\":\"inconsistent\",\"reason\":\"" + reason + "\"",
            "cpp_test_scenarios::scenarios::lifecycle::time_sync");
    }
};

}  // namespace

Scenario::Ptr make_lifecycle_time_sync_scenario() {
    return std::make_shared<TimeSyncScenario>();
}
