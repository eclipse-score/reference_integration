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

#include <iostream>
#include <vector>

#include <cli.hpp>
#include <scenario.hpp>
#include <test_context.hpp>

ScenarioGroup::Ptr root_scenario_group();

int main(int argc, char* argv[]) {
    try {
        std::vector<std::string> raw_arguments{argv, argv + argc};
        TestContext test_context{root_scenario_group()};
        run_cli_app(raw_arguments, test_context);
        return 0;

    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        // Match Rust panic return code.
        return 101;
    }
}
