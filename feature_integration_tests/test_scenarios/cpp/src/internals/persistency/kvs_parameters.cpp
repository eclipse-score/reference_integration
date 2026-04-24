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

#include "kvs_parameters.h"

#include "score/json/json_parser.h"

#include <stdexcept>

namespace {
KvsDefaults parse_kvs_defaults(const std::string& str) {
    if (str == "ignored") return KvsDefaults::Ignored;
    if (str == "optional") return KvsDefaults::Optional;
    if (str == "required") return KvsDefaults::Required;
    throw std::invalid_argument("Invalid KvsDefaults mode: " + str);
}

KvsLoad parse_kvs_load(const std::string& str) {
    if (str == "ignored") return KvsLoad::Ignored;
    if (str == "optional") return KvsLoad::Optional;
    if (str == "required") return KvsLoad::Required;
    throw std::invalid_argument("Invalid KvsLoad mode: " + str);
}

const score::json::Object& expect_object(const score::json::Any& value, const std::string& field_name) {
    const auto object_res = value.As<score::json::Object>();
    if (!object_res.has_value()) {
        throw std::invalid_argument("Expected object field: " + field_name);
    }
    return object_res.value().get();
}

}  // namespace

KvsParameters KvsParameters::from_json_section(const std::string& input, const std::string& section_name) {
    KvsParameters params;

    const score::json::JsonParser parser;
    const auto root_any_res = parser.FromBuffer(input);
    if (!root_any_res.has_value()) {
        throw std::invalid_argument("Failed to parse scenario input JSON");
    }

    const auto root_object_res = root_any_res.value().As<score::json::Object>();
    if (!root_object_res.has_value()) {
        throw std::invalid_argument("Scenario input root must be a JSON object");
    }

    const auto& root = root_object_res.value().get();
    const auto section_it = root.find(section_name);
    if (section_it == root.end()) {
        throw std::invalid_argument("Missing section: " + section_name);
    }

    const score::json::Object* parsed_section = &expect_object(section_it->second, section_name);
    const auto nested_parameters_it = parsed_section->find("kvs_parameters");
    if (nested_parameters_it != parsed_section->end()) {
        parsed_section = &expect_object(nested_parameters_it->second, "kvs_parameters");
    }

    const auto instance_it = parsed_section->find("instance_id");
    if (instance_it == parsed_section->end()) {
        throw std::invalid_argument("Missing instance_id in section: " + section_name);
    }
    const auto instance_res = instance_it->second.As<std::int64_t>();
    if (!instance_res.has_value()) {
        throw std::invalid_argument("Invalid instance_id in section: " + section_name);
    }
    params.instance_id = InstanceId(static_cast<uint32_t>(instance_res.value()));

    if (const auto defaults_it = parsed_section->find("defaults"); defaults_it != parsed_section->end()) {
        const auto defaults_res = defaults_it->second.As<std::string_view>();
        if (defaults_res.has_value()) {
            params.defaults = parse_kvs_defaults(std::string(defaults_res.value()));
        }
    }

    if (const auto load_it = parsed_section->find("kvs_load"); load_it != parsed_section->end()) {
        const auto load_res = load_it->second.As<std::string_view>();
        if (load_res.has_value()) {
            params.kvs_load = parse_kvs_load(std::string(load_res.value()));
        }
    }

    if (const auto dir_it = parsed_section->find("dir"); dir_it != parsed_section->end()) {
        const auto dir_res = dir_it->second.As<std::string_view>();
        if (dir_res.has_value()) {
            params.dir = std::string(dir_res.value());
        }
    }

    if (const auto snapshot_it = parsed_section->find("snapshot_max_count"); snapshot_it != parsed_section->end()) {
        const auto snapshot_res = snapshot_it->second.As<std::int64_t>();
        if (snapshot_res.has_value()) {
            params.snapshot_max_count = static_cast<int>(snapshot_res.value());
        }
    }

    return params;
}
