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

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

/// Open a KVS whose defaults file contains keys with non-ASCII UTF-8
/// characters. KVS keys must be printable ASCII, so opening must fail with
/// kInvalidKey; the scenario fails if the KVS accepts the file or fails for
/// another reason. Python verifies the scenario
/// succeeded and that no snapshot was written.
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

        try {
            kvs_build_helpers::create_kvs(params);
        } catch (const std::runtime_error& e) {
            // create_kvs throws with the KVS error message; kInvalidKey reads "Key is not valid".
            if (std::string(e.what()) == "Key is not valid") {
                return;
            }
            throw std::runtime_error(std::string("Expected kInvalidKey, got: ") + e.what());
        }
        throw std::runtime_error("KVS accepted a defaults file with non-ASCII keys");
    }
};

/// Read a default value whose key uses printable ASCII punctuation and a space
/// (the edges of the allowed key characters) without ever calling set_value on
/// it. Write the retrieved value to an ASCII result key and flush.
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
        auto default_result = kvs->get_default_value_f64("probe ~!#$%");
        if (!default_result.has_value()) {
            throw std::runtime_error("Failed to read default value for 'probe ~!#$%'");
        }

        // Persist to a plain result key so Python can verify it independently.
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
