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

#ifndef INTERNALS_TIME_CLOCK_LOG_H_
#define INTERNALS_TIME_CLOCK_LOG_H_

#include "tracing.hpp"

#include <chrono>
#include <cstdint>
#include <string>
#include <string_view>
#include <utility>

namespace time_log {

/**
 * @brief Return the current UNIX timestamp in microseconds.
 *
 * The FIT LogContainer parses the "timestamp" field as microseconds, so the
 * C++ scenarios emit microseconds to keep log ordering consistent with the
 * Rust tracing JSON shape.
 *
 * @return Microseconds since the UNIX epoch.
 */
inline std::int64_t unix_micros() {
    const auto now = std::chrono::system_clock::now();
    return std::chrono::duration_cast<std::chrono::microseconds>(now.time_since_epoch()).count();
}

/**
 * @brief Emit the clock reading through the C++ scenario tracing API.
 *
 * Structured fields are written as JSON to stdout for the FIT LogContainer.
 *
 * @param clock Clock domain label.
 * @param fields Remaining field-name/value pairs.
 */
template <typename... Fields>
inline void log_info(const std::string_view clock, Fields... fields) {
    TRACING_INFO("cpp_test_scenarios::scenarios::time", std::make_pair(std::string{"clock"}, clock), fields...);
}

}  // namespace time_log

#endif  // INTERNALS_TIME_CLOCK_LOG_H_
