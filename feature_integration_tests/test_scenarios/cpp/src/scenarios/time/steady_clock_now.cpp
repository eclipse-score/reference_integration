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

#include "score/time/steady_time/src/steady_clock.h"

#include <scenario.hpp>

#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>

namespace {

/// Read the SteadyClock twice via the public Clock API and verify monotonicity.
///
/// A steady (monotonic) clock must never move backwards. Two consecutive
/// Clock<steady_clock>::Now() readings must be non-decreasing. This proves the
/// steady clock backend links and behaves monotonically in the reference
/// integration build.
class SteadyClockNow final : public Scenario {
public:
    /**
     * @brief Return the scenario name used to identify this scenario in the runner.
     * @return Scenario name string.
     */
    std::string name() const final { return "steady_clock_now"; }

    /**
     * @brief Execute the steady-clock monotonicity scenario.
     *
     * Takes two consecutive snapshots and verifies the second is not earlier
     * than the first, then logs both readings for Python inspection.
     *
     * @param input Unused; this scenario takes no configuration.
     * @throws std::runtime_error if the second reading precedes the first.
     */
    void run(const std::string& /*input*/) const final {
        const auto clock = score::time::SteadyClock::GetInstance();
        const std::int64_t first_ns = clock.Now().TimePointNs().count();
        const std::int64_t second_ns = clock.Now().TimePointNs().count();

        if (second_ns < first_ns) {
            throw std::runtime_error(
                "SteadyClock::Now() is not monotonic: second reading precedes the first");
        }

        time_log::log_info(
            "\"clock\":\"steady\",\"first_ns\":" + std::to_string(first_ns) +
                ",\"second_ns\":" + std::to_string(second_ns),
            "cpp_test_scenarios::scenarios::time::steady_clock_now");
    }
};

}  // namespace

/**
 * @brief Factory function for the SteadyClockNow scenario.
 * @return Shared pointer to the constructed scenario.
 */
Scenario::Ptr make_steady_clock_now_scenario() {
    return std::make_shared<SteadyClockNow>();
}
