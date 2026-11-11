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

#include "../../internals/persistency/kvs_build_helpers.h"
#include "../../internals/persistency/kvs_instance.h"

#include <scenario.hpp>

#include <stdexcept>
#include <string>

namespace {

/// Open a KVS whose defaults file was created with printable-ASCII key names with spaces and punctuation.
/// Override only the punctuation key and flush. Python verifies:
/// - the punctuation key appears in the snapshot with the override value
/// - the plain and space keys are absent (never explicitly written)
///
/// Combines feat_req__persistency__support_datatype_keys,
/// feat_req__persistency__default_values, and
/// feat_req__persistency__default_value_file.
class Utf8Defaults : public Scenario {
public:
    std::string name() const override {
        return "utf8_defaults";
    }

    void run(const std::string& input) const override {
        KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");

        auto kvs_opt = KvsInstance::create(params);
        if (!kvs_opt) {
            throw std::runtime_error("Failed to create KVS instance");
        }
        auto kvs = *kvs_opt;

        // Override only the punctuation key; plain and space keys remain as defaults.
        if (!kvs->set_value("ascii_punct_key !?", 777.0)) {
            throw std::runtime_error("Failed to set value");
        }

        if (!kvs->flush()) {
            throw std::runtime_error("Failed to flush KVS");
        }

        // Log default values for plain and space keys so Python can assert they are accessible.
        auto val_ascii = kvs->get_default_value_f64("utf8_ascii_key");
        if (!val_ascii.has_value()) {
            throw std::runtime_error("Failed to read default value for 'utf8_ascii_key'");
        }
        auto val_space = kvs->get_default_value_f64("ascii_space key");
        if (!val_space.has_value()) {
            throw std::runtime_error("Failed to read default value for 'ascii_space key'");
        }
        kvs_build_helpers::log_info(
            "\"key\":\"utf8_ascii_key\",\"value\":" + kvs_build_helpers::format_double_python(val_ascii.value()),
            "cpp_test_scenarios::scenarios::persistency::utf8_defaults");
        kvs_build_helpers::log_info(
            "\"key\":\"ascii_space key\",\"value\":" + kvs_build_helpers::format_double_python(val_space.value()),
            "cpp_test_scenarios::scenarios::persistency::utf8_defaults");

        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params)) {
            std::cerr << "Warning: Failed to normalize snapshot file" << std::endl;
        }
    }
};

/// Read a default value whose key is a punctuation string without ever calling
/// set_value on it. Write the retrieved value to an ASCII result key and flush.
/// Python verifies the result key equals the expected default, combining
/// feat_req__persistency__default_value_get with
/// feat_req__persistency__support_datatype_keys in one observable storage outcome.
class Utf8DefaultValueGet : public Scenario {
public:
    std::string name() const override {
        return "utf8_default_value_get";
    }

    void run(const std::string& input) const override {
        KvsParameters params = KvsParameters::from_json_section(input, "kvs_parameters_1");

        auto kvs_opt = KvsInstance::create(params);
        if (!kvs_opt) {
            throw std::runtime_error("Failed to create KVS instance");
        }
        auto kvs = *kvs_opt;

        // Read the default via a punctuation key — never explicitly set.
        auto default_result = kvs->get_default_value_f64("probe key ~!");
        if (!default_result.has_value()) {
            throw std::runtime_error("Failed to read default value for 'probe key ~!'");
        }

        // Persist to an ASCII result key so Python can verify without special-character key lookup.
        if (!kvs->set_value("result_key", default_result.value())) {
            throw std::runtime_error("Failed to set result_key");
        }
        if (!kvs->flush()) {
            throw std::runtime_error("Failed to flush KVS");
        }
        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params)) {
            std::cerr << "Warning: Failed to normalize snapshot file" << std::endl;
        }
    }
};

}  // anonymous namespace

Scenario::Ptr make_utf8_defaults_scenario() {
    return std::make_shared<Utf8Defaults>();
}

Scenario::Ptr make_utf8_default_value_get_scenario() {
    return std::make_shared<Utf8DefaultValueGet>();
}
