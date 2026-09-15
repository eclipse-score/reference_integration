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

#include "score/time/high_res_steady_time/src/high_res_steady_clock.h"

#include <scenario.hpp>

#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string>

namespace {

/// Read the HighResSteadyClock twice via the public Clock API and verify it is
/// live and monotonic.
///
/// The high-resolution steady clock must return a non-zero reading and never
/// move backwards. This proves the high-resolution backend (system-clock based
/// on Linux) links and behaves monotonically in the reference integration build.
class HighResSteadyClockNow final : public Scenario {
public:
    /**
     * @brief Return the scenario name used to identify this scenario in the runner.
     * @return Scenario name string.
     */
    std::string name() const final { return "high_res_steady_clock_now"; }

    /**
     * @brief Execute the high-resolution steady-clock scenario.
     *
     * Takes two consecutive snapshots and verifies the first is non-zero and the
     * second is not earlier than the first, then logs both readings for Python
     * inspection.
     *
     * @param input Unused; this scenario takes no configuration.
     * @throws std::runtime_error if the reading is zero or non-monotonic.
     */
    void run(const std::string& /*input*/) const final {
        const auto clock = score::time::HighResSteadyClock::GetInstance();
        const std::int64_t first_ns = clock.Now().TimePointNs().count();
        const std::int64_t second_ns = clock.Now().TimePointNs().count();

        if (first_ns == 0) {
            throw std::runtime_error("HighResSteadyClock::Now() returned a zero reading");
        }
        if (second_ns < first_ns) {
            throw std::runtime_error(
                "HighResSteadyClock::Now() is not monotonic: second reading precedes the first");
        }

        time_log::log_info(
            "\"clock\":\"high_res_steady\",\"first_ns\":" + std::to_string(first_ns) +
                ",\"second_ns\":" + std::to_string(second_ns),
            "cpp_test_scenarios::scenarios::time::high_res_steady_clock_now");
    }
};

}  // namespace

/**
 * @brief Factory function for the HighResSteadyClockNow scenario.
 * @return Shared pointer to the constructed scenario.
 */
Scenario::Ptr make_high_res_steady_clock_now_scenario() {
    return std::make_shared<HighResSteadyClockNow>();
}
