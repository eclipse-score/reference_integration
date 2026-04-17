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

#include "framework/scenario_framework.h"

#include <iostream>
#include <string>

ScenarioRegistry create_scenario_registry();

namespace {

void print_help() {
    std::cout << "Test scenario runner" << std::endl;
    std::cout << "'-n', '--name' - test scenario name" << std::endl;
    std::cout << "'-i', '--input' - test scenario input" << std::endl;
    std::cout << "'-l', '--list-scenarios' - list available scenarios" << std::endl;
    std::cout << "'-h', '--help' - show help" << std::endl;
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        const ScenarioRegistry scenarios = create_scenario_registry();

        std::string scenario_name;
        std::string json_input;
        bool list_scenarios = false;
        bool show_help = false;

        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "-l" || arg == "--list-scenarios") {
                list_scenarios = true;
                continue;
            }
            if (arg == "-h" || arg == "--help") {
                show_help = true;
                continue;
            }
            if (arg == "-n" || arg == "--name") {
                if (i + 1 >= argc) {
                    std::cerr << "Missing value for " << arg << std::endl;
                    return 1;
                }
                scenario_name = argv[++i];
                continue;
            }
            if (arg == "-i" || arg == "--input") {
                if (i + 1 >= argc) {
                    std::cerr << "Missing value for " << arg << std::endl;
                    return 1;
                }
                json_input = argv[++i];
                continue;
            }

            std::cerr << "Unknown argument provided: " << arg << std::endl;
            return 1;
        }

        if (show_help) {
            print_help();
            return 0;
        }

        if (list_scenarios) {
            for (const auto& [name, _] : scenarios) {
                std::cout << name << std::endl;
            }
            return 0;
        }

        if (scenario_name.empty() || json_input.empty()) {
            std::cerr << "Scenario name and input are required." << std::endl;
            print_help();
            return 1;
        }

        // Find and run scenario
        auto it = scenarios.find(scenario_name);
        if (it == scenarios.end()) {
            std::cerr << "Unknown scenario: " << scenario_name << std::endl;
            return 1;
        }

        return it->second->run(json_input);

    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }
}
