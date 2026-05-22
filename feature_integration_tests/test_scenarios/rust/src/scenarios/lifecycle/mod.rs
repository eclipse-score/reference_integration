// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// <https://www.apache.org/licenses/LICENSE-2.0>
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************
mod launch_manager_support;

use launch_manager_support::{
    ConditionalLaunching, ConfigurationManagement, ControlInterfaceCommands, ControlInterfaceSupport, DebugAndTerminal,
    DependencyOrdering, IOAndFileDescriptors, LoggingSupport, MonitoringAndRecovery, ParallelLaunching,
    ProcessArguments, ProcessLaunchingSupport, ProcessManagement, ProcessResources, ProcessSecurity,
    ProcessTermination, RunTargets,
};
use test_scenarios_rust::scenario::{ScenarioGroup, ScenarioGroupImpl};

pub fn lifecycle_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "lifecycle",
        vec![
            Box::new(ProcessLaunchingSupport),
            Box::new(DependencyOrdering),
            Box::new(ParallelLaunching),
            Box::new(ControlInterfaceSupport),
            Box::new(ProcessArguments),
            Box::new(ProcessSecurity),
            Box::new(ProcessResources),
            Box::new(ConditionalLaunching),
            Box::new(ProcessManagement),
            Box::new(RunTargets),
            Box::new(ProcessTermination),
            Box::new(MonitoringAndRecovery),
            Box::new(ControlInterfaceCommands),
            Box::new(LoggingSupport),
            Box::new(ConfigurationManagement),
            Box::new(DebugAndTerminal),
            Box::new(IOAndFileDescriptors),
        ],
        vec![],
    ))
}
