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

#include "../../internals/time/clock_log.h"

#include "score/json/json_parser.h"
#include "score/time/steady_time/src/steady_clock.h"

#include <scenario.hpp>

#include <chrono>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {

/// Read the SteadyClock repeatedly, sleep a known duration, then read once more.
///
/// A steady (monotonic) clock must never move backwards. This scenario takes a
/// series of readings, asserts the sequence is non-decreasing, sleeps for a
/// known duration, takes one final reading and asserts the clock has progressed
/// beyond the last pre-sleep reading. This exercises the monotonicity and
/// progression guarantees of FR-14 (Monotonic Clock API), including the
/// TC-FR14-001 "call Now() repeatedly, assert strictly increasing" case.
class SteadyClockProgression final : public Scenario {
public:
    /**
     * @brief Return the scenario name used to identify this scenario in the runner.
     * @return Scenario name string.
     */
    std::string name() const final { return "steady_clock_progression"; }

    /**
     * @brief Execute the steady-clock progression scenario.
     *
     * Takes ``tick_count`` consecutive readings and verifies the sequence is
     * non-decreasing, sleeps for ``sleep_ms`` milliseconds, then takes a final
     * reading and verifies it is not earlier than the last pre-sleep reading.
     * Both values are read from the scenario input, defaulting to 5 ticks and a
     * 100 ms sleep when absent.
     *
     * @param input JSON object with optional ``tick_count`` and ``sleep_ms`` fields.
     * @throws std::invalid_argument if the configured values are out of range.
     * @throws std::runtime_error if any reading violates monotonicity.
     */
    void run(const std::string& input) const final {
        // Defaults; overridable via the test config.
        std::int64_t tick_count = 5;
        std::int64_t sleep_ms = 100;

        const score::json::JsonParser parser;
        if (const auto root_any_res = parser.FromBuffer(input); root_any_res.has_value()) {
            if (const auto root_obj_res = root_any_res.value().As<score::json::Object>();
                root_obj_res.has_value()) {
                const auto& root = root_obj_res.value().get();
                if (const auto it = root.find("tick_count"); it != root.end()) {
                    if (const auto v = it->second.As<std::int64_t>(); v.has_value()) {
                        tick_count = v.value();
                    }
                }
                if (const auto it = root.find("sleep_ms"); it != root.end()) {
                    if (const auto v = it->second.As<std::int64_t>(); v.has_value()) {
                        sleep_ms = v.value();
                    }
                }
            }
        }

        if (tick_count < 2) {
            throw std::invalid_argument("tick_count must be at least 2");
        }
        if (sleep_ms <= 0) {
            throw std::invalid_argument("sleep_ms must be positive");
        }

        const auto clock = score::time::SteadyClock::GetInstance();

        std::vector<std::int64_t> ticks;
        ticks.reserve(static_cast<std::size_t>(tick_count));
        for (std::int64_t i = 0; i < tick_count; ++i) {
            ticks.push_back(clock.Now().TimePointNs().count());
        }

        for (std::size_t i = 1; i < ticks.size(); ++i) {
            if (ticks[i] < ticks[i - 1]) {
                throw std::runtime_error(
                    "SteadyClock::Now() is not monotonic: reading " + std::to_string(i) +
                    " precedes the previous one");
            }
        }

        const std::int64_t first_ns = ticks.front();
        const std::int64_t last_ns = ticks.back();
        std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));
        const std::int64_t final_ns = clock.Now().TimePointNs().count();

        if (final_ns < last_ns) {
            throw std::runtime_error(
                "SteadyClock::Now() did not progress after sleep: final reading precedes the last");
        }

        time_log::log_info(
            "\"clock\":\"steady\",\"tick_count\":" + std::to_string(tick_count) +
                ",\"first_ns\":" + std::to_string(first_ns) +
                ",\"last_ns\":" + std::to_string(last_ns) +
                ",\"final_ns\":" + std::to_string(final_ns) +
                ",\"sleep_ms\":" + std::to_string(sleep_ms),
            "cpp_test_scenarios::scenarios::time::steady_clock_progression");
    }
};

}  // namespace

/**
 * @brief Factory function for the SteadyClockProgression scenario.
 * @return Shared pointer to the constructed scenario.
 */
Scenario::Ptr make_steady_clock_progression_scenario() {
    return std::make_shared<SteadyClockProgression>();
}
