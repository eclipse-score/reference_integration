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

#include <scenario.hpp>

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

/// Open a KVS whose defaults file was created with UTF-8 encoded key names.
/// Override only the emoji key and flush. Python verifies:
/// - the emoji key appears in the snapshot with the override value
/// - the ASCII and Greek keys are absent (never explicitly written)
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

        // Override only the emoji key; ascii and greek keys remain as defaults.
        if (!kvs->set_value(u8"utf8_emoji 🔑", 777.0)) {
            throw std::runtime_error("Failed to set value");
        }

        if (!kvs->flush()) {
            throw std::runtime_error("Failed to flush KVS");
        }

        // Log default values for ascii and greek keys so Python can assert they are accessible.
        auto val_ascii = kvs->get_value_f64("utf8_ascii_key");
        if (!val_ascii.has_value()) {
            throw std::runtime_error("Failed to read default value for 'utf8_ascii_key'");
        }
        auto val_greek = kvs->get_value_f64(u8"utf8_greek κλμ");
        if (!val_greek.has_value()) {
            throw std::runtime_error(u8"Failed to read default value for 'utf8_greek κλμ'");
        }
        std::cout << "default key=utf8_ascii_key value=" << val_ascii.value() << "\n";
        std::cout << u8"default key=utf8_greek κλμ value=" << val_greek.value() << "\n";

        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params)) {
            std::cerr << "Warning: Failed to normalize snapshot file" << std::endl;
        }
    }
};

/// Read a default value whose key is a UTF-8 emoji string without ever calling
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

        // Read the default via a UTF-8 emoji key — never explicitly set.
        auto default_result = kvs->get_value_f64(u8"probe 🔍");
        if (!default_result.has_value()) {
            throw std::runtime_error(u8"Failed to read default value for 'probe 🔍'");
        }

        // Persist to an ASCII result key so Python can verify without UTF-8 key lookup.
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
