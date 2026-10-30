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

#ifndef DEPLOY_COMMUNICATION_HEARTBEAT_H
#define DEPLOY_COMMUNICATION_HEARTBEAT_H

#include "score/mw/com/types.h"

#include <array>
#include <cstdint>
#include <string>
#include <string_view>

namespace score::platform::heartbeat
{

// Resolved by provider and consumer through the deployed mw_com_config.json.
inline constexpr std::string_view kInstanceSpecifier{"score/platform/heartbeat"};

inline constexpr std::size_t kPayloadSize{32U};

struct Heartbeat
{
    std::uint64_t sequence;
    std::array<std::uint8_t, kPayloadSize> payload;
    std::uint32_t crc32;
};

inline constexpr std::size_t kMaxModules{16U};
inline constexpr std::size_t kNameSize{40U};
inline constexpr std::size_t kVersionSize{48U};
inline constexpr std::size_t kTimestampSize{32U};

// Fixed-size, zero-terminated strings: the value lives in shared memory.
struct ModuleVersion
{
    std::array<char, kNameSize> name;
    std::array<char, kVersionSize> version;
};

/// The S-CORE version the platform was built from: the known_good.json snapshot and its target_sw modules.
struct PlatformInfo
{
    std::array<char, kTimestampSize> known_good_timestamp;
    std::uint32_t module_count;
    std::array<ModuleVersion, kMaxModules> modules;
    std::uint32_t crc32;
};

template <typename Trait>
class HeartbeatInterface : public Trait::Base
{
  public:
    using Trait::Base::Base;

    typename Trait::template Event<Heartbeat> heartbeat_{*this, "heartbeat"};
    typename Trait::template Field<PlatformInfo, score::mw::com::WithNotifier> platform_info_{*this, "platform_info"};
};

using HeartbeatSkeleton = score::mw::com::AsSkeleton<HeartbeatInterface>;
using HeartbeatProxy = score::mw::com::AsProxy<HeartbeatInterface>;

/// Heartbeat number `sequence`: a payload derived from the sequence, sealed with a baselibs CRC32.
Heartbeat MakeHeartbeat(std::uint64_t sequence) noexcept;

/// True if the payload matches the sequence and the baselibs CRC32 over both is intact.
bool IsValid(const Heartbeat& heartbeat) noexcept;

/// The S-CORE version this binary was built from, sealed with a baselibs CRC32.
PlatformInfo MakePlatformInfo() noexcept;

/// True if the module count is in range, all strings are terminated and the baselibs CRC32 is intact.
bool IsValid(const PlatformInfo& info) noexcept;

/// One line per module, e.g. "score_baselibs 0.2.16".
std::string ToString(const PlatformInfo& info);

/// Differences between `expected` and `actual`, one per line; empty if both describe the same version.
std::string Compare(const PlatformInfo& expected, const PlatformInfo& actual);

}  // namespace score::platform::heartbeat

#endif  // DEPLOY_COMMUNICATION_HEARTBEAT_H
