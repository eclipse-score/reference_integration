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

#include "score/json/json_parser.h"

#include <scenario.hpp>

#include <chrono>
#include <iostream>
#include <stdexcept>

struct TestInput {
    std::string key;
    double value_1;
    double value_2;

    static TestInput from_json(const std::string& input);
};

class MultipleKvsPerApp : public Scenario {
public:
    std::string name() const override;
    void run(const std::string& input) const override;
};

std::string unix_seconds_string() {
    const auto now = std::chrono::system_clock::now();
    const auto secs = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();
    return std::to_string(secs);
}

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
    const auto key_it = test.find("key");
    const auto value_1_it = test.find("value_1");
    const auto value_2_it = test.find("value_2");
    if (key_it == test.end() || value_1_it == test.end() || value_2_it == test.end()) {
        throw std::invalid_argument("Invalid test section format");
    }

    const auto key_res = key_it->second.As<std::string_view>();
    const auto value_1_res = value_1_it->second.As<double>();
    const auto value_2_res = value_2_it->second.As<double>();
    if (!key_res.has_value() || !value_1_res.has_value() || !value_2_res.has_value()) {
        throw std::invalid_argument("Invalid test section format");
    }

    TestInput parsed;
    parsed.key = std::string(key_res.value());
    parsed.value_1 = value_1_res.value();
    parsed.value_2 = value_2_res.value();
    return parsed;
}

std::string MultipleKvsPerApp::name() const {
    return "multiple_kvs_per_app";
}

void MultipleKvsPerApp::run(const std::string& input) const {
    // Parse parameters
    KvsParameters params1 = KvsParameters::from_json_section(input, "kvs_parameters_1");
    KvsParameters params2 = KvsParameters::from_json_section(input, "kvs_parameters_2");
    TestInput test_input = TestInput::from_json(input);

    // ============================================================
    // PHASE 1: Create instances, set values, flush to disk
    // ============================================================
    {
        // Create first KVS instance
        auto kvs1_opt = KvsInstance::create(params1);
        if (!kvs1_opt) {
            throw std::runtime_error("Failed to create KVS instance 1");
        }
        auto kvs1 = *kvs1_opt;

        // Create second KVS instance
        auto kvs2_opt = KvsInstance::create(params2);
        if (!kvs2_opt) {
            throw std::runtime_error("Failed to create KVS instance 2");
        }
        auto kvs2 = *kvs2_opt;

        // Set values to both instances
        if (!kvs1->set_value(test_input.key, test_input.value_1)) {
            throw std::runtime_error("Failed to set kvs1 value");
        }

        if (!kvs2->set_value(test_input.key, test_input.value_2)) {
            throw std::runtime_error("Failed to set kvs2 value");
        }

        // Flush both instances to disk
        if (!kvs1->flush()) {
            throw std::runtime_error("Failed to flush kvs1");
        }

        if (!kvs2->flush()) {
            throw std::runtime_error("Failed to flush kvs2");
        }

        // Instances go out of scope here
    }

    // ============================================================
    // PHASE 2: Reopen instances and verify persistence
    // ============================================================
    {
        // Reopen first KVS instance (from persisted file)
        auto kvs1_opt = KvsInstance::create(params1);
        if (!kvs1_opt) {
            throw std::runtime_error("Failed to reopen KVS instance 1");
        }
        auto kvs1 = *kvs1_opt;

        // Reopen second KVS instance (from persisted file)
        auto kvs2_opt = KvsInstance::create(params2);
        if (!kvs2_opt) {
            throw std::runtime_error("Failed to reopen KVS instance 2");
        }
        auto kvs2 = *kvs2_opt;

        // Read values back
        auto value1_opt = kvs1->get_value(test_input.key);
        if (!value1_opt) {
            throw std::runtime_error("Failed to read kvs1 value");
        }
        double value1 = *value1_opt;

        auto value2_opt = kvs2->get_value(test_input.key);
        if (!value2_opt) {
            throw std::runtime_error("Failed to read kvs2 value");
        }
        double value2 = *value2_opt;

        // Match Rust tracing JSON shape expected by FIT log filters.
        const std::string timestamp = unix_seconds_string();

        std::cout << "{\"timestamp\":\"" << timestamp
                  << "\",\"level\":\"INFO\",\"fields\":{\"instance\":\""
                  << params1.instance_id.to_string()
                  << "\",\"key\":\"" << test_input.key
                  << "\",\"value\":" << value1
                  << "},\"target\":\"cpp_test_scenarios::scenarios::persistency::multiple_kvs_per_app\",\"threadId\":\"ThreadId(1)\"}"
                  << std::endl;

        std::cout << "{\"timestamp\":\"" << timestamp
                  << "\",\"level\":\"INFO\",\"fields\":{\"instance\":\""
                  << params2.instance_id.to_string()
                  << "\",\"key\":\"" << test_input.key
                  << "\",\"value\":" << value2
                  << "},\"target\":\"cpp_test_scenarios::scenarios::persistency::multiple_kvs_per_app\",\"threadId\":\"ThreadId(1)\"}"
                  << std::endl;

        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params1)) {
            throw std::runtime_error("Failed to normalize KVS snapshot output for instance 1");
        }
        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params2)) {
            throw std::runtime_error("Failed to normalize KVS snapshot output for instance 2");
        }
    }
}

Scenario::Ptr make_multiple_kvs_per_app_scenario() {
    return Scenario::Ptr{new MultipleKvsPerApp{}};
}
