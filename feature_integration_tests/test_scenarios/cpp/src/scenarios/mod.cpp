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

#include <scenario.hpp>

#include <vector>

Scenario::Ptr make_multiple_kvs_per_app_scenario();
Scenario::Ptr make_default_values_ignored_scenario();
Scenario::Ptr make_reset_to_default_scenario();
Scenario::Ptr make_utf8_defaults_scenario();
Scenario::Ptr make_utf8_default_value_get_scenario();
Scenario::Ptr make_multi_instance_isolation_scenario();
Scenario::Ptr make_lifecycle_application_if_scenario();
Scenario::Ptr make_lifecycle_baselibs_integration_scenario();
Scenario::Ptr make_lifecycle_comm_dependency_activation_scenario();
Scenario::Ptr make_lifecycle_config_validation_gate_scenario();
Scenario::Ptr make_lifecycle_ipc_alive_if_scenario();
Scenario::Ptr make_lifecycle_ipc_controlif_scenario();
Scenario::Ptr make_lifecycle_ipc_deadline_monitor_if_scenario();
Scenario::Ptr make_lifecycle_logging_correlation_scenario();
Scenario::Ptr make_lifecycle_multi_instance_isolation_scenario();
Scenario::Ptr make_lifecycle_orchestrator_sync_scenario();
Scenario::Ptr make_lifecycle_security_isolation_scenario();
Scenario::Ptr make_lifecycle_time_sync_scenario();
ScenarioGroup::Ptr supported_datatypes_group();
ScenarioGroup::Ptr default_values_group();

ScenarioGroup::Ptr lifecycle_scenario_group() {
    return std::make_shared<ScenarioGroupImpl>(
        "lifecycle",
        std::vector<Scenario::Ptr>{
            make_lifecycle_application_if_scenario(),
            make_lifecycle_baselibs_integration_scenario(),
            make_lifecycle_comm_dependency_activation_scenario(),
            make_lifecycle_config_validation_gate_scenario(),
            make_lifecycle_ipc_alive_if_scenario(),
            make_lifecycle_ipc_controlif_scenario(),
            make_lifecycle_ipc_deadline_monitor_if_scenario(),
            make_lifecycle_logging_correlation_scenario(),
            make_lifecycle_multi_instance_isolation_scenario(),
            make_lifecycle_orchestrator_sync_scenario(),
            make_lifecycle_security_isolation_scenario(),
            make_lifecycle_time_sync_scenario(),
        },
        std::vector<ScenarioGroup::Ptr>{});
}

ScenarioGroup::Ptr persistency_scenario_group() {
    return std::make_shared<ScenarioGroupImpl>(
        "persistency",
        std::vector<Scenario::Ptr>{
            make_multiple_kvs_per_app_scenario(),
            make_default_values_ignored_scenario(),
            make_reset_to_default_scenario(),
            make_utf8_defaults_scenario(),
            make_utf8_default_value_get_scenario(),
            make_multi_instance_isolation_scenario(),
        },
        std::vector<ScenarioGroup::Ptr>{supported_datatypes_group(), default_values_group()});
}

ScenarioGroup::Ptr root_scenario_group() {
    return std::make_shared<ScenarioGroupImpl>(
        "root",
        std::vector<Scenario::Ptr>{},
        std::vector<ScenarioGroup::Ptr>{lifecycle_scenario_group(), persistency_scenario_group()});
}
