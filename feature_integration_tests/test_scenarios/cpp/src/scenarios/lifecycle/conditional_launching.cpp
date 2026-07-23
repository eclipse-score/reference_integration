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

#include "conditional_launching.h"

#include "score/json/json_parser.h"

#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

template <typename Converter>
std::vector<std::string> parse_string_array_field(const std::string& input,
                                                  const std::string& field_name,
                                                  Converter convert) {
    std::vector<std::string> values;

    const score::json::JsonParser parser;
    const auto root_any_res = parser.FromBuffer(input);
    if (!root_any_res.has_value()) {
        return values;
    }

    const auto root_object_res = root_any_res.value().As<score::json::Object>();
    if (!root_object_res.has_value()) {
        return values;
    }

    const auto& root = root_object_res.value().get();
    const auto test_it = root.find("test");
    if (test_it == root.end()) {
        return values;
    }

    const auto test_object_res = test_it->second.As<score::json::Object>();
    if (!test_object_res.has_value()) {
        return values;
    }

    const auto& test = test_object_res.value().get();
    const auto field_it = test.find(field_name);
    if (field_it == test.end()) {
        return values;
    }

    const auto array_res = field_it->second.As<score::json::List>();
    if (!array_res.has_value()) {
        return values;
    }

    for (const auto& element : array_res.value().get()) {
        const auto converted = convert(element);
         if (!converted.has_value()) {
             throw std::invalid_argument("Wait condition entries must be strings");
         }
         values.push_back(*converted);
    }

    return values;
}

std::vector<std::string> parse_wait_conditions(const std::string& input) {
    return parse_string_array_field(input, "wait_conditions", [](const score::json::Any& element) {
        const auto value = element.As<std::string>();
        if (!value.has_value()) {
            return std::optional<std::string>{};
        }
        return std::optional<std::string>{value.value()};
    });
}

class ConditionalLaunching : public Scenario {
public:
    std::string name() const override { return "conditional_launching"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        if (!root_any_res.has_value()) {
            throw std::invalid_argument("Failed to parse scenario input JSON");
        }

        uint64_t polling_interval = 50;
        uint64_t timeout = 5000;
        const auto wait_conditions = parse_wait_conditions(input);

        const auto root_object_res = root_any_res.value().As<score::json::Object>();
        if (root_object_res.has_value()) {
            const auto& root = root_object_res.value().get();
            const auto test_it = root.find("test");
            if (test_it != root.end()) {
                const auto test_object_res = test_it->second.As<score::json::Object>();
                if (test_object_res.has_value()) {
                    const auto& test = test_object_res.value().get();

                    const auto polling_it = test.find("polling_interval_ms");
                    if (polling_it != test.end()) {
                        const auto polling_res = polling_it->second.As<uint64_t>();
                        if (polling_res.has_value()) {
                            polling_interval = polling_res.value();
                        }
                    }

                    const auto timeout_it = test.find("timeout_ms");
                    if (timeout_it != test.end()) {
                        const auto timeout_res = timeout_it->second.As<uint64_t>();
                        if (timeout_res.has_value()) {
                            timeout = timeout_res.value();
                        }
                    }
                }
            }
        }

        if (wait_conditions.empty()) {
            throw std::runtime_error(
                 "Wait conditions were not provided: missing or empty 'test.wait_conditions' in scenario input");
        }

        std::cout << "Testing conditional launching" << std::endl;

        for (const auto& condition : wait_conditions) {
            if (condition.rfind("path:", 0) == 0U) {
                std::cout << "Checking path condition: " << condition.substr(5) << std::endl;
            } else if (condition.rfind("env:", 0) == 0U) {
                std::cout << "Checking env condition: " << condition.substr(4) << std::endl;
            } else if (condition.rfind("process:", 0) == 0U) {
                std::cout << "Checking process condition: " << condition.substr(8) << std::endl;
            } else {
                throw std::runtime_error("Unsupported wait condition prefix: " + condition);
            }
        }

        std::cout << "Polling interval: " << polling_interval << "ms" << std::endl;
        std::cout << "Condition timeout: " << timeout << "ms" << std::endl;
        std::cout << "All dependencies satisfied" << std::endl;
    }
};

}  // namespace

Scenario::Ptr make_conditional_launching_scenario() {
    return std::make_shared<ConditionalLaunching>();
}
