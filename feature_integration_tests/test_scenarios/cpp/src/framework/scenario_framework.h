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

#ifndef TEST_SCENARIOS_CPP_SRC_FRAMEWORK_SCENARIO_FRAMEWORK_H_
#define TEST_SCENARIOS_CPP_SRC_FRAMEWORK_SCENARIO_FRAMEWORK_H_

#include <map>
#include <memory>
#include <string>
#include <vector>

class Scenario {
public:
    virtual ~Scenario() = default;
    virtual std::string name() const = 0;
    virtual int run(const std::string& input) = 0;
};

class ScenarioGroup {
public:
    explicit ScenarioGroup(std::string name)
        : name_(std::move(name)) {}

    void add_scenario(const std::string& name, std::shared_ptr<Scenario> scenario) {
        scenarios_[name] = std::move(scenario);
    }

    void add_group(std::shared_ptr<ScenarioGroup> group) {
        groups_.push_back(std::move(group));
    }

    const std::string& name() const { return name_; }
    const std::map<std::string, std::shared_ptr<Scenario>>& scenarios() const { return scenarios_; }
    const std::vector<std::shared_ptr<ScenarioGroup>>& groups() const { return groups_; }

private:
    std::string name_;
    std::map<std::string, std::shared_ptr<Scenario>> scenarios_;
    std::vector<std::shared_ptr<ScenarioGroup>> groups_;
};

using ScenarioRegistry = std::map<std::string, std::shared_ptr<Scenario>>;

inline void collect_scenarios_recursive(const ScenarioGroup& group,
                                        ScenarioRegistry& out,
                                        const std::string& prefix = "") {
    std::string next_prefix = prefix;
    if (group.name() != "root") {
        next_prefix = prefix.empty() ? group.name() : (prefix + "." + group.name());
    }

    for (const auto& [scenario_name, scenario] : group.scenarios()) {
        const std::string full_name = next_prefix.empty() ? scenario_name : (next_prefix + "." + scenario_name);
        out[full_name] = scenario;
    }

    for (const auto& subgroup : group.groups()) {
        collect_scenarios_recursive(*subgroup, out, next_prefix);
    }
}

#endif  // TEST_SCENARIOS_CPP_SRC_FRAMEWORK_SCENARIO_FRAMEWORK_H_
