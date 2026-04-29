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

#include <scenario.hpp>

#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

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

        // Override all keys with new values
        for (size_t i = 0; i < test_input.keys.size(); ++i) {
            if (!kvs->set_value(test_input.keys[i], test_input.override_values[i])) {
                throw std::runtime_error("Failed to override value");
            }
        }

        // Reset key2 (index 1) using remove_key — reverts to default in memory
        const auto& key_to_reset = test_input.keys[1];
        if (!kvs->remove_key(key_to_reset)) {
            throw std::runtime_error("Failed to remove key");
        }

        // Flush to persist: key1 and key3 with overrides, key2 absent
        if (!kvs->flush()) {
            throw std::runtime_error("Failed to flush KVS");
        }

        // Normalize snapshot file for Python assertion
        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params)) {
            std::cerr << "Warning: Failed to normalize snapshot file" << std::endl;
        }
    }
}

Scenario::Ptr make_reset_to_default_scenario() {
    return std::make_shared<ResetToDefault>();
}
