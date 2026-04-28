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

#include "../../internals/persistency/kvs_instance.h"

#include "tracing.hpp"

#include "score/json/json_parser.h"

#include <scenario.hpp>

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

const std::string kTargetName{"cpp_test_scenarios::scenarios::persistency::default_values_ignored"};

struct TestInput {
    std::string key;
    double override_value;

    static TestInput from_json(const std::string& input);
};

class DefaultValuesIgnored : public Scenario {
public:
    std::string name() const override;
    void run(const std::string& input) const override;
};

TestInput TestInput::from_json(const std::string& input_json) {
    const score::json::JsonParser parser;
    const auto root_any_res = parser.FromBuffer(input_json);
    if (!root_any_res.has_value()) {
        throw std::invalid_argument("Failed to parse scenario input JSON");
    }

    const auto root_object_res = root_any_res.value().As<score::json::Object>();
    if (!root_object_res.has_value()) {
        throw std::invalid_argument("Scenario input root must be an object");
    }

    const auto& root = root_object_res.value().get();
    const auto test_it = root.find("test");
    if (test_it == root.end()) {
        throw std::invalid_argument("Missing test section");
    }

    const auto test_object_res = test_it->second.As<score::json::Object>();
    if (!test_object_res.has_value()) {
        throw std::invalid_argument("test section must be an object");
    }

    const auto& test = test_object_res.value().get();
    TestInput parsed;

    if (const auto it = test.find("key"); it != test.end()) {
        if (const auto val = it->second.As<std::string_view>(); val.has_value()) {
            parsed.key = std::string(val.value());
        }
    }

    if (const auto it = test.find("override_value"); it != test.end()) {
        if (const auto val = it->second.As<double>(); val.has_value()) {
            parsed.override_value = val.value();
        }
    }

    return parsed;
}

}  // anonymous namespace

std::string DefaultValuesIgnored::name() const {
    return "default_values_ignored";
}

void DefaultValuesIgnored::run(const std::string& input) const {
    // Parse parameters
    KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");
    TestInput test_input = TestInput::from_json(input);

    // Verify KvsDefaults::Ignored mode
    TRACING_INFO(kTargetName,
                 std::pair{std::string{"mode"}, "ignored"},
                 std::pair{std::string{"defaults_loaded"}, "false"});

    // Create KVS with Ignored mode
    auto kvs_opt = KvsInstance::create(params);
    if (!kvs_opt) {
        throw std::runtime_error("Failed to create KVS instance");
    }
    auto kvs = *kvs_opt;

    // Attempt to get default value - should fail since defaults are ignored
    auto default_result = kvs->get_value_f64(test_input.key);
    if (default_result.has_value()) {
        throw std::runtime_error("Expected get_value to fail with Ignored mode, but it succeeded");
    }

    // Set explicit value
    if (!kvs->set_value(test_input.key, test_input.override_value)) {
        throw std::runtime_error("Failed to set value");
    }

    // Get the value back
    auto retrieved_opt = kvs->get_value_f64(test_input.key);
    if (!retrieved_opt) {
        throw std::runtime_error("Failed to get explicitly set value");
    }

    TRACING_INFO(kTargetName,
                 std::pair{std::string{"operation"}, "set_and_get"},
                 std::pair{std::string{"key"}, test_input.key},
                 std::pair{std::string{"value"}, *retrieved_opt});

    // Flush to storage
    if (!kvs->flush()) {
        throw std::runtime_error("Failed to flush KVS");
    }

    // Normalize snapshot file
    if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params)) {
        std::cerr << "Warning: Failed to normalize snapshot file" << std::endl;
    }
}

Scenario::Ptr make_default_values_ignored_scenario() {
    return std::make_shared<DefaultValuesIgnored>();
}
