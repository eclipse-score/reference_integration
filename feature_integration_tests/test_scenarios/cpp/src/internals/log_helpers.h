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

#ifndef INTERNALS_LOG_HELPERS_H_
#define INTERNALS_LOG_HELPERS_H_

#include <chrono>
#include <iomanip>
#include <iostream>
#include <locale>
#include <sstream>
#include <string>

namespace log_helpers {

/**
 * @brief Return the current UNIX timestamp as a decimal string (seconds).
 *
 * Used to populate the "timestamp" field in structured JSON log lines so that
 * the C++ output matches the Rust tracing JSON shape expected by the FIT log
 * filters.
 *
 * @return String containing the number of seconds since the UNIX epoch.
 */
inline std::string unix_seconds_string() {
    const auto now = std::chrono::system_clock::now();
    const auto secs =
        std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();
    return std::to_string(secs);
}

/**
 * @brief Escape a string for embedding as a JSON string value.
 *
 * Escapes '"', '\\', and control characters. Without this, interpolating a raw
 * value (e.g. a filesystem path containing '"' or '\\') straight into a JSON
 * string produces malformed JSON that downstream JSON-based log parsing (e.g.
 * Python's FIT LogContainer) cannot read back.
 *
 * @param value Raw string to escape.
 * @return JSON-escaped string, without surrounding quotes.
 */
inline std::string json_escape(const std::string& value) {
    std::string escaped;
    escaped.reserve(value.size());
    for (const char c : value) {
        switch (c) {
            case '"':
                escaped += "\\\"";
                break;
            case '\\':
                escaped += "\\\\";
                break;
            case '\n':
                escaped += "\\n";
                break;
            case '\r':
                escaped += "\\r";
                break;
            case '\t':
                escaped += "\\t";
                break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) {
                    std::ostringstream oss;
                    oss << "\\u" << std::hex << std::setfill('0') << std::setw(4)
                        << static_cast<int>(static_cast<unsigned char>(c));
                    escaped += oss.str();
                } else {
                    escaped += c;
                }
        }
    }
    return escaped;
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
 * {"timestamp":"1234567890","level":"INFO","fields":{"key":"my_key","value":42.0},
 *  "target":"cpp_test_scenarios::scenarios::persistency::my_module","threadId":"ThreadId(1)"}
 * @endcode
 *
 * @param fields  JSON fragment for the "fields" object, e.g. @c "\"key\":\"x\",\"value\":1.0"
 *                Caller is responsible for escaping any string values embedded here.
 * @param target  Module target string embedded in the log line.
 */
inline void log_info(const std::string& fields, const std::string& target) {
    std::cout << "{\"timestamp\":\"" << unix_seconds_string()
              << "\",\"level\":\"INFO\",\"fields\":{" << fields
              << "},\"target\":\"" << json_escape(target)
              << "\",\"threadId\":\"ThreadId(1)\"}\n";
}

/**
 * @brief Format a double value to match Python's str(float) representation.
 *
 * For whole-number values (e.g. 42.0, 200.0) this appends ".0" so that the
 * resulting string matches what Python's f-string interpolation produces.
 * Non-integer values (e.g. 3.14) are printed as-is by the default stream.
 *
 * @param v Double value to format.
 * @return String representation matching Python float str().
 */
inline std::string format_double_python(double v) {
    std::ostringstream oss;
    oss.imbue(std::locale::classic());  // Ensure '.' decimal separator regardless of process locale.
    oss << v;
    std::string s = oss.str();
    if (s.find('.') == std::string::npos && s.find('e') == std::string::npos &&
        s.find('E') == std::string::npos) {
        s += ".0";
    }
    return s;
}

}  // namespace log_helpers

#endif  // INTERNALS_LOG_HELPERS_H_
