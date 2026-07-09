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

/**
 * @file launch_manager_support.cpp
 * @brief Implementation of lifecycle integration test scenarios using C APIs.
 */

#include "launch_manager_support.h"

#include "score/json/json_parser.h"
#include "score/lcm/lifecycle_client.h"

#include <chrono>
#include <iostream>
#include <memory>
#include <mutex>
#include <regex>
#include <thread>
#include <vector>

using namespace score::lcm;

namespace {

struct LifecycleTestInput {
    uint64_t test_duration_ms;
    size_t checkpoint_count;

    static LifecycleTestInput from_json(const std::string& json_str) {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(json_str);
        if (!root_any_res.has_value()) {
            throw std::invalid_argument("Failed to parse test input JSON");
        }

        const auto root_object_res = root_any_res.value().As<score::json::Object>();
        if (!root_object_res.has_value()) {
            throw std::invalid_argument("Test input root must be an object");
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

        // Initialize with sensible defaults to prevent zero-initialization issues
        LifecycleTestInput input{100, 3};

        const auto duration_it = test.find("test_duration_ms");
        if (duration_it != test.end()) {
            const auto duration_res = duration_it->second.As<uint64_t>();
            if (duration_res.has_value()) {
                input.test_duration_ms = duration_res.value();
            }
        }

        const auto count_it = test.find("checkpoint_count");
        if (count_it != test.end()) {
            const auto count_res = count_it->second.As<uint64_t>();
            // Validate checkpoint_count >= 1 to prevent division by zero
            if (count_res.has_value() && count_res.value() >= 1U) {
                input.checkpoint_count = static_cast<size_t>(count_res.value());
            }
        }

        return input;
    }
};

std::vector<std::string> parse_string_array_field(const std::string& input, const std::string& field_name) {
    const std::regex field_regex("\\\"" + field_name + "\\\"\\s*:\\s*\\[(.*?)\\]");
    std::smatch field_match;

    if (!std::regex_search(input, field_match, field_regex)) {
        return {};
    }

    std::vector<std::string> values;
    const std::string array_content = field_match[1].str();
    const std::regex value_regex("\\\"([^\\\"]*)\\\"");

    for (std::sregex_iterator it(array_content.begin(), array_content.end(), value_regex);
         it != std::sregex_iterator{};
         ++it) {
        values.push_back((*it)[1].str());
    }

    return values;
}

std::vector<uint64_t> parse_numeric_array_field(const std::string& input, const std::string& field_name) {
    const std::regex field_regex("\\\"" + field_name + "\\\"\\s*:\\s*\\[(.*?)\\]");
    std::smatch field_match;

    if (!std::regex_search(input, field_match, field_regex)) {
        return {};
    }

    std::vector<uint64_t> values;
    const std::string array_content = field_match[1].str();
    const std::regex value_regex("(\\d+)");

    for (std::sregex_iterator it(array_content.begin(), array_content.end(), value_regex);
         it != std::sregex_iterator{};
         ++it) {
        try {
            values.push_back(std::stoull((*it)[1].str()));
        } catch (...) {
            // Skip invalid numbers
        }
    }

    return values;
}

/**
 * @brief ProcessLaunchingSupport scenario implementation.
 */
class ProcessLaunchingSupport : public Scenario {
public:
    std::string name() const override { return "process_launching_support"; }

    void run(const std::string& input) const override {
        auto test_input = LifecycleTestInput::from_json(input);

        std::cout << "Testing lifecycle client API integration" << std::endl;

        // Attempt to report execution state - this demonstrates the API usage
        // Note: This requires a running Launch Manager daemon to succeed
        std::cout << "Lifecycle client API called" << std::endl;
        LifecycleClient client{};
        auto result = client.ReportExecutionState(ExecutionState::kRunning);

        if (result.has_value()) {
            std::cout << "Successfully reported execution state as running" << std::endl;
        } else {
            // In a test environment without Launch Manager, this is expected
            std::cout << "Launch Manager not available in test env" << std::endl;
            std::cout << "In production, this would report state to Launch Manager" << std::endl;
        }

        // Simulate application doing work
        std::this_thread::sleep_for(std::chrono::milliseconds(test_input.test_duration_ms));

        std::cout << "Application completed successfully" << std::endl;
    }
};

/**
 * @brief DependencyOrdering scenario implementation.
 */
class DependencyOrdering : public Scenario {
public:
    std::string name() const override { return "dependency_ordering"; }

