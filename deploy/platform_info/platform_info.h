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

#ifndef DEPLOY_PLATFORM_INFO_PLATFORM_INFO_H
#define DEPLOY_PLATFORM_INFO_PLATFORM_INFO_H

#include "score/mw/com/types.h"

#include <array>
#include <cstdint>
#include <string>
#include <string_view>

namespace score::platform::info
{

// Resolved by provider and consumer through the deployed mw_com_config.json.
inline constexpr std::string_view kInstanceSpecifier{"score/platform/info"};

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
class PlatformInfoInterface : public Trait::Base
{
  public:
    using Trait::Base::Base;

    typename Trait::template Field<PlatformInfo, score::mw::com::WithNotifier> platform_info_{*this, "platform_info"};
};

using PlatformInfoSkeleton = score::mw::com::AsSkeleton<PlatformInfoInterface>;
using PlatformInfoProxy = score::mw::com::AsProxy<PlatformInfoInterface>;

/// The S-CORE version this binary was built from, sealed with a baselibs CRC32.
PlatformInfo MakePlatformInfo() noexcept;

/// True if the module count is in range, all strings are terminated and the baselibs CRC32 is intact.
bool IsValid(const PlatformInfo& info) noexcept;

/// The known_good timestamp, then one line per module, e.g. "score_baselibs 0.2.16".
std::string ToString(const PlatformInfo& info);

/// Differences between `expected` and `actual`, one per line; empty if both describe the same version.
std::string Compare(const PlatformInfo& expected, const PlatformInfo& actual);

}  // namespace score::platform::info

#endif  // DEPLOY_PLATFORM_INFO_PLATFORM_INFO_H
