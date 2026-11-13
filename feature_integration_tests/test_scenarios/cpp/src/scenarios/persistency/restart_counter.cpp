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
#include "internals/log_helpers.h"
#include "../../internals/persistency/kvs_instance.h"

#include "score/json/json_parser.h"

#include <scenario.hpp>

#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct TestInput {
    std::string counter_key;
    std::vector<std::string> set_keys;
    std::vector<double> set_values;
    std::vector<std::string> reset_keys;
    std::vector<std::string> read_keys;

    static TestInput from_json(const std::string& input);
};

std::vector<std::string> string_list(const score::json::Object& test, const std::string& field) {
    std::vector<std::string> values;
    const auto it = test.find(field);
    if (it == test.end()) {
        return values;
    }
    const auto list_res = it->second.As<score::json::List>();
    if (!list_res.has_value()) {
        throw std::invalid_argument(field + " must be a list");
    }
    for (const auto& element : list_res.value().get()) {
        const auto value = element.As<std::string>();
        if (!value.has_value()) {
            throw std::invalid_argument(field + " entries must be strings");
        }
        values.push_back(value.value());
    }
    return values;
}

std::vector<double> double_list(const score::json::Object& test, const std::string& field) {
    std::vector<double> values;
    const auto it = test.find(field);
    if (it == test.end()) {
        return values;
    }
    const auto list_res = it->second.As<score::json::List>();
    if (!list_res.has_value()) {
        throw std::invalid_argument(field + " must be a list");
    }
    for (const auto& element : list_res.value().get()) {
        const auto value = element.As<double>();
        if (!value.has_value()) {
            throw std::invalid_argument(field + " entries must be numbers");
        }
        values.push_back(value.value());
    }
    return values;
}

TestInput TestInput::from_json(const std::string& input) {
    const score::json::JsonParser parser;
    const auto root_any_res = parser.FromBuffer(input);
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

    const auto counter_it = test.find("counter_key");
    if (counter_it == test.end()) {
        throw std::invalid_argument("Missing counter_key");
    }
    const auto counter_res = counter_it->second.As<std::string>();
    if (!counter_res.has_value()) {
        throw std::invalid_argument("counter_key must be a string");
    }

    TestInput parsed;
    parsed.counter_key = counter_res.value();
    parsed.set_keys = string_list(test, "set_keys");
    parsed.set_values = double_list(test, "set_values");
    parsed.reset_keys = string_list(test, "reset_keys");
    parsed.read_keys = string_list(test, "read_keys");
    if (parsed.set_keys.size() != parsed.set_values.size()) {
        throw std::invalid_argument("set_keys and set_values must have the same length");
    }
    return parsed;
}

void log_value(const std::string& key, double value, const std::string& source) {
    log_helpers::log_info("\"key\":\"" + log_helpers::json_escape(key) + "\",\"value\":" +
                              log_helpers::format_double_python(value) + ",\"source\":\"" + source + "\"",
                          "cpp_test_scenarios::scenarios::persistency::restart_counter");
}

/// The stored value of `key`, or nullopt if it has none. Throws if the lookup or read fails,
/// so a broken KVS is never mistaken for an absent key.
std::optional<double> stored_value(KvsInstance& kvs, const std::string& key) {
    const auto exists = kvs.key_exists(key);
    if (!exists) {
        throw std::runtime_error("Failed to check key: " + key);
    }
    if (!*exists) {
        return std::nullopt;
    }
    const auto value = kvs.get_value(key);
    if (!value) {
        throw std::runtime_error("Failed to read stored value: " + key);
    }
    return value;
}

/// One launch of a KVS-owning process, meant to be started repeatedly by Launch Manager.
///
/// Reads `counter_key` (0 when not stored), stores it incremented, applies `set_keys`/
/// `set_values`, calls `reset_key` on `reset_keys`, reads back each of `read_keys` and flushes.
/// A read-back logs the stored value (`source = "read_back"`) or, when the key has no stored
/// value (e.g. after `reset_key`), its default (`source = "read_back_default"`). Any read that
/// fails for another reason fails the scenario instead of falling back. The counter only equals
/// the number of launches if every launch loaded the state its predecessor flushed.
/// The snapshot is not normalized, so the next C++ launch can reload it.
class RestartCounter final : public Scenario {
public:
    std::string name() const final { return "restart_counter"; }

    void run(const std::string& input) const final {
        const KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");
        const TestInput test_input = TestInput::from_json(input);

        auto kvs_opt = KvsInstance::create(params);
        if (!kvs_opt) {
            throw std::runtime_error("Failed to create KVS instance");
        }
        auto kvs = *kvs_opt;

        const double loaded = stored_value(*kvs, test_input.counter_key).value_or(0.0);
        log_value(test_input.counter_key, loaded, "loaded_on_open");

        if (!kvs->set_value(test_input.counter_key, loaded + 1.0)) {
            throw std::runtime_error("Failed to set counter value");
        }
        for (size_t i = 0; i < test_input.set_keys.size(); ++i) {
            if (!kvs->set_value(test_input.set_keys[i], test_input.set_values[i])) {
                throw std::runtime_error("Failed to set value: " + test_input.set_keys[i]);
            }
        }
        for (const auto& key : test_input.reset_keys) {
            if (!kvs->reset_key(key)) {
                throw std::runtime_error("Failed to reset key: " + key);
            }
        }
        for (const auto& key : test_input.read_keys) {
            if (const auto value = stored_value(*kvs, key)) {
                log_value(key, *value, "read_back");
                continue;
            }
            const auto default_value = kvs->get_default_value_f64(key);
            if (!default_value) {
                throw std::runtime_error("Failed to read default value: " + key);
            }
            log_value(key, *default_value, "read_back_default");
        }
        if (!kvs->flush()) {
            throw std::runtime_error("Failed to flush KVS");
        }
    }
};

}  // anonymous namespace

Scenario::Ptr make_restart_counter_scenario() {
    return std::make_shared<RestartCounter>();
}
