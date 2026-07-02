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

mod application_if;
mod baselibs_integration;
mod comm_dependency_activation;
mod config_validation_gate;
mod ipc_alive_if;
mod ipc_controlif;
mod ipc_deadline_monitor_if;
mod logging_correlation;
mod multi_instance_isolation;
mod orchestrator_sync;
mod security_isolation;
mod time_sync;

use application_if::ApplicationInterfaceScenario;
use baselibs_integration::BaselibsIntegrationScenario;
use comm_dependency_activation::CommDependencyActivationScenario;
use config_validation_gate::ConfigValidationGateScenario;
use ipc_alive_if::IpcAliveInterfaceScenario;
use ipc_controlif::IpcControlInterfaceScenario;
use ipc_deadline_monitor_if::IpcDeadlineMonitorInterfaceScenario;
use logging_correlation::LoggingCorrelationScenario;
use multi_instance_isolation::MultiInstanceIsolationScenario;
use orchestrator_sync::OrchestratorSyncScenario;
use security_isolation::SecurityIsolationScenario;
use test_scenarios_rust::scenario::{ScenarioGroup, ScenarioGroupImpl};
use time_sync::TimeSyncScenario;

pub fn lifecycle_group() -> Box<dyn ScenarioGroup> {
    Box::new(ScenarioGroupImpl::new(
        "lifecycle",
        vec![
            Box::new(ApplicationInterfaceScenario),
            Box::new(BaselibsIntegrationScenario),
            Box::new(CommDependencyActivationScenario),
            Box::new(ConfigValidationGateScenario),
            Box::new(IpcAliveInterfaceScenario),
            Box::new(IpcControlInterfaceScenario),
            Box::new(IpcDeadlineMonitorInterfaceScenario),
            Box::new(LoggingCorrelationScenario),
            Box::new(MultiInstanceIsolationScenario),
            Box::new(OrchestratorSyncScenario),
            Box::new(SecurityIsolationScenario),
            Box::new(TimeSyncScenario),
        ],
        vec![],
    ))
}
