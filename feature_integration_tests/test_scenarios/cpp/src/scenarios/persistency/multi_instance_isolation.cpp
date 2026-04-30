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

#include <stdexcept>
#include <string>

namespace {

/// Write key_a to instance 1 and key_b to instance 2 within a shared directory.
///
/// Python verifies snapshot isolation: the snapshot of instance 1 contains
/// key_a but not key_b, and the snapshot of instance 2 contains key_b but
/// not key_a.  This proves that default values loaded for one KVS instance
/// do not leak into a second instance sharing the same working directory.
///
/// Partially verifies feat_req__persistency__default_values and
/// feat_req__persistency__multiple_kvs.
class MultiInstanceIsolation final : public Scenario {
public:
    /**
     * @brief Return the scenario name used to identify this scenario in the runner.
     * @return Scenario name string.
     */
    std::string name() const final { return "multi_instance_isolation"; }

    /**
     * @brief Execute the isolation scenario.
     *
     * Opens two KVS instances from the JSON input parameters, writes key_a
     * only to instance 1 and key_b only to instance 2, flushes both, and
     * normalises the snapshot files to the Rust envelope format for Python
     * verification.
     *
     * @param input JSON string containing kvs_parameters_1 and kvs_parameters_2.
     */
    void run(const std::string& input) const final {
        KvsParameters params1 = KvsParameters::from_json_section(input, "kvs_parameters_1");
        KvsParameters params2 = KvsParameters::from_json_section(input, "kvs_parameters_2");

        // Write key_a exclusively to instance 1.
        auto kvs1_opt = KvsInstance::create(params1);
        if (!kvs1_opt) {
            throw std::runtime_error("Failed to create KVS instance 1");
        }
        auto kvs1 = *kvs1_opt;
        if (!kvs1->set_value("key_a", 11.0)) {
            throw std::runtime_error("Failed to set key_a on instance 1");
        }
        if (!kvs1->flush()) {
            throw std::runtime_error("Failed to flush instance 1");
        }
        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params1)) {
            throw std::runtime_error("Failed to normalize snapshot for instance 1");
        }

        // Write key_b exclusively to instance 2.
        auto kvs2_opt = KvsInstance::create(params2);
        if (!kvs2_opt) {
            throw std::runtime_error("Failed to create KVS instance 2");
        }
        auto kvs2 = *kvs2_opt;
        if (!kvs2->set_value("key_b", 22.0)) {
            throw std::runtime_error("Failed to set key_b on instance 2");
        }
        if (!kvs2->flush()) {
            throw std::runtime_error("Failed to flush instance 2");
        }
        if (!KvsInstance::normalize_snapshot_file_to_rust_envelope(params2)) {
            throw std::runtime_error("Failed to normalize snapshot for instance 2");
        }
    }
};

}  // namespace

/**
 * @brief Factory function for MultiInstanceIsolation scenario.
 * @return Shared pointer to the constructed scenario.
 */
Scenario::Ptr make_multi_instance_isolation_scenario() {
    return std::make_shared<MultiInstanceIsolation>();
}
