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

#include "score/mw/log/logger.h"

#include <chrono>
#include <cstdint>
#include <string>

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
 * @brief Emit the clock reading through the SCORE logging API.
 *
 * The FIT runner captures C++ scenario output, including the console logger's
 * formatted records. Keep the values in a concise message for inspection.
 *
 * @param message Clock reading details to log.
 */
inline void log_info(const std::string& message) {
    static auto& logger = score::mw::log::CreateLogger("cpp_test_scenarios.time");
    logger.LogInfo() << message;
}

}  // namespace time_log

#endif  // INTERNALS_TIME_CLOCK_LOG_H_
