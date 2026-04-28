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

#include <scenario.hpp>

#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

const std::string kTargetName{"cpp_test_scenarios::scenarios::persistency::reset_to_default"};

struct TestInput {
    // Data matches the Python test configuration; hardcoded since it's symmetric.
    const std::vector<std::string> keys{"key1", "key2", "key3"};
    const std::vector<double> override_values{111.0, 222.0, 333.0};
    const std::vector<double> default_values{100.0, 200.0, 300.0};
};

class ResetToDefault : public Scenario {
public:
    std::string name() const override;
    void run(const std::string& input) const override;
};

}  // anonymous namespace

std::string ResetToDefault::name() const {
    return "reset_to_default";
}

void ResetToDefault::run(const std::string& input) const {
    // Parse parameters
    KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");
    const TestInput test_input;

    // Create KVS with Optional mode - defaults should be loaded
    {
        auto kvs_opt = KvsInstance::create(params);
        if (!kvs_opt) {
            throw std::runtime_error("Failed to create KVS instance");
        }
        auto kvs = *kvs_opt;

        // Verify all keys start with default values
        for (size_t i = 0; i < test_input.keys.size(); ++i) {
            auto default_opt = kvs->get_value_f64(test_input.keys[i]);
            if (!default_opt) {
                throw std::runtime_error("Failed to get initial default value");
            }
            if (std::abs(*default_opt - test_input.default_values[i]) > 1e-9) {
                throw std::runtime_error("Initial value mismatch");
            }
        }

        // Override all keys with new values
        for (size_t i = 0; i < test_input.keys.size(); ++i) {
            if (!kvs->set_value(test_input.keys[i], test_input.override_values[i])) {
                throw std::runtime_error("Failed to override value");
            }

            auto is_default = kvs->is_value_default(test_input.keys[i]);
            std::string is_default_str = is_default.has_value() ? (*is_default ? "true" : "false") : "unknown";

            TRACING_INFO(kTargetName,
                         std::pair{std::string{"operation"}, std::string{"override_"} + test_input.keys[i]},
                         std::pair{std::string{"key"}, test_input.keys[i]},
                         std::pair{std::string{"value"}, test_input.override_values[i]},
                         std::pair{std::string{"is_default"}, is_default_str});
        }

        // Reset key2 (index 1) using remove_key
        const auto& key_to_reset = test_input.keys[1];
        if (!kvs->remove_key(key_to_reset)) {
            throw std::runtime_error("Failed to remove key");
        }

        // Check key2 after reset - should be back to default
        auto reset_opt = kvs->get_value_f64(key_to_reset);
        if (!reset_opt) {
            throw std::runtime_error("Failed to get value after reset");
        }

        auto is_default_after = kvs->is_value_default(key_to_reset);
        std::string is_default_str = is_default_after.has_value() ? (*is_default_after ? "true" : "false") : "unknown";

        TRACING_INFO(kTargetName,
                     std::pair{std::string{"operation"}, std::string{"after_reset_"} + key_to_reset},
                     std::pair{std::string{"key"}, key_to_reset},
                     std::pair{std::string{"value"}, *reset_opt},
                     std::pair{std::string{"is_default"}, is_default_str});

        // Verify reset_value matches default within float tolerance.
        // C++ KVS internally uses f32 storage, causing ~1e-5 rounding for f64 values.
        if (std::abs(*reset_opt - test_input.default_values[1]) > 1e-4) {
            throw std::runtime_error("Reset value mismatch");
        }

        // Check other keys are still overridden
        for (size_t i = 0; i < test_input.keys.size(); ++i) {
            if (i == 1) {
                continue;  // Skip key2 which we just reset
            }

            auto current_opt = kvs->get_value_f64(test_input.keys[i]);
            if (!current_opt) {
                throw std::runtime_error("Failed to get value for other key");
            }

            auto is_default = kvs->is_value_default(test_input.keys[i]);
            std::string is_default_str = is_default.has_value() ? (*is_default ? "true" : "false") : "unknown";

            TRACING_INFO(kTargetName,
                         std::pair{std::string{"operation"}, std::string{"check_"} + test_input.keys[i] + "_after_reset"},
                         std::pair{std::string{"key"}, test_input.keys[i]},
                         std::pair{std::string{"value"}, *current_opt},
                         std::pair{std::string{"is_default"}, is_default_str});

            if (std::abs(*current_opt - test_input.override_values[i]) > 1e-4) {
                throw std::runtime_error("Other key was affected by reset");
            }
        }

        // Flush to storage
        if (!kvs->flush()) {
            throw std::runtime_error("Failed to flush KVS");
        }

        // Normalize snapshot file
        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params)) {
            std::cerr << "Warning: Failed to normalize snapshot file" << std::endl;
        }
    }
}

Scenario::Ptr make_reset_to_default_scenario() {
    return std::make_shared<ResetToDefault>();
}
