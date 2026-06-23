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

/**
 * @brief Create ControlInterfaceSupport scenario.
 */
Scenario::Ptr make_control_interface_support_scenario();

/**
 * @brief Create ProcessArguments scenario.
 */
Scenario::Ptr make_process_arguments_scenario();

/**
 * @brief Create ProcessSecurity scenario.
 */
Scenario::Ptr make_process_security_scenario();

/**
 * @brief Create ProcessResources scenario.
 */
Scenario::Ptr make_process_resources_scenario();

/**
 * @brief Create ConditionalLaunching scenario.
 */
Scenario::Ptr make_conditional_launching_scenario();

/**
 * @brief Create ProcessManagement scenario.
 */
Scenario::Ptr make_process_management_scenario();

/**
 * @brief Create RunTargets scenario.
 */
Scenario::Ptr make_run_targets_scenario();

/**
 * @brief Create ProcessTermination scenario.
 */
Scenario::Ptr make_process_termination_scenario();

/**
 * @brief Create MonitoringAndRecovery scenario.
 */
Scenario::Ptr make_monitoring_and_recovery_scenario();

/**
 * @brief Create ControlInterfaceCommands scenario.
 */
Scenario::Ptr make_control_interface_commands_scenario();

/**
 * @brief Create LoggingSupport scenario.
 */
Scenario::Ptr make_logging_support_scenario();

/**
 * @brief Create ConfigurationManagement scenario.
 */
Scenario::Ptr make_configuration_management_scenario();

/**
 * @brief Create DebugAndTerminal scenario.
 */
Scenario::Ptr make_debug_and_terminal_scenario();

/**
 * @brief Create IOAndFileDescriptors scenario.
 */
Scenario::Ptr make_io_and_file_descriptors_scenario();

