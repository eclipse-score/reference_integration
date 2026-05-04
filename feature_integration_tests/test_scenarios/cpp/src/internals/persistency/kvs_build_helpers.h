// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************

#ifndef INTERNALS_PERSISTENCY_KVS_BUILD_HELPERS_H_
#define INTERNALS_PERSISTENCY_KVS_BUILD_HELPERS_H_

#include "kvs_parameters.h"

#include <kvs.hpp>
#include <kvsbuilder.hpp>

#include <chrono>
#include <iostream>
#include <locale>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>

namespace kvs_build_helpers {

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
 * @param target  Module target string embedded in the log line.
 */
inline void log_info(const std::string& fields, const std::string& target) {
    std::cout << "{\"timestamp\":\"" << unix_seconds_string()
              << "\",\"level\":\"INFO\",\"fields\":{" << fields
              << "},\"target\":\"" << target
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

/**
 * @brief Convert an optional KvsDefaults mode to the boolean flag expected by KvsBuilder.
 *
 * Returns true if the mode is Required, false if Optional or Ignored, or
 * std::nullopt if no mode was provided (omit the flag from the builder call).
 *
 * @param mode Optional KvsDefaults value to convert.
 * @return Converted boolean flag or nullopt.
 */
inline std::optional<bool> to_need_flag(const std::optional<KvsDefaults>& mode) {
    if (!mode.has_value()) {
        return std::nullopt;
    }
    return *mode == KvsDefaults::Required;
}

/**
 * @brief Convert an optional KvsLoad mode to the boolean flag expected by KvsBuilder.
 *
 * Returns true if the mode is Required, false if Optional or Ignored, or
 * std::nullopt if no mode was provided (omit the flag from the builder call).
 *
 * @param mode Optional KvsLoad value to convert.
 * @return Converted boolean flag or nullopt.
 */
inline std::optional<bool> to_need_flag(const std::optional<KvsLoad>& mode) {
    if (!mode.has_value()) {
        return std::nullopt;
    }
    return *mode == KvsLoad::Required;
}

/**
 * @brief Build a Kvs instance from KvsParameters, applying all optional fields.
 *
 * Applies instance_id, defaults flag, kvs_load flag, and working directory from
 * the provided KvsParameters to a KvsBuilder and returns the constructed Kvs.
 *
 * @param params Parsed KVS parameters from the test input JSON.
 * @return Constructed Kvs instance.
 * @throws std::runtime_error if the build fails.
 */
inline score::mw::per::kvs::Kvs create_kvs(const KvsParameters& params) {
    score::mw::per::kvs::KvsBuilder builder{
        score::mw::per::kvs::InstanceId{params.instance_id.value}};

    if (const auto defaults = to_need_flag(params.defaults)) {
        builder = builder.need_defaults_flag(*defaults);
    }
    if (const auto kvs_load = to_need_flag(params.kvs_load)) {
        builder = builder.need_kvs_flag(*kvs_load);
    }
    if (params.dir.has_value()) {
        builder = builder.dir(std::string(*params.dir));
    }

    auto build_result = builder.build();
    if (!build_result) {
        throw std::runtime_error(std::string(build_result.error().Message()));
    }

    return std::move(build_result.value());
}

}  // namespace kvs_build_helpers

#endif  // INTERNALS_PERSISTENCY_KVS_BUILD_HELPERS_H_
