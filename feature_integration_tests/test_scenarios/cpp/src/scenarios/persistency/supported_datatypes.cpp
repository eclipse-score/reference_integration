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

#include "../../internals/persistency/kvs_parameters.h"

#include "tracing.hpp"

#include <kvs.hpp>
#include <kvsbuilder.hpp>
#include <scenario.hpp>

#include <iomanip>
#include <memory>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

using namespace score::mw::per::kvs;

namespace {
const std::string kTargetName{"cpp_test_scenarios::scenarios::persistency::supported_datatypes"};

std::optional<bool> to_need_flag(const std::optional<KvsDefaults>& mode) {
    if (!mode.has_value()) {
        return std::nullopt;
    }
    if (*mode == KvsDefaults::Required) {
        return true;
    }
    return false;
}

std::optional<bool> to_need_flag(const std::optional<KvsLoad>& mode) {
    if (!mode.has_value()) {
        return std::nullopt;
    }
    if (*mode == KvsLoad::Required) {
        return true;
    }
    return false;
}

Kvs create_kvs(const KvsParameters& params) {
    KvsBuilder builder{score::mw::per::kvs::InstanceId{params.instance_id.value}};

    if (const auto defaults = to_need_flag(params.defaults)) {
        builder = builder.need_defaults_flag(*defaults);
    }
    if (const auto kvs_load = to_need_flag(params.kvs_load)) {
        builder = builder.need_kvs_flag(*kvs_load);
    }
    if (params.dir.has_value()) {
        builder = builder.dir(std::string(*params.dir));
    }

    auto build_result = builder.build();
    if (!build_result) {
        throw std::runtime_error(std::string(build_result.error().Message()));
    }

    return std::move(build_result.value());
}

void log_key(const std::string& keyname) {
    TRACING_INFO(kTargetName, std::pair{std::string{"key"}, keyname});
}

void log_key_value(const std::string& keyname, const std::string& value_json) {
    TRACING_INFO(kTargetName,
                 std::pair{std::string{"key"}, keyname},
                 std::pair{std::string{"value"}, value_json});
}

class SupportedDatatypesKeys : public Scenario {
public:
    std::string name() const final {
        return "keys";
    }

    void run(const std::string& input) const final {
        KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");
        Kvs kvs = create_kvs(params);

        std::vector<std::string> keys_to_check = {
            "example",
            u8"emoji ✅❗😀",
            u8"greek ημα",
        };
        for (const auto& key : keys_to_check) {
            auto set_result = kvs.set_value(key, KvsValue(nullptr));
            if (!set_result) {
                throw std::runtime_error("Failed to set value");
            }
        }

        auto keys_in_kvs = kvs.get_all_keys();
        if (!keys_in_kvs) {
            throw std::runtime_error(std::string(keys_in_kvs.error().Message()));
        }
        for (const auto& key : keys_in_kvs.value()) {
            log_key(key);
        }
    }
};

class SupportedDatatypesValues : public Scenario {
private:
    KvsValue value;

    static std::string kvs_value_to_string(const KvsValue& v) {
        switch (v.getType()) {
            case KvsValue::Type::i32:
                return std::to_string(std::get<int32_t>(v.getValue()));
            case KvsValue::Type::u32:
                return std::to_string(std::get<uint32_t>(v.getValue()));
            case KvsValue::Type::i64:
                return std::to_string(std::get<int64_t>(v.getValue()));
            case KvsValue::Type::u64:
                return std::to_string(std::get<uint64_t>(v.getValue()));
            case KvsValue::Type::f64: {
                auto val = std::get<double>(v.getValue());
                std::ostringstream oss;
                oss << std::setprecision(15) << val;
                std::string s = oss.str();
                if (auto dot = s.find('.'); dot != std::string::npos) {
                    auto last_nonzero = s.find_last_not_of('0');
                    if (last_nonzero != std::string::npos && last_nonzero > dot) {
                        s.erase(last_nonzero + 1);
                    }
                    if (!s.empty() && s.back() == '.') {
                        s.pop_back();
                    }
                }
                return s;
            }
            case KvsValue::Type::Boolean:
                return std::get<bool>(v.getValue()) ? "true" : "false";
            case KvsValue::Type::String:
                return "\"" + std::get<std::string>(v.getValue()) + "\"";
            case KvsValue::Type::Null:
                return "null";
            case KvsValue::Type::Array: {
                const auto& arr = std::get<std::vector<std::shared_ptr<KvsValue>>>(v.getValue());
                std::string json = "[";
                for (size_t i = 0; i < arr.size(); ++i) {
                    const auto& elem = *arr[i];
                    json += "{\"t\":\"" + SupportedDatatypesValues(elem).name() +
                            "\",\"v\":" + kvs_value_to_string(elem) + "}";
                    if (i + 1 < arr.size()) {
                        json += ",";
                    }
                }
                json += "]";
                return json;
            }
            case KvsValue::Type::Object: {
                const auto& obj = std::get<std::unordered_map<std::string, std::shared_ptr<KvsValue>>>(v.getValue());
                std::string json = "{";
                size_t count = 0;
                for (const auto& kv : obj) {
                    const auto& elem = *kv.second;
                    json += "\"" + kv.first + "\":{\"t\":\"" + SupportedDatatypesValues(elem).name() +
                            "\",\"v\":" + kvs_value_to_string(elem) + "}";
                    if (++count < obj.size()) {
                        json += ",";
                    }
                }
                json += "}";
                return json;
            }
            default:
                return "null";
        }
    }

public:
    explicit SupportedDatatypesValues(const KvsValue& v) : value(v) {}

