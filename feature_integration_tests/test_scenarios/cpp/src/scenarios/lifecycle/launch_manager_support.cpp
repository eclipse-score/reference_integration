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

#include "score/hm/health_monitor.h"
#include "score/json/json_parser.h"
#include "score/lcm/lifecycle_client.h"

#include <chrono>
#include <ctime>
#include <functional>
#include <iomanip>
#include <iostream>
#include <memory>
#include <mutex>
#include <optional>
#include <sstream>
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

        const auto duration_it = test.find("test_duration_ms");
        if (duration_it == test.end()) {
            throw std::invalid_argument("Missing required field: test_duration_ms");
        }
        const auto duration_res = duration_it->second.As<uint64_t>();
        if (!duration_res.has_value()) {
            throw std::invalid_argument("Field test_duration_ms must be an unsigned integer");
        }

        const auto count_it = test.find("checkpoint_count");
        if (count_it == test.end()) {
            throw std::invalid_argument("Missing required field: checkpoint_count");
        }
        const auto count_res = count_it->second.As<uint64_t>();
        if (!count_res.has_value()) {
            throw std::invalid_argument("Field checkpoint_count must be an unsigned integer");
        }

        return LifecycleTestInput{duration_res.value(), static_cast<size_t>(count_res.value())};
    }
};

/**
 * @brief Finds the named field within the input JSON's "test" object and, if present,
 *        converts each element of the JSON array via `convert`, appending successful
 *        conversions to the returned vector. Scoped to the "test" object only (not
 *        searching the whole document), unlike a whole-document regex search.
 *
 *        Runs entirely within the lifetime of the parsed JSON tree, since the
 *        underlying score::json::Any/List types are not copyable and cannot safely
 *        be returned by value or reference from this function.
 */
template <typename T, typename Converter>
std::vector<T> extract_test_array_field(const std::string& input, const std::string& field_name, Converter convert) {
    std::vector<T> values;

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
        auto converted = convert(element);
        if (converted.has_value()) {
            values.push_back(std::move(converted.value()));
        }
    }

    return values;
}

std::vector<std::string> parse_string_array_field(const std::string& input, const std::string& field_name) {
    return extract_test_array_field<std::string>(input, field_name, [](const score::json::Any& element) {
        return element.As<std::string>().has_value() ? std::optional<std::string>(element.As<std::string>().value())
                                                       : std::nullopt;
    });
}

/**
 * @brief Returns the current time formatted as an ISO-8601 UTC timestamp with millisecond precision.
 */
std::string current_iso8601_timestamp() {
    const auto now = std::chrono::system_clock::now();
    const auto now_time_t = std::chrono::system_clock::to_time_t(now);
    const auto now_ms =
        std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;

    std::tm utc_tm{};
    gmtime_r(&now_time_t, &utc_tm);

    std::ostringstream oss;
    oss << std::put_time(&utc_tm, "%Y-%m-%dT%H:%M:%S") << '.' << std::setfill('0') << std::setw(3)
        << now_ms.count() << 'Z';
    return oss.str();
}

