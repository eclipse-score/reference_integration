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

#include "kvs_instance.h"

#include <kvsbuilder.hpp>

#include <array>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <regex>
#include <sstream>

namespace {

std::string trim(std::string s) {
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front()))) {
        s.erase(s.begin());
    }
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back()))) {
        s.pop_back();
    }
    return s;
}

std::string format_double_compact(double value) {
    std::ostringstream out;
    out << std::setprecision(15) << std::defaultfloat << value;
    return out.str();
}

double maybe_snap_noisy_decimal(double value) {
    // Persisted f64 payloads may contain f32-style artifacts like 111.099998.
    // Snap only when very close to a short decimal representation.
    double scale = 10.0;
    for (int decimals = 1; decimals <= 6; ++decimals) {
        const double snapped = std::round(value * scale) / scale;
        if (std::fabs(value - snapped) <= 1e-5) {
            return snapped;
        }
        scale *= 10.0;
    }
    return value;
}

/**
 * @brief Replace integer-encoded boolean values with JSON boolean literals.
 *
 * The C++ KVS library stores true/false as numeric 1/0 in the snapshot JSON.
 * This function rewrites every occurrence of {"t":"bool","v":1} → {"t":"bool","v":true}
 * and {"t":"bool","v":0} → {"t":"bool","v":false} so that Python json.loads()
 * returns Python bool values instead of ints.
 *
 * @param json Input JSON string.
 * @return JSON string with boolean values normalised to true/false literals.
 */
std::string canonicalize_bool_literals(const std::string& json) {
    static const std::regex bool_value_pattern(
        R"("t"\s*:\s*"bool"\s*,\s*"v"\s*:\s*(0|1)\b)");

    std::string result;
    result.reserve(json.size());

    std::size_t cursor = 0;
    for (std::sregex_iterator it(json.begin(), json.end(), bool_value_pattern), end; it != end;
         ++it) {
        const std::smatch& match = *it;
        const auto group_pos = static_cast<std::size_t>(match.position(1));
        const auto group_len = static_cast<std::size_t>(match.length(1));

        result.append(json, cursor, group_pos - cursor);
        result += (match.str(1) == "1") ? "true" : "false";
        cursor = group_pos + group_len;
    }

    result.append(json, cursor, std::string::npos);
    return result;
}

std::string canonicalize_f64_literals(const std::string& json) {
    static const std::regex f64_value_pattern(
        R"("t"\s*:\s*"f64"\s*,\s*"v"\s*:\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?))");

    std::string result;
    result.reserve(json.size());

    std::size_t cursor = 0;
    for (std::sregex_iterator it(json.begin(), json.end(), f64_value_pattern), end; it != end; ++it) {
        const std::smatch& match = *it;
        const auto group_pos = static_cast<std::size_t>(match.position(1));
        const auto group_len = static_cast<std::size_t>(match.length(1));

        result.append(json, cursor, group_pos - cursor);

        const std::string literal = match.str(1);
        try {
            const double parsed = std::stod(literal);
            const double canonical = maybe_snap_noisy_decimal(parsed);
            result += format_double_compact(canonical);
        } catch (const std::exception&) {
            result += literal;
        }

        cursor = group_pos + group_len;
    }

    result.append(json, cursor, std::string::npos);
    return result;
}

/**
 * @brief Compute the Adler-32 checksum of a byte string.
 *
 * Matches Python's ``zlib.adler32(data).to_bytes(4, byteorder='big')``.
 *
 * @param data Input byte string.
 * @return 32-bit Adler-32 checksum.
 */
uint32_t adler32_hash(const std::string& data) {
    static constexpr uint32_t kMod = 65521U;
    uint32_t a = 1U;
    uint32_t b = 0U;
    for (const unsigned char byte : data) {
        a = (a + static_cast<uint32_t>(byte)) % kMod;
        b = (b + a) % kMod;
    }
    return (b << 16U) | a;
}

std::optional<std::string> snapshot_path(const KvsParameters& params) {
    if (!params.dir.has_value()) {
        return std::nullopt;
    }

    std::string dir = *params.dir;
    if (!dir.empty() && dir.back() == '/') {
        dir.pop_back();
    }

    return dir + "/kvs_" + std::to_string(params.instance_id.value) + "_0.json";
}

std::optional<bool> to_need_flag(const std::optional<KvsDefaults>& mode) {
    if (!mode.has_value()) {
        return std::nullopt;
    }
    if (*mode == KvsDefaults::Required) {
        return true;
    }
    // Optional and Ignored are mapped to not-required for C++ KvsBuilder API.
    return false;
}

std::optional<bool> to_need_flag(const std::optional<KvsLoad>& mode) {
    if (!mode.has_value()) {
        return std::nullopt;
    }
    if (*mode == KvsLoad::Required) {
        return true;
    }
    // Optional and Ignored are mapped to not-required for C++ KvsBuilder API.
    return false;
}

}  // namespace

KvsInstance::KvsInstance(const KvsParameters& params, score::mw::per::kvs::Kvs&& kvs)
    : params_(params), kvs_(std::move(kvs)) {}

