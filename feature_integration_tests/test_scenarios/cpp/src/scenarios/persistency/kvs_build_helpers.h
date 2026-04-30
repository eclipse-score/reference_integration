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

#ifndef FEATURE_INTEGRATION_TESTS_TEST_SCENARIOS_CPP_SRC_SCENARIOS_PERSISTENCY_KVS_BUILD_HELPERS_H_
#define FEATURE_INTEGRATION_TESTS_TEST_SCENARIOS_CPP_SRC_SCENARIOS_PERSISTENCY_KVS_BUILD_HELPERS_H_

#include "../../internals/persistency/kvs_parameters.h"

#include <kvs.hpp>
#include <kvsbuilder.hpp>

#include <optional>
#include <stdexcept>
#include <string>

namespace kvs_build_helpers {

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

#endif  // FEATURE_INTEGRATION_TESTS_TEST_SCENARIOS_CPP_SRC_SCENARIOS_PERSISTENCY_KVS_BUILD_HELPERS_H_