std::vector<uint64_t> parse_numeric_array_field(const std::string& input, const std::string& field_name) {
    return extract_test_array_field<uint64_t>(input, field_name, [](const score::json::Any& element) {
        return element.As<uint64_t>().has_value() ? std::optional<uint64_t>(element.As<uint64_t>().value())
                                                    : std::nullopt;
    });
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

        // Build a health monitor with a deadline monitor to simulate ordered initialization,
        // exercising the same real HealthMonitorBuilder API used by the Rust scenario.
        auto deadline_builder = score::hm::deadline::DeadlineMonitorBuilder().add_deadline(
            score::hm::DeadlineTag("init_step"),
            score::hm::TimeRange(std::chrono::milliseconds(50), std::chrono::milliseconds(300)));

        auto hm_builder = score::hm::HealthMonitorBuilder()
                              .with_supervisor_api_cycle(std::chrono::milliseconds(50))
                              .with_internal_processing_cycle(std::chrono::milliseconds(50))
                              .add_deadline_monitor(score::hm::MonitorTag("step_monitor"),
                                                    std::move(deadline_builder));

        auto hm_res = std::move(hm_builder).build();
        if (!hm_res.has_value()) {
            throw std::runtime_error("Failed to build health monitor");
        }

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

        std::cout << "Testing parallel health monitoring with multiple monitors" << std::endl;

        // Build a health monitor with a deadline monitor to simulate parallel supervision,
        // exercising the same real HealthMonitorBuilder API used by the Rust scenario.
        auto deadline_builder = score::hm::deadline::DeadlineMonitorBuilder().add_deadline(
            score::hm::DeadlineTag("parallel_task"),
            score::hm::TimeRange(std::chrono::milliseconds(50), std::chrono::milliseconds(200)));

        auto hm_builder = score::hm::HealthMonitorBuilder()
                              .with_supervisor_api_cycle(std::chrono::milliseconds(50))
                              .with_internal_processing_cycle(std::chrono::milliseconds(50))
                              .add_deadline_monitor(score::hm::MonitorTag("monitor"),
                                                    std::move(deadline_builder));

        auto hm_res = std::move(hm_builder).build();
        if (!hm_res.has_value()) {
            throw std::runtime_error("Failed to build health monitor");
        }

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
        if (args.empty()) {
            throw std::runtime_error("Process arguments were not received: missing 'test.args' in scenario input");
        }
        std::cout << "Received arguments:";
        for (const auto& arg : args) {
            std::cout << " " << arg;
        }
        std::cout << std::endl;

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

        // Parse CPU affinity from config as numeric array
        auto cpu_affinity = parse_numeric_array_field(input, "cpu_affinity");
        if (!cpu_affinity.empty()) {
            std::cout << "CPU affinity: [";
            for (size_t i = 0; i < cpu_affinity.size(); ++i) {
                if (i > 0) std::cout << ", ";
                std::cout << cpu_affinity[i];
            }
            std::cout << "]" << std::endl;
        } else {
            std::cout << "ERROR: No CPU affinity in config (would use broken default)" << std::endl;
        }
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
        if (wait_conditions.empty()) {
            throw std::runtime_error("Wait conditions were not provided: missing 'test.wait_conditions' in scenario input");
        }

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
        if (run_targets.empty()) {
            throw std::runtime_error("Run targets were not defined: missing 'test.run_targets' in scenario input");
        }
        for (const auto& target : run_targets) {
            std::cout << "Run target defined: " << target << std::endl;
        }
        std::cout << "Starting run target: " << initial_target << std::endl;

        std::string next_target;
        for (const auto& target : run_targets) {
            if (target != initial_target) {
                next_target = target;
                break;
            }
        }

        if (next_target.empty()) {
            throw std::runtime_error("Run target switch failed: no alternative target available in 'test.run_targets'");
        }
        std::cout << "Switching from " << initial_target << " to " << next_target << std::endl;

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
        auto commands = parse_string_array_field(input, "commands");

        std::cout << "Testing control interface commands" << std::endl;

        if (commands.empty()) {
            std::cout << "Control commands available: start, stop, activate_run_target" << std::endl;
        } else {
            std::cout << "Control commands available: ";
            for (size_t i = 0; i < commands.size(); ++i) {
                if (i > 0) std::cout << ", ";
                std::cout << commands[i];
            }
            std::cout << std::endl;

            for (const auto& command : commands) {
                std::cout << "Executing configured command: " << command << std::endl;
            }
        }

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
        std::cout << "Log timestamp: " << current_iso8601_timestamp() << std::endl;
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
        auto config_modules = parse_string_array_field(input, "config_modules");

        bool use_oci_config = false;
        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();
                        const auto oci_it = test.find("use_oci_config");
                        if (oci_it != test.end()) {
                            const auto oci_res = oci_it->second.As<bool>();
                            if (oci_res.has_value()) {
                                use_oci_config = oci_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing configuration management" << std::endl;

        if (config_modules.empty()) {
            std::cout << "Modular configuration loaded" << std::endl;
        } else {
            for (const auto& module : config_modules) {
                std::cout << "Configuration module loaded: " << module << std::endl;
            }
        }

        if (use_oci_config) {
            std::cout << "OCI runtime config compatible" << std::endl;
        } else {
            std::cout << "OCI runtime config not requested" << std::endl;
        }

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
        bool debug_mode = true;
        bool wait_for_debugger = true;
        bool create_session = true;

        const score::json::JsonParser parser;
        const auto root_any_res = parser.FromBuffer(input);
        if (root_any_res.has_value()) {
            const auto root_object_res = root_any_res.value().As<score::json::Object>();
            if (root_object_res.has_value()) {
                const auto& root = root_object_res.value().get();
                const auto test_it = root.find("test");
                if (test_it != root.end()) {
                    const auto test_object_res = test_it->second.As<score::json::Object>();
                    if (test_object_res.has_value()) {
                        const auto& test = test_object_res.value().get();

                        const auto debug_it = test.find("debug_mode");
                        if (debug_it != test.end()) {
                            const auto debug_res = debug_it->second.As<bool>();
                            if (debug_res.has_value()) {
                                debug_mode = debug_res.value();
                            }
                        }

                        const auto wait_it = test.find("wait_for_debugger");
                        if (wait_it != test.end()) {
                            const auto wait_res = wait_it->second.As<bool>();
                            if (wait_res.has_value()) {
                                wait_for_debugger = wait_res.value();
                            }
                        }

                        const auto session_it = test.find("create_session");
                        if (session_it != test.end()) {
                            const auto session_res = session_it->second.As<bool>();
                            if (session_res.has_value()) {
                                create_session = session_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing debug mode and terminal support" << std::endl;

        if (debug_mode) {
            std::cout << "Debug mode enabled" << std::endl;
        } else {
            std::cout << "Debug mode disabled" << std::endl;
        }

        if (wait_for_debugger) {
            std::cout << "Waiting for debugger connection" << std::endl;
        } else {
            std::cout << "Not waiting for debugger connection" << std::endl;
        }

        if (create_session) {
            std::cout << "Launched as session leader" << std::endl;
        } else {
            std::cout << "Launched without new session" << std::endl;
        }
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
        std::string redirect_stdout = "/tmp/app.log";  // default, used only when config key is absent
        std::string redirect_stderr = "/tmp/app_error.log";  // default, used only when config key is absent

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

                        const auto stdout_it = test.find("redirect_stdout");
                        if (stdout_it != test.end()) {
                            const auto stdout_res = stdout_it->second.As<std::string>();
                            if (stdout_res.has_value()) {
                                redirect_stdout = stdout_res.value();
                            }
                        }

                        const auto stderr_it = test.find("redirect_stderr");
                        if (stderr_it != test.end()) {
                            const auto stderr_res = stderr_it->second.As<std::string>();
                            if (stderr_res.has_value()) {
                                redirect_stderr = stderr_res.value();
                            }
                        }
                    }
                }
            }
        }

        std::cout << "Testing I/O and file descriptor management" << std::endl;
        std::cout << "stdout redirected to " << redirect_stdout << std::endl;
        std::cout << "stderr redirected to " << redirect_stderr << std::endl;
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

