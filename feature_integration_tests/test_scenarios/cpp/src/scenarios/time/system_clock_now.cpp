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

#include "score/time/system_time/src/system_clock.h"

#include <scenario.hpp>

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <string>

namespace {

/// Read the SystemClock via the public Clock API and verify it tracks the host
/// wall clock.
///
/// score_time's SystemClock wraps std::chrono::system_clock, so a reading taken
/// through Clock<system_clock>::Now() must fall within a generous tolerance of a
/// direct std::chrono::system_clock::now() call. This proves the library links
/// its production backend and returns a live reading (not an epoch-zero stub)
/// when integrated into the reference integration build.
class SystemClockNow final : public Scenario {
public:
    /**
     * @brief Return the scenario name used to identify this scenario in the runner.
     * @return Scenario name string.
     */
    std::string name() const final { return "system_clock_now"; }

    /**
     * @brief Execute the system-clock reading scenario.
     *
     * Reads the SystemClock snapshot, compares it against the host system clock
     * within a 60-second tolerance, and logs the reading for Python inspection.
     *
     * @param input Unused; this scenario takes no configuration.
     * @throws std::runtime_error if the reading is non-positive or outside tolerance.
     */
    void run(const std::string& /*input*/) const final {
        const auto snapshot = score::time::SystemClock::GetInstance().Now();
        const std::int64_t reading_ns = snapshot.TimePointNs().count();

        const std::int64_t reference_ns =
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::system_clock::now().time_since_epoch())
                .count();

        // Generous tolerance absorbs scheduling jitter while still catching a
        // broken backend (e.g. an epoch-zero stub or an unlinked clock).
        constexpr std::int64_t tolerance_ns = 60LL * 1000 * 1000 * 1000;
        if (reading_ns <= 0 || std::llabs(reference_ns - reading_ns) > tolerance_ns) {
            throw std::runtime_error(
                "SystemClock::Now() reading is not within tolerance of the host system clock");
        }

        time_log::log_info(
            "\"clock\":\"system\",\"value_ns\":" + std::to_string(reading_ns),
            "cpp_test_scenarios::scenarios::time::system_clock_now");
    }
};

}  // namespace

/**
 * @brief Factory function for the SystemClockNow scenario.
 * @return Shared pointer to the constructed scenario.
 */
Scenario::Ptr make_system_clock_now_scenario() {
    return std::make_shared<SystemClockNow>();
}
