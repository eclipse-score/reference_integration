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

/**
 * @file launch_manager_support.h
 * @brief Lifecycle integration test scenarios using real C++ lifecycle and health monitoring APIs.
 *
 * These scenarios test that applications can properly integrate with the lifecycle
 * framework by using the lifecycle client and health monitoring libraries.
 */

#pragma once

#include <scenario.hpp>

/**
 * @brief Create ProcessLaunchingSupport scenario.
 *
 * Tests that an application can report execution state to the Launch Manager.
 * This verifies the basic integration point that enables Launch Manager to
 * monitor and manage application lifecycle.
 */
Scenario::Ptr make_process_launching_support_scenario();

/**
 * @brief Create DependencyOrdering scenario.
 *
 * Tests health monitoring with sequential deadline reporting.
 * This demonstrates ordered deadline transitions that could be used
 * by Launch Manager to verify proper application startup sequences.
 */
Scenario::Ptr make_dependency_ordering_scenario();

/**
 * @brief Create ParallelLaunching scenario.
 *
 * Tests parallel health monitoring with multiple independent monitors.
 * This demonstrates that multiple independent monitoring contexts can run
 * simultaneously, supporting parallel application execution scenarios.
 */
Scenario::Ptr make_parallel_launching_scenario();
