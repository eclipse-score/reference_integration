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

#include <chrono>
#include <cstdint>
#include <iostream>
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
 * @brief Emit a structured JSON INFO log line to stdout.
 *
 * Matches the Rust tracing JSON format expected by the FIT LogContainer so
 * that Python test assertions can use find_log() uniformly for both Rust and
 * C++ scenarios.
 *
 * Example output:
 * @code
 * {"timestamp":"1700000000000000","level":"INFO","fields":{"clock":"system","value_ns":1700000000000000000},
 *  "target":"cpp_test_scenarios::scenarios::time::system_clock_now","threadId":"ThreadId(1)"}
 * @endcode
 *
 * @param fields  JSON fragment for the "fields" object, e.g. @c "\"clock\":\"system\",\"value_ns\":1"
 * @param target  Module target string embedded in the log line.
 */
inline void log_info(const std::string& fields, const std::string& target) {
    std::cout << "{\"timestamp\":\"" << unix_micros()
              << "\",\"level\":\"INFO\",\"fields\":{" << fields
              << "},\"target\":\"" << target
              << "\",\"threadId\":\"ThreadId(1)\"}\n";
}

}  // namespace time_log

#endif  // INTERNALS_TIME_CLOCK_LOG_H_