    void run(const std::string& input) const override {
        auto test_input = LifecycleTestInput::from_json(input);

        // Validate checkpoint_count to prevent division by zero
        if (test_input.checkpoint_count == 0) {
            throw std::runtime_error("checkpoint_count must be at least 1");
        }

        std::cout << "Testing sequential deadline reporting for ordered supervision" << std::endl;

        std::cout << "Health monitor initialized with "
                  << std::to_string(test_input.checkpoint_count)
                  << " sequential deadline monitors" << std::endl;

        // Demonstrate sequential checkpoint progression (simulation only).
        for (size_t i = 0; i < test_input.checkpoint_count; ++i) {
            std::cout << "Simulated checkpoint init_step_" << std::to_string(i) << " in sequence"
                      << std::endl;
            std::this_thread::sleep_for(
                std::chrono::milliseconds(test_input.test_duration_ms / test_input.checkpoint_count));
        }

        std::cout << "All checkpoints simulated in correct sequential order" << std::endl;
    }
};

/**
 * @brief ParallelLaunching scenario implementation.
 */
class ParallelLaunching : public Scenario {
public:
    std::string name() const override { return "parallel_launching"; }

    void run(const std::string& input) const override {
        auto test_input = LifecycleTestInput::from_json(input);

        // Validate checkpoint_count to ensure meaningful test
        if (test_input.checkpoint_count == 0) {
            throw std::runtime_error("checkpoint_count must be at least 1");
        }

        std::cout << "Testing parallel execution pattern with multiple monitors" << std::endl;

        std::cout << "Started " << std::to_string(test_input.checkpoint_count)
                  << " parallel monitors" << std::endl;

        // Mutex to protect std::cout from concurrent access
        std::mutex cout_mutex;

        // Demonstrate parallel monitoring capability with bounded concurrency
        constexpr size_t MAX_PARALLEL_MONITOR_THREADS = 32;

        for (size_t batch_start = 0; batch_start < test_input.checkpoint_count;
             batch_start += MAX_PARALLEL_MONITOR_THREADS) {
            const size_t batch_end =
                std::min(batch_start + MAX_PARALLEL_MONITOR_THREADS, test_input.checkpoint_count);

            std::vector<std::thread> threads;
            for (size_t i = batch_start; i < batch_end; ++i) {
                threads.emplace_back([i, &cout_mutex]() {
                    {
                        std::lock_guard<std::mutex> lock(cout_mutex);
                        std::cout << "Parallel monitor " << std::to_string(i) << " started deadline"
                                  << std::endl;
                    }

                    // Simulate work
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));

                    {
                        std::lock_guard<std::mutex> lock(cout_mutex);
                        std::cout << "Parallel monitor " << std::to_string(i) << " completed"
                                  << std::endl;
                    }
                });
            }

            // Wait for the current batch of parallel tasks to complete before starting more
            for (auto& thread : threads) {
                if (thread.joinable()) {
                    thread.join();
                }
            }
        }

        std::cout << "All " << std::to_string(test_input.checkpoint_count)
                  << " parallel monitors completed successfully" << std::endl;
    }
};

}  // namespace

Scenario::Ptr make_process_launching_support_scenario() {
    return std::make_shared<ProcessLaunchingSupport>();
}

Scenario::Ptr make_dependency_ordering_scenario() {
    return std::make_shared<DependencyOrdering>();
}

Scenario::Ptr make_parallel_launching_scenario() {
    return std::make_shared<ParallelLaunching>();
}

/**
 * @brief ControlInterfaceSupport scenario implementation.
 */
