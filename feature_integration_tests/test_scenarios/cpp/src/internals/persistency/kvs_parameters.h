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

#ifndef INTERNALS_PERSISTENCY_KVS_PARAMETERS_H_
#define INTERNALS_PERSISTENCY_KVS_PARAMETERS_H_

#include <optional>
#include <cstdint>
#include <string>

// Enum for KVS defaults mode
enum class KvsDefaults {
    Ignored,
    Optional,
    Required,
};

// Enum for KVS load mode
enum class KvsLoad {
    Ignored,
    Optional,
    Required,
};

// Instance ID wrapper
struct InstanceId {
    uint32_t value;
    
    explicit InstanceId(uint32_t v = 0) : value(v) {}
    
    std::string to_string() const {
        return "InstanceId(" + std::to_string(value) + ")";
    }
};

// KVS parameters parsed from JSON
struct KvsParameters {
    InstanceId instance_id;
    std::optional<KvsDefaults> defaults;
    std::optional<KvsLoad> kvs_load;
    std::optional<std::string> dir;
    std::optional<int> snapshot_max_count;

    // Parse from full scenario input by section name (e.g. "kvs_parameters_1").
    static KvsParameters from_json_section(const std::string& input, const std::string& section_name);
};

#endif // INTERNALS_PERSISTENCY_KVS_PARAMETERS_H_
