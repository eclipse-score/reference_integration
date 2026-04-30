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
#include "../../internals/persistency/kvs_parameters.h"

#include <kvs.hpp>
#include <kvsbuilder.hpp>
#include <scenario.hpp>

#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace score::mw::per::kvs;

namespace {

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

/// Set a value and flush. Python reads the snapshot bytes and the hash file,
/// verifying adler32(snapshot) matches the hash written by KVS.
/// NOTE: normalize is NOT called here so the hash file remains consistent
/// with the snapshot bytes (both are in the C++ KVS native format).
class Checksum final : public Scenario {
public:
    std::string name() const final { return "checksum"; }

    void run(const std::string& input) const final {
        auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
        auto kvs{create_kvs(params)};

        auto set_result{kvs.set_value("checksum_test_key", KvsValue{1.0})};
        if (!set_result) {
            throw std::runtime_error{"Failed to set value"};
        }

        auto flush_result{kvs.flush()};
        if (!flush_result) {
            throw std::runtime_error{"Failed to flush"};
        }
        // Do NOT normalize: the hash file must match the snapshot bytes.
    }
};

/// Open KVS with three default keys, override ONLY the middle key, flush.
/// Python verifies the snapshot contains exactly the one overridden key
/// while the other two keys are absent (never explicitly written).
/// Combines default_values + default_value_file + store_data requirements.
class PartialOverride final : public Scenario {
public:
    std::string name() const final { return "partial_override"; }

    void run(const std::string& input) const final {
        auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};

        auto kvs_opt{KvsInstance::create(params)};
        if (!kvs_opt) {
            throw std::runtime_error{"Failed to create KVS instance for PartialOverride"};
        }
        auto kvs{*kvs_opt};

        // Override only the middle key; partial_key_0 and partial_key_2 stay as defaults.
        if (!kvs->set_value("partial_key_1", 999.0)) {
            throw std::runtime_error{"Failed to set value"};
        }

        if (!kvs->flush()) {
            throw std::runtime_error{"Failed to flush"};
        }

        // Log default values for key_0 and key_2 so Python can assert they are accessible.
        auto val0{kvs->get_value_f64("partial_key_0")};
        if (!val0.has_value()) {
            throw std::runtime_error{"Failed to read default value for 'partial_key_0'"};
        }
        auto val2{kvs->get_value_f64("partial_key_2")};
        if (!val2.has_value()) {
            throw std::runtime_error{"Failed to read default value for 'partial_key_2'"};
        }
        std::cout << "default key=partial_key_0 value=" << val0.value() << "\n";
        std::cout << "default key=partial_key_2 value=" << val2.value() << "\n";

        KvsInstance::normalize_snapshot_file_to_rust_envelope(params);
    }
};

/// Open KVS with a defaults file containing one key. Call get_value on that key
/// without ever calling set_value, write the retrieved value to a probe key, flush.
/// Python verifies the probe key equals the expected default, confirming that
/// feat_req__persistency__default_value_get is satisfied.
class GetDefaultValue final : public Scenario {
public:
    std::string name() const final { return "get_default_value"; }

    void run(const std::string& input) const final {
        auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};

        auto kvs_opt{KvsInstance::create(params)};
        if (!kvs_opt) {
            throw std::runtime_error{"Failed to create KVS instance"};
        }
        auto kvs{*kvs_opt};

        // Read the default — this key has a default value but was never explicitly set.
        auto default_result{kvs->get_value_f64("default_probe_key")};
        if (!default_result.has_value()) {
            throw std::runtime_error{"Failed to read default value for 'default_probe_key'"};
        }

        // Persist the retrieved value to a probe key so Python can verify it.
        if (!kvs->set_value("result_key", default_result.value())) {
            throw std::runtime_error{"Failed to set result_key"};
        }
        if (!kvs->flush()) {
            throw std::runtime_error{"Failed to flush"};
        }

        KvsInstance::normalize_snapshot_file_to_rust_envelope(params);
    }
};

