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

#ifndef INTERNALS_PERSISTENCY_KVS_INSTANCE_H_
#define INTERNALS_PERSISTENCY_KVS_INSTANCE_H_

#include "kvs_parameters.h"

#include <cstdint>
#include <kvs.hpp>
#include <memory>
#include <optional>
#include <string>

class KvsInstance {
public:
    // Factory method to create KVS instance
    static std::optional<std::shared_ptr<KvsInstance>> create(const KvsParameters& params);

    // Wrap snapshot file into Rust-style top-level object envelope.
    static bool normalize_snapshot_file_to_rust_envelope(const KvsParameters& params);

    // Set a value
    bool set_value(const std::string& key, double value);

    // Set unsigned 32-bit value.
    bool set_value_u32(const std::string& key, std::uint32_t value);

    // Get a value
    std::optional<double> get_value(const std::string& key);

    // Get unsigned 32-bit value.
    std::optional<std::uint32_t> get_value_u32(const std::string& key);

    // Flush to persistent storage
    bool flush();

    // Get instance parameters
    const KvsParameters& get_parameters() const {
        return params_;
    }

private:
    KvsInstance(const KvsParameters& params, score::mw::per::kvs::Kvs&& kvs);

    KvsParameters params_;
    score::mw::per::kvs::Kvs kvs_;
};

#endif  // INTERNALS_PERSISTENCY_KVS_INSTANCE_H_
