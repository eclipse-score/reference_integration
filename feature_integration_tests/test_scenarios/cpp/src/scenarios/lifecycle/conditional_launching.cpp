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

#include "internals/log_helpers.h"
#include "score/json/json_parser.h"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {

constexpr const char* kTarget = "cpp_test_scenarios::scenarios::lifecycle::conditional_launching";

void log_info(const std::string& message) {
    log_helpers::log_info("\"message\":\"" + log_helpers::json_escape(message) + "\"", kTarget);
}

bool path_condition_met(const std::string& path) {
    std::error_code ec;
    return std::filesystem::exists(path, ec) && !ec;
}

bool env_condition_met(const std::string& name) {
    return std::getenv(name.c_str()) != nullptr;
}

// True if some process's /proc/<pid>/comm (15-char truncated) or argv[0] basename equals
// `process_name`. Best effort: a process exiting mid-scan counts as "not found this pass".
bool process_condition_met(const std::string& process_name) {
    // Iteration can still throw filesystem_error when a pid vanishes, despite the error_code overload.
    try {
        std::error_code ec;
        for (const auto& entry : std::filesystem::directory_iterator(
                 "/proc", std::filesystem::directory_options::skip_permission_denied, ec)) {
            const std::string pid = entry.path().filename().string();
            if (pid.empty() ||
                !std::all_of(pid.begin(), pid.end(), [](unsigned char c) { return std::isdigit(c); })) {
                continue;
            }

            std::ifstream comm(entry.path() / "comm");
            std::string comm_value;
            if (comm && std::getline(comm, comm_value) && comm_value == process_name) {
                return true;
            }

            std::ifstream cmdline(entry.path() / "cmdline");
            std::stringstream cmdline_buffer;
            cmdline_buffer << cmdline.rdbuf();
            const std::string argv0 = cmdline_buffer.str();
            if (!argv0.empty()) {
                const auto argv0_end = argv0.find('\0');
                const std::string first_arg = argv0.substr(0, argv0_end);
                // Basename, not suffix: "/usr/bin/oversleep" must not match "sleep".
                const auto slash_pos = first_arg.find_last_of('/');
                const std::string basename =
                    slash_pos == std::string::npos ? first_arg : first_arg.substr(slash_pos + 1);
                if (basename == process_name) {
                    return true;
                }
            }
        }
    } catch (const std::filesystem::filesystem_error&) {
        return false;
    }
    return false;
}

template <typename Converter>
std::optional<std::vector<std::string>> parse_string_array_field(const std::string& input,
                                                                 const std::string& field_name,
                                                                 Converter convert) {
    std::vector<std::string> values;

    const score::json::JsonParser parser;
    const auto root_any_res = parser.FromBuffer(input);
    if (!root_any_res.has_value()) {
        return std::nullopt;
    }

    const auto root_object_res = root_any_res.value().As<score::json::Object>();
    if (!root_object_res.has_value()) {
        return std::nullopt;
    }

    const auto& root = root_object_res.value().get();
    const auto test_it = root.find("test");
    if (test_it == root.end()) {
        return std::nullopt;
    }

    const auto test_object_res = test_it->second.As<score::json::Object>();
    if (!test_object_res.has_value()) {
        return std::nullopt;
    }

    const auto& test = test_object_res.value().get();
    const auto field_it = test.find(field_name);
    if (field_it == test.end()) {
        return std::nullopt;
    }

    const auto array_res = field_it->second.As<score::json::List>();
    if (!array_res.has_value()) {
        return std::nullopt;
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

std::optional<std::vector<std::string>> parse_wait_conditions(const std::string& input) {
    return parse_string_array_field(input, "wait_conditions", [](const score::json::Any& element) {
        const auto value = element.As<std::string>();
        if (!value.has_value()) {
            return std::optional<std::string>{};
        }
        return std::optional<std::string>{value.value()};
    });
}

// FIT stub (not launch_manager): validates `test.wait_conditions`, then polls each condition every
// `polling_interval_ms` until all are met or `timeout_ms` expires. A met condition stays latched,
// even if it later becomes false. Mirrors the Rust scenario, including its error messages.
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
        const auto wait_conditions_res = parse_wait_conditions(input);

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

        // Same messages as the Rust scenario: "missing" and "empty" are distinct errors.
        if (!wait_conditions_res.has_value()) {
            throw std::runtime_error(
                "Wait conditions were not provided: missing 'test.wait_conditions' in scenario input");
        }
        const auto& wait_conditions = *wait_conditions_res;
        if (wait_conditions.empty()) {
            throw std::runtime_error(
                "Wait conditions were not provided: empty 'test.wait_conditions' in scenario input");
        }

        log_info("Testing conditional launching");

        for (const auto& condition : wait_conditions) {
            if (condition.rfind("path:", 0) != 0U && condition.rfind("env:", 0) != 0U &&
                condition.rfind("process:", 0) != 0U) {
                throw std::runtime_error("Unsupported wait condition prefix: " + condition);
            }
        }

        log_info("Polling interval: " + std::to_string(polling_interval) + "ms");
        log_info("Condition timeout: " + std::to_string(timeout) + "ms");

        const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(timeout);
        std::vector<bool> satisfied(wait_conditions.size(), false);

        while (true) {
            bool all_satisfied = true;
            for (std::size_t i = 0; i < wait_conditions.size(); ++i) {
                if (satisfied[i]) {
                    continue;
                }
                const auto& condition = wait_conditions[i];
                bool met = false;
                if (condition.rfind("path:", 0) == 0U) {
                    met = path_condition_met(condition.substr(5));
                } else if (condition.rfind("env:", 0) == 0U) {
                    met = env_condition_met(condition.substr(4));
                } else {
                    met = process_condition_met(condition.substr(8));
                }

                if (met) {
                    satisfied[i] = true;
                    log_info("Condition satisfied: " + condition);
                } else {
                    all_satisfied = false;
                }
            }

            if (all_satisfied) {
                break;
            }

            if (std::chrono::steady_clock::now() >= deadline) {
                std::string unmet;
                for (std::size_t i = 0; i < wait_conditions.size(); ++i) {
                    if (!satisfied[i]) {
                        if (!unmet.empty()) {
                            unmet += ", ";
                        }
                        unmet += wait_conditions[i];
                    }
                }
                throw std::runtime_error("Timed out after " + std::to_string(timeout) +
                                          "ms waiting for condition(s): " + unmet);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(polling_interval));
        }

        log_info("All dependencies satisfied");
    }
};

}  // namespace

Scenario::Ptr make_conditional_launching_scenario() {
    return std::make_shared<ConditionalLaunching>();
}