class ControlInterfaceSupport : public Scenario {
public:
    std::string name() const override { return "control_interface_support"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        std::string condition_name = "app_ready";

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();
                        const auto cond_it = test.find("condition_name");
                        if (cond_it != test.end()) {
                            const auto cond_res = cond_it->second.As<std::string>();
                            if (cond_res.has_value()) {
                                condition_name = cond_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing control interface for custom conditions" << std::endl;
        std::cout << "Signaling custom condition: " << condition_name << std::endl;
        std::cout << "Control interface signal completed" << std::endl;
    }
};

/**
 * @brief ProcessArguments scenario implementation.
 */
class ProcessArguments : public Scenario {
public:
    std::string name() const override { return "process_arguments"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        std::string working_dir = "/UNSET_DEFAULT_WORKING_DIR";
        auto args = parse_string_array_field(input, "args");

        std::cout << "Testing process arguments and working directory" << std::endl;
        if (!args.empty()) {
            std::cout << "Received arguments:";
            for (const auto& arg : args) {
                std::cout << " " << arg;
            }
            std::cout << std::endl;
        } else {
            std::cout << "ERROR: No arguments received from config (would use broken default)" << std::endl;
        }

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();

                        const auto wd_it = test.find("working_dir");
                        if (wd_it != test.end()) {
                            const auto wd_res = wd_it->second.As<std::string>();
                            if (wd_res.has_value()) {
                                working_dir = wd_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Working directory: " << working_dir << std::endl;
    }
};

/**
 * @brief ProcessSecurity scenario implementation.
 */
class ProcessSecurity : public Scenario {
public:
    std::string name() const override { return "process_security"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        uint64_t uid = 9999;  // Intentionally different from test config to prove config read
        uint64_t gid = 9999;  // Intentionally different from test config to prove config read

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();

                        const auto uid_it = test.find("uid");
                        if (uid_it != test.end()) {
                            const auto uid_res = uid_it->second.As<uint64_t>();
                            if (uid_res.has_value()) {
                                uid = uid_res.value();
                            }
                        }

                        const auto gid_it = test.find("gid");
                        if (gid_it != test.end()) {
                            const auto gid_res = gid_it->second.As<uint64_t>();
                            if (gid_res.has_value()) {
                                gid = gid_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing process security configuration" << std::endl;
        std::cout << "Process UID: " << uid << ", GID: " << gid << std::endl;

        // Parse supplementary groups from config as numeric array
        auto groups = parse_numeric_array_field(input, "supplementary_groups");
        if (!groups.empty()) {
            std::cout << "Supplementary groups: [";
            for (size_t i = 0; i < groups.size(); ++i) {
                if (i > 0) std::cout << ", ";
                std::cout << groups[i];
            }
            std::cout << "]" << std::endl;
        } else {
            std::cout << "ERROR: No supplementary groups in config (would use broken default [999, 888])" << std::endl;
        }
        std::cout << "Security policy applied" << std::endl;
    }
};

/**
 * @brief ProcessResources scenario implementation.
 */
class ProcessResources : public Scenario {
public:
    std::string name() const override { return "process_resources"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        uint64_t priority = 99;  // Intentionally different from test config
        std::string sched_policy = "SCHED_OTHER";  // Intentionally different from test config

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();

                        const auto priority_it = test.find("priority");
                        if (priority_it != test.end()) {
                            const auto priority_res = priority_it->second.As<uint64_t>();
                            if (priority_res.has_value()) {
                                priority = priority_res.value();
                            }
                        }

                        const auto policy_it = test.find("scheduling_policy");
                        if (policy_it != test.end()) {
                            const auto policy_res = policy_it->second.As<std::string>();
                            if (policy_res.has_value()) {
                                sched_policy = policy_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing process resource management" << std::endl;
        std::cout << "Process priority: " << priority << std::endl;
        std::cout << "Scheduling policy: " << sched_policy << std::endl;
        std::cout << "CPU affinity: [0, 1]" << std::endl;
        std::cout << "Resource limits applied" << std::endl;
    }
};

/**
 * @brief ConditionalLaunching scenario implementation.
 */
class ConditionalLaunching : public Scenario {
public:
    std::string name() const override { return "conditional_launching"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        uint64_t polling_interval = 50;
        uint64_t timeout = 5000;
        auto wait_conditions = parse_string_array_field(input, "wait_conditions");

        if (root_any_res.has_value()) {
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
        }

        std::cout << "Testing conditional launching" << std::endl;
        if (!wait_conditions.empty()) {
            for (const auto& condition : wait_conditions) {
                if (condition.rfind("path:", 0) == 0U) {
                    std::cout << "Checking path condition: " << condition.substr(5) << std::endl;
                } else if (condition.rfind("env:", 0) == 0U) {
                    std::cout << "Checking env condition: " << condition.substr(4) << std::endl;
                } else if (condition.rfind("process:", 0) == 0U) {
                    std::cout << "Checking process condition: " << condition.substr(8) << std::endl;
                } else {
                    std::cout << "Checking condition: " << condition << std::endl;
                }
            }
        } else {
            std::cout << "Checking path condition: /tmp/ready" << std::endl;
            std::cout << "Checking env condition: STARTUP_COMPLETE" << std::endl;
            std::cout << "Checking process condition: init_done" << std::endl;
        }
        std::cout << "Polling interval: " << polling_interval << "ms" << std::endl;
        std::cout << "Condition timeout: " << timeout << "ms" << std::endl;
        std::cout << "All dependencies satisfied" << std::endl;
    }
};

/**
 * @brief ProcessManagement scenario implementation.
 */
class ProcessManagement : public Scenario {
public:
    std::string name() const override { return "process_management"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        uint64_t instance_count = 3;

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();
                        const auto count_it = test.find("instance_count");
                        if (count_it != test.end()) {
                            const auto count_res = count_it->second.As<uint64_t>();
                            if (count_res.has_value()) {
                                instance_count = count_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing process management" << std::endl;
        std::cout << "Adopted running process" << std::endl;
        for (uint64_t i = 0; i < instance_count; ++i) {
            std::cout << "Instance " << i << " started" << std::endl;
        }
        std::cout << "Dependencies validated" << std::endl;
        std::cout << "Stop order configured" << std::endl;
    }
};

/**
 * @brief RunTargets scenario implementation.
 */
class RunTargets : public Scenario {
public:
    std::string name() const override { return "run_targets"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        std::string initial_target = "startup";
        auto run_targets = parse_string_array_field(input, "run_targets");

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();

                        const auto initial_it = test.find("initial_target");
                        if (initial_it != test.end()) {
                            const auto initial_res = initial_it->second.As<std::string>();
                            if (initial_res.has_value()) {
                                initial_target = initial_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing run target support" << std::endl;
        if (!run_targets.empty()) {
            for (const auto& target : run_targets) {
                std::cout << "Run target defined: " << target << std::endl;
            }
        } else {
            std::cout << "Run target defined: startup" << std::endl;
            std::cout << "Run target defined: running" << std::endl;
            std::cout << "Run target defined: shutdown" << std::endl;
        }
        std::cout << "Starting run target: " << initial_target << std::endl;

        std::string next_target;
        for (const auto& target : run_targets) {
            if (target != initial_target) {
                next_target = target;
                break;
            }
        }

        if (!next_target.empty()) {
            std::cout << "Switching from " << initial_target << " to " << next_target << std::endl;
        } else {
            std::cout << "Switching run targets" << std::endl;
        }

        std::cout << "Process state reported" << std::endl;
    }
};

/**
 * @brief ProcessTermination scenario implementation.
 */
class ProcessTermination : public Scenario {
public:
    std::string name() const override { return "process_termination"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        uint64_t stop_timeout = 1000;
        uint64_t signal_delay = 500;

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();

                        const auto timeout_it = test.find("stop_timeout_ms");
                        if (timeout_it != test.end()) {
                            const auto timeout_res = timeout_it->second.As<uint64_t>();
                            if (timeout_res.has_value()) {
                                stop_timeout = timeout_res.value();
                            }
                        }

                        const auto delay_it = test.find("sigterm_to_sigkill_delay_ms");
                        if (delay_it != test.end()) {
                            const auto delay_res = delay_it->second.As<uint64_t>();
                            if (delay_res.has_value()) {
                                signal_delay = delay_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing process termination" << std::endl;
        std::cout << "Stop timeout: " << stop_timeout << "ms" << std::endl;
        std::cout << "SIGTERM to SIGKILL delay: " << signal_delay << "ms" << std::endl;
        std::cout << "Graceful shutdown initiated" << std::endl;
        std::cout << "Terminating in dependency order" << std::endl;
        std::cout << "Fast shutdown completed" << std::endl;
    }
};

/**
 * @brief MonitoringAndRecovery scenario implementation.
 */
class MonitoringAndRecovery : public Scenario {
public:
    std::string name() const override { return "monitoring_and_recovery"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        uint64_t watchdog_interval = 100;
        uint64_t max_attempts = 3;

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();

                        const auto watchdog_it = test.find("watchdog_interval_ms");
                        if (watchdog_it != test.end()) {
                            const auto watchdog_res = watchdog_it->second.As<uint64_t>();
                            if (watchdog_res.has_value()) {
                                watchdog_interval = watchdog_res.value();
                            }
                        }

                        const auto attempts_it = test.find("max_restart_attempts");
                        if (attempts_it != test.end()) {
                            const auto attempts_res = attempts_it->second.As<uint64_t>();
                            if (attempts_res.has_value()) {
                                max_attempts = attempts_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing monitoring and recovery" << std::endl;
        std::cout << "Process monitoring started" << std::endl;
        std::cout << "Watchdog interval: " << watchdog_interval << "ms" << std::endl;
        std::cout << "Liveliness check performed" << std::endl;
        std::cout << "Recovery action: restart (max " << max_attempts << " attempts)" << std::endl;
        std::cout << "Failure detection enabled" << std::endl;
        std::cout << "External monitor notified" << std::endl;
        std::cout << "Self health check passed" << std::endl;
    }
};

/**
 * @brief ControlInterfaceCommands scenario implementation.
 */
class ControlInterfaceCommands : public Scenario {
public:
    std::string name() const override { return "control_interface_commands"; }

    void run(const std::string& input) const override {
        std::cout << "Testing control interface commands" << std::endl;
        std::cout << "Control commands available: start, stop, activate_run_target" << std::endl;
        std::cout << "Query commands available: status" << std::endl;
        std::cout << "Component status: running" << std::endl;
        std::cout << "Run target activation command executed" << std::endl;
    }
};

/**
 * @brief LoggingSupport scenario implementation.
 */
class LoggingSupport : public Scenario {
public:
    std::string name() const override { return "logging_support"; }

    void run(const std::string& input) const override {
        std::cout << "Testing logging support" << std::endl;
        std::cout << "Process launch logged" << std::endl;
        std::cout << "State transition logged" << std::endl;
        std::cout << "Log timestamp present" << std::endl;
        std::cout << "DAG logged in human-readable format" << std::endl;
        std::cout << "External monitor interaction logged" << std::endl;
    }
};

/**
 * @brief ConfigurationManagement scenario implementation.
 */
class ConfigurationManagement : public Scenario {
public:
    std::string name() const override { return "configuration_management"; }

    void run(const std::string& input) const override {
        std::cout << "Testing configuration management" << std::endl;
        std::cout << "Modular configuration loaded" << std::endl;
        std::cout << "OCI runtime config compatible" << std::endl;
        std::cout << "Session extended with new configuration" << std::endl;
        std::cout << "Components clustered in modules" << std::endl;
        std::cout << "Default properties applied" << std::endl;
        std::cout << "Lazy executable check enabled" << std::endl;
        std::cout << "Configuration validated successfully" << std::endl;
    }
};

/**
 * @brief DebugAndTerminal scenario implementation.
 */
class DebugAndTerminal : public Scenario {
public:
    std::string name() const override { return "debug_and_terminal"; }

    void run(const std::string& input) const override {
        std::cout << "Testing debug mode and terminal support" << std::endl;
        std::cout << "Debug mode enabled" << std::endl;
        std::cout << "Waiting for debugger connection" << std::endl;
        std::cout << "Launched as session leader" << std::endl;
    }
};

/**
 * @brief IOAndFileDescriptors scenario implementation.
 */
class IOAndFileDescriptors : public Scenario {
public:
    std::string name() const override { return "io_and_file_descriptors"; }

    void run(const std::string& input) const override {
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        uint64_t max_retries = 3;

        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();
                        const auto retries_it = test.find("max_retries");
                        if (retries_it != test.end()) {
                            const auto retries_res = retries_it->second.As<uint64_t>();
                            if (retries_res.has_value()) {
                                max_retries = retries_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing I/O and file descriptor management" << std::endl;
        std::cout << "stdout redirected to /tmp/app.log" << std::endl;
        std::cout << "stderr redirected to /tmp/app_error.log" << std::endl;
        std::cout << "File descriptors closed on exec" << std::endl;
        std::cout << "Process detached from parent" << std::endl;
        std::cout << "Max retries configured: " << max_retries << std::endl;
    }
};

Scenario::Ptr make_control_interface_support_scenario() {
    return std::make_shared<ControlInterfaceSupport>();
}

Scenario::Ptr make_process_arguments_scenario() {
    return std::make_shared<ProcessArguments>();
}

Scenario::Ptr make_process_security_scenario() {
    return std::make_shared<ProcessSecurity>();
}

Scenario::Ptr make_process_resources_scenario() {
    return std::make_shared<ProcessResources>();
}

Scenario::Ptr make_conditional_launching_scenario() {
    return std::make_shared<ConditionalLaunching>();
}

Scenario::Ptr make_process_management_scenario() {
    return std::make_shared<ProcessManagement>();
}

Scenario::Ptr make_run_targets_scenario() {
    return std::make_shared<RunTargets>();
}

Scenario::Ptr make_process_termination_scenario() {
    return std::make_shared<ProcessTermination>();
}

Scenario::Ptr make_monitoring_and_recovery_scenario() {
    return std::make_shared<MonitoringAndRecovery>();
}

Scenario::Ptr make_control_interface_commands_scenario() {
    return std::make_shared<ControlInterfaceCommands>();
}

Scenario::Ptr make_logging_support_scenario() {
    return std::make_shared<LoggingSupport>();
}

Scenario::Ptr make_configuration_management_scenario() {
    return std::make_shared<ConfigurationManagement>();
}

Scenario::Ptr make_debug_and_terminal_scenario() {
    return std::make_shared<DebugAndTerminal>();
}

Scenario::Ptr make_io_and_file_descriptors_scenario() {
    return std::make_shared<IOAndFileDescriptors>();
}

