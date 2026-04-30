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

#include "../../internals/persistency/kvs_instance.h"
#include "kvs_build_helpers.h"

#include <scenario.hpp>

#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace score::mw::per::kvs;
using kvs_build_helpers::create_kvs;

namespace {

/// Write all nine value types under ASCII key names in a single flush.
/// Python reads the snapshot and verifies every key is present with the correct
/// type tag and value — proving that primitive and composite types coexist
/// without interference in one atomic storage outcome.
/// Combines feat_req__persistency__support_datatype_value,
/// feat_req__persistency__support_datatype_keys, and
/// feat_req__persistency__store_data.
class AllValueTypes : public Scenario {
public:
    std::string name() const final { return "all_value_types"; }

    void run(const std::string& input) const final {
        KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");
        Kvs kvs = create_kvs(params);

        std::unordered_map<std::string, KvsValue> nested_obj = {{"sub-number", KvsValue(789.0)}};
        std::vector<KvsValue> arr = {
            KvsValue(321.5), KvsValue(false), KvsValue("hello"),
            KvsValue(nullptr), KvsValue(std::vector<KvsValue>{}), KvsValue(nested_obj),
        };

        auto check = [](auto result, const std::string& key) {
            if (!result) {
                throw std::runtime_error("Failed to set value for key: " + key);
            }
        };

        check(kvs.set_value("i32_key", KvsValue(static_cast<int32_t>(-321))), "i32_key");
        check(kvs.set_value("u32_key", KvsValue(static_cast<uint32_t>(1234))), "u32_key");
        check(kvs.set_value("i64_key", KvsValue(static_cast<int64_t>(-123456789))), "i64_key");
        check(kvs.set_value("u64_key", KvsValue(static_cast<uint64_t>(123456789))), "u64_key");
        check(kvs.set_value("f64_key", KvsValue(-5432.1)), "f64_key");
        check(kvs.set_value("bool_key", KvsValue(true)), "bool_key");
        check(kvs.set_value("str_key", KvsValue("example")), "str_key");
        check(kvs.set_value("arr_key", KvsValue(arr)), "arr_key");
        check(kvs.set_value("obj_key", KvsValue(nested_obj)), "obj_key");

        if (!kvs.flush()) {
            throw std::runtime_error("Failed to flush");
        }
        KvsInstance::normalize_snapshot_file_to_rust_envelope(params);
    }
};

/// Write five values with mixed types under both ASCII and UTF-8 key names,
/// then flush and normalize. Python reads the single snapshot and verifies
/// every key is present with the correct type tag and value.
class AllTypesUtf8 : public Scenario {
public:
    std::string name() const final {
        return "all_types_utf8";
    }

    void run(const std::string& input) const final {
        KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");
        Kvs kvs = create_kvs(params);

        auto check = [](auto result, const std::string& key) {
            if (!result) {
                throw std::runtime_error("Failed to set value for key: " + key);
            }
        };

        check(kvs.set_value("ascii_i32", KvsValue(static_cast<int32_t>(-321))), "ascii_i32");
        check(kvs.set_value(u8"emoji_f64 🎯", KvsValue(3.14)), u8"emoji_f64 🎯");
        check(kvs.set_value(u8"greek_bool αβγ", KvsValue(true)), u8"greek_bool αβγ");
        check(kvs.set_value("ascii_str", KvsValue("hello")), "ascii_str");
        check(kvs.set_value("ascii_null", KvsValue(nullptr)), "ascii_null");

        if (!kvs.flush()) {
            throw std::runtime_error("Failed to flush");
        }

        KvsInstance::normalize_snapshot_file_to_rust_envelope(params);
    }
};

}  // namespace

ScenarioGroup::Ptr supported_datatypes_group() {
    std::vector<Scenario::Ptr> scenarios = {
        std::make_shared<AllValueTypes>(),
        std::make_shared<AllTypesUtf8>(),
    };
    return std::make_shared<ScenarioGroupImpl>(
        "supported_datatypes", scenarios, std::vector<ScenarioGroup::Ptr>{});
}