/// Override all six keys, then call reset_key on even-indexed keys (0, 2, 4),
/// flush. Python verifies even-indexed keys are absent from the snapshot
/// (reverted to in-memory defaults) while odd-indexed keys (1, 3, 5) remain
/// with override values — combining feat_req__persistency__reset_to_default,
/// feat_req__persistency__default_values, feat_req__persistency__default_value_file,
/// and feat_req__persistency__store_data in one observable storage outcome.
class SelectiveReset final : public Scenario {
public:
    std::string name() const final { return "selective_reset"; }

    void run(const std::string& input) const final {
        const int num_keys{6};
        auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
        auto kvs{create_kvs(params)};

        std::vector<std::string> keys;
        for (int i{0}; i < num_keys; ++i) {
            std::string key{"sel_key_" + std::to_string(i)};
            if (!kvs.set_value(key, KvsValue{100.0 * (i + 1)})) {
                throw std::runtime_error{"Failed to set value"};
            }
            keys.push_back(key);
        }

        if (!kvs.flush()) {
            throw std::runtime_error{"Failed to flush after set"};
        }

        // Reset even-indexed keys (0, 2, 4); odd-indexed keep their overrides.
        for (int i{0}; i < num_keys; i += 2) {
            if (!kvs.reset_key(keys[i])) {
                throw std::runtime_error{"Failed to reset key: " + keys[i]};
            }
        }

        if (!kvs.flush()) {
            throw std::runtime_error{"Failed to flush after reset"};
        }

        KvsInstance::normalize_snapshot_file_to_rust_envelope(params);
    }
};

/// Write four initial keys and flush, then call reset() to clear all keys, then write
/// two new keys and flush again. Python verifies all four initial keys are absent and
/// both new keys are present with the correct values — proving reset() cleared the
/// entire storage and subsequent writes persist correctly.
/// This is the only FIT scenario that exercises the "all keys" variant of
/// feat_req__persistency__reset_to_default (as opposed to reset_key which is covered
/// by SelectiveReset). Combines with feat_req__persistency__default_values,
/// feat_req__persistency__default_value_file, and feat_req__persistency__store_data.
class FullReset final : public Scenario {
public:
    std::string name() const final { return "full_reset"; }

    void run(const std::string& input) const final {
        auto params{KvsParameters::from_json_section(input, "kvs_parameters_1")};
        auto kvs{create_kvs(params)};

        // Phase 1: write four initial keys and flush.
        for (int i{0}; i < 4; ++i) {
            std::string key{"fr_key_" + std::to_string(i)};
            if (!kvs.set_value(key, KvsValue{100.0 * (i + 1)})) {
                throw std::runtime_error{"Failed to set initial value for " + key};
            }
        }
        if (!kvs.flush()) {
            throw std::runtime_error{"Failed to flush after initial set"};
        }

        // Phase 2: reset ALL keys, write two new keys, flush.
        if (!kvs.reset()) {
            throw std::runtime_error{"Failed to reset all keys"};
        }
        if (!kvs.set_value("fr_new_0", KvsValue{10.0})) {
            throw std::runtime_error{"Failed to set fr_new_0"};
        }
        if (!kvs.set_value("fr_new_1", KvsValue{20.0})) {
            throw std::runtime_error{"Failed to set fr_new_1"};
        }
        if (!kvs.flush()) {
            throw std::runtime_error{"Failed to flush after reset"};
        }
        KvsInstance::normalize_snapshot_file_to_rust_envelope(params);
    }
};

}  // namespace

ScenarioGroup::Ptr default_values_group() {
    return ScenarioGroup::Ptr{new ScenarioGroupImpl{
        "default_values",
        {std::make_shared<Checksum>(), std::make_shared<PartialOverride>(),
         std::make_shared<GetDefaultValue>(), std::make_shared<SelectiveReset>(),
         std::make_shared<FullReset>()},
        {}}};
}