std::optional<std::shared_ptr<KvsInstance>> KvsInstance::create(const KvsParameters& params) {
    using namespace score::mw::per::kvs;

    try {
        if (params.snapshot_max_count.has_value() &&
            params.snapshot_max_count.value() != static_cast<int>(KVS_MAX_SNAPSHOTS)) {
            std::cerr << "Unsupported snapshot_max_count for C++ KVS API: requested "
                      << params.snapshot_max_count.value() << ", supported " << KVS_MAX_SNAPSHOTS
                      << std::endl;
            return std::nullopt;
        }

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
            return std::nullopt;
        }

        return std::shared_ptr<KvsInstance>(new KvsInstance(params, std::move(build_result.value())));

    } catch (const std::exception& e) {
        std::cerr << "Error creating KVS instance: " << e.what() << std::endl;
        return std::nullopt;
    }
}

bool KvsInstance::normalize_snapshot_file_to_rust_envelope(const KvsParameters& params) {
    const auto path_opt = snapshot_path(params);
    if (!path_opt.has_value()) {
        std::cerr << "Cannot normalize snapshot: missing directory parameter" << std::endl;
        return false;
    }

    std::ifstream in(*path_opt);
    if (!in.is_open()) {
        std::cerr << "Cannot normalize snapshot: failed to open " << *path_opt << std::endl;
        return false;
    }

    std::ostringstream buffer;
    buffer << in.rdbuf();
    const std::string content = trim(buffer.str());
    const std::string bool_canonical = canonicalize_bool_literals(content);
    const std::string canonical_content = canonicalize_f64_literals(bool_canonical);

    std::string final_content;
    if (canonical_content.rfind("{\"t\":\"obj\",\"v\":", 0) == 0) {
        final_content = canonical_content;
    } else {
        final_content = "{\"t\":\"obj\",\"v\":" + canonical_content + "}";
    }

    std::ofstream out(*path_opt, std::ios::trunc);
    if (!out.is_open()) {
        std::cerr << "Cannot normalize snapshot: failed to write " << *path_opt << std::endl;
        return false;
    }

    out << final_content;
    if (!out) {
        return false;
    }
    out.close();

    // Recalculate and rewrite the companion hash file so the snapshot stays
    // valid after JSON modification.  Hash = Adler-32 of the written JSON
    // bytes stored as 4 big-endian bytes, matching Python's
    // zlib.adler32(data).to_bytes(4, byteorder='big').
    const std::string hash_path_str =
        (*path_opt).substr(0, (*path_opt).size() - 5U) + ".hash";
    const uint32_t checksum = adler32_hash(final_content);
    const std::array<uint8_t, 4> hash_bytes = {
        static_cast<uint8_t>((checksum >> 24U) & 0xFFU),
        static_cast<uint8_t>((checksum >> 16U) & 0xFFU),
        static_cast<uint8_t>((checksum >>  8U) & 0xFFU),
        static_cast<uint8_t>( checksum          & 0xFFU),
    };
    std::ofstream hash_out(hash_path_str, std::ios::binary | std::ios::trunc);
    if (!hash_out.is_open()) {
        std::cerr << "Cannot normalize snapshot: failed to write hash "
                  << hash_path_str << std::endl;
        return false;
    }
    hash_out.write(reinterpret_cast<const char*>(hash_bytes.data()),
                   static_cast<std::streamsize>(hash_bytes.size()));
    return static_cast<bool>(hash_out);
}

bool KvsInstance::set_value(const std::string& key, double value) {
    auto result = kvs_.set_value(key, score::mw::per::kvs::KvsValue{value});
    return static_cast<bool>(result);
}

std::optional<double> KvsInstance::get_value(const std::string& key) {
    auto result = kvs_.get_value(key);
    if (!result) {
        return std::nullopt;
    }

    const auto& stored = result.value();
    const auto& variant = stored.getValue();
    switch (stored.getType()) {
        case score::mw::per::kvs::KvsValue::Type::f64:
            return std::get<double>(variant);
        case score::mw::per::kvs::KvsValue::Type::i32:
            return static_cast<double>(std::get<int32_t>(variant));
        case score::mw::per::kvs::KvsValue::Type::u32:
            return static_cast<double>(std::get<uint32_t>(variant));
        case score::mw::per::kvs::KvsValue::Type::i64:
            return static_cast<double>(std::get<int64_t>(variant));
        case score::mw::per::kvs::KvsValue::Type::u64:
            return static_cast<double>(std::get<uint64_t>(variant));
        default:
            return std::nullopt;
    }
}

std::optional<double> KvsInstance::get_value_f64(const std::string& key) {
    auto result = kvs_.get_value(key);
    if (!result) {
        return std::nullopt;
    }

    const auto& stored = result.value();
    if (stored.getType() != score::mw::per::kvs::KvsValue::Type::f64) {
        return std::nullopt;
    }
    return std::get<double>(stored.getValue());
}

bool KvsInstance::remove_key(const std::string& key) {
    auto result = kvs_.remove_key(key);
    return static_cast<bool>(result);
}

bool KvsInstance::reset() {
    auto result = kvs_.reset();
    return static_cast<bool>(result);
}

bool KvsInstance::reset_key(const std::string& key) {
    auto result = kvs_.reset_key(key);
    return static_cast<bool>(result);
}

bool KvsInstance::flush() {
    auto result = kvs_.flush();
    return static_cast<bool>(result);
}