    std::string name() const final {
        switch (value.getType()) {
            case KvsValue::Type::i32:
                return "i32";
            case KvsValue::Type::u32:
                return "u32";
            case KvsValue::Type::i64:
                return "i64";
            case KvsValue::Type::u64:
                return "u64";
            case KvsValue::Type::f64:
                return "f64";
            case KvsValue::Type::Boolean:
                return "bool";
            case KvsValue::Type::String:
                return "str";
            case KvsValue::Type::Null:
                return "null";
            case KvsValue::Type::Array:
                return "arr";
            case KvsValue::Type::Object:
                return "obj";
            default:
                return "unknown";
        }
    }

    void run(const std::string& input) const final {
        KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");
        Kvs kvs = create_kvs(params);

        auto set_result = kvs.set_value(name(), value);
        if (!set_result) {
            throw std::runtime_error("Failed to set value");
        }

        auto kvs_value = kvs.get_value(name());
        if (!kvs_value) {
            throw std::runtime_error(std::string(kvs_value.error().Message()));
        }

        std::string json_value = "{\"t\":\"" + name() + "\",\"v\":" +
                                 kvs_value_to_string(kvs_value.value()) + "}";
        log_key_value(name(), json_value);
    }

    static Scenario::Ptr supported_datatypes_i32() {
        return std::make_shared<SupportedDatatypesValues>(KvsValue(static_cast<int32_t>(-321)));
    }

    static Scenario::Ptr supported_datatypes_u32() {
        return std::make_shared<SupportedDatatypesValues>(KvsValue(static_cast<uint32_t>(1234)));
    }

    static Scenario::Ptr supported_datatypes_i64() {
        return std::make_shared<SupportedDatatypesValues>(KvsValue(static_cast<int64_t>(-123456789)));
    }

    static Scenario::Ptr supported_datatypes_u64() {
        return std::make_shared<SupportedDatatypesValues>(KvsValue(static_cast<uint64_t>(123456789)));
    }

    static Scenario::Ptr supported_datatypes_f64() {
        return std::make_shared<SupportedDatatypesValues>(KvsValue(-5432.1));
    }

    static Scenario::Ptr supported_datatypes_bool() {
        return std::make_shared<SupportedDatatypesValues>(KvsValue(true));
    }

    static Scenario::Ptr supported_datatypes_string() {
        return std::make_shared<SupportedDatatypesValues>(KvsValue("example"));
    }

    static Scenario::Ptr supported_datatypes_array() {
        std::unordered_map<std::string, KvsValue> obj = {{"sub-number", KvsValue(789.0)}};
        std::vector<KvsValue> arr = std::vector<KvsValue>{KvsValue(321.5),
                                                          KvsValue(false),
                                                          KvsValue("hello"),
                                                          KvsValue(nullptr),
                                                          KvsValue(std::vector<KvsValue>{}),
                                                          KvsValue(obj)};
        return std::make_shared<SupportedDatatypesValues>(KvsValue(arr));
    }

    static Scenario::Ptr supported_datatypes_object() {
        std::unordered_map<std::string, KvsValue> obj = {{"sub-number", KvsValue(789.0)}};
        return std::make_shared<SupportedDatatypesValues>(KvsValue(obj));
    }

    static ScenarioGroup::Ptr value_types_group() {
        std::vector<Scenario::Ptr> scenarios = {supported_datatypes_i32(),
                                                supported_datatypes_u32(),
                                                supported_datatypes_i64(),
                                                supported_datatypes_u64(),
                                                supported_datatypes_f64(),
                                                supported_datatypes_bool(),
                                                supported_datatypes_string(),
                                                supported_datatypes_array(),
                                                supported_datatypes_object()};
        return std::make_shared<ScenarioGroupImpl>("values", scenarios, std::vector<ScenarioGroup::Ptr>{});
    }
};

}  // namespace

ScenarioGroup::Ptr supported_datatypes_group() {
    std::vector<Scenario::Ptr> keys = {std::make_shared<SupportedDatatypesKeys>()};
    std::vector<ScenarioGroup::Ptr> groups = {SupportedDatatypesValues::value_types_group()};
    return std::make_shared<ScenarioGroupImpl>("supported_datatypes", keys, groups);
}

