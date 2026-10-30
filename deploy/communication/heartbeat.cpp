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

#include "deploy/communication/heartbeat.h"

#include "deploy/communication/platform_info_data.h"
#include "score/hash/code/crc/crc32_ieee.h"

#include <algorithm>
#include <optional>

namespace score::platform::heartbeat
{
namespace
{

constexpr bool GeneratedDataFits() noexcept
{
    if ((generated::kModules.size() > kMaxModules) || (generated::kKnownGoodTimestamp.size() >= kTimestampSize))
    {
        return false;
    }
    for (const auto& module : generated::kModules)
    {
        if ((module.name.size() >= kNameSize) || (module.version.size() >= kVersionSize))
        {
            return false;
        }
    }
    return true;
}
static_assert(GeneratedDataFits(), "known_good.json does not fit into PlatformInfo; raise the sizes in heartbeat.h");

template <std::size_t N>
void CopyTo(std::array<char, N>& target, const std::string_view value) noexcept
{
    target.fill('\0');
    std::copy_n(value.begin(), std::min(value.size(), N - 1U), target.begin());
}

template <std::size_t N>
bool IsTerminated(const std::array<char, N>& value) noexcept
{
    return std::find(value.begin(), value.end(), '\0') != value.end();
}

template <std::size_t N>
std::string_view View(const std::array<char, N>& value) noexcept
{
    const auto end = std::find(value.begin(), value.end(), '\0');
    return {value.data(), static_cast<std::size_t>(end - value.begin())};
}

template <std::size_t N>
score::Result<void> Feed(score::hash::Crc32IeeeHashCalculator& crc, const std::array<char, N>& value) noexcept
{
    // Whole array incl. zero padding, so the checksum covers every byte of the sample.
    return crc.Update({reinterpret_cast<const std::uint8_t*>(value.data()), value.size()});
}

std::optional<std::uint32_t> Crc32Of(const PlatformInfo& info) noexcept
{
    std::array<std::uint8_t, sizeof(info.module_count)> count_bytes{};
    for (std::size_t i = 0U; i < count_bytes.size(); ++i)
    {
        count_bytes[i] = static_cast<std::uint8_t>((info.module_count >> (8U * i)) & 0xFFU);
    }

    score::hash::Crc32IeeeHashCalculator crc{};
    bool ok = Feed(crc, info.known_good_timestamp).has_value() &&
              crc.Update({count_bytes.data(), count_bytes.size()}).has_value();
    for (const auto& module : info.modules)
    {
        ok = ok && Feed(crc, module.name).has_value() && Feed(crc, module.version).has_value();
    }
    if (!ok)
    {
        return std::nullopt;
    }
    return static_cast<std::uint32_t>(crc.GetChecksum());
}

const ModuleVersion* FindModule(const PlatformInfo& info, const std::string_view name) noexcept
{
    for (std::size_t i = 0U; i < info.module_count; ++i)
    {
        if (View(info.modules[i].name) == name)
        {
            return &info.modules[i];
        }
    }
    return nullptr;
}

using Payload = std::array<std::uint8_t, kPayloadSize>;

Payload PayloadFor(const std::uint64_t sequence) noexcept
{
    Payload payload{};
    for (std::size_t i = 0U; i < payload.size(); ++i)
    {
        payload[i] = static_cast<std::uint8_t>((sequence + i) & 0xFFU);
    }
    return payload;
}

std::optional<std::uint32_t> Crc32Of(const std::uint64_t sequence, const Payload& payload) noexcept
{
    // Serialized explicitly so the checksum does not depend on struct padding or endianness.
    std::array<std::uint8_t, sizeof(sequence)> sequence_bytes{};
    for (std::size_t i = 0U; i < sequence_bytes.size(); ++i)
    {
        sequence_bytes[i] = static_cast<std::uint8_t>((sequence >> (8U * i)) & 0xFFU);
    }

    score::hash::Crc32IeeeHashCalculator crc{};
    if (!crc.Update({sequence_bytes.data(), sequence_bytes.size()}).has_value() ||
        !crc.Update({payload.data(), payload.size()}).has_value())
    {
        return std::nullopt;
    }
    return static_cast<std::uint32_t>(crc.GetChecksum());
}

}  // namespace

Heartbeat MakeHeartbeat(const std::uint64_t sequence) noexcept
{
    Heartbeat heartbeat{sequence, PayloadFor(sequence), 0U};
    heartbeat.crc32 = Crc32Of(heartbeat.sequence, heartbeat.payload).value_or(0U);
    return heartbeat;
}

bool IsValid(const Heartbeat& heartbeat) noexcept
{
    if (heartbeat.payload != PayloadFor(heartbeat.sequence))
    {
        return false;
    }
    const auto crc32 = Crc32Of(heartbeat.sequence, heartbeat.payload);
    return crc32.has_value() && (crc32.value() == heartbeat.crc32);
}

PlatformInfo MakePlatformInfo() noexcept
{
    PlatformInfo info{};
    CopyTo(info.known_good_timestamp, generated::kKnownGoodTimestamp);
    info.module_count = static_cast<std::uint32_t>(generated::kModules.size());
    for (std::size_t i = 0U; i < generated::kModules.size(); ++i)
    {
        CopyTo(info.modules[i].name, generated::kModules[i].name);
        CopyTo(info.modules[i].version, generated::kModules[i].version);
    }
    info.crc32 = Crc32Of(info).value_or(0U);
    return info;
}

bool IsValid(const PlatformInfo& info) noexcept
{
    if ((info.module_count > kMaxModules) || !IsTerminated(info.known_good_timestamp))
    {
        return false;
    }
    for (const auto& module : info.modules)
    {
        if (!IsTerminated(module.name) || !IsTerminated(module.version))
        {
            return false;
        }
    }
    const auto crc32 = Crc32Of(info);
    return crc32.has_value() && (crc32.value() == info.crc32);
}

std::string ToString(const PlatformInfo& info)
{
    std::string text{"known_good "};
    text.append(View(info.known_good_timestamp));
    for (std::size_t i = 0U; i < info.module_count; ++i)
    {
        text.append("\n  ").append(View(info.modules[i].name)).append(" ").append(View(info.modules[i].version));
    }
    return text;
}

std::string Compare(const PlatformInfo& expected, const PlatformInfo& actual)
{
    std::string differences{};
    if (View(expected.known_good_timestamp) != View(actual.known_good_timestamp))
    {
        differences.append("known_good: expected ")
            .append(View(expected.known_good_timestamp))
            .append(", platform has ")
            .append(View(actual.known_good_timestamp))
            .append("\n");
    }
    for (std::size_t i = 0U; i < expected.module_count; ++i)
    {
        const auto& wanted = expected.modules[i];
        const auto* found = FindModule(actual, View(wanted.name));
        if (found == nullptr)
        {
            differences.append(View(wanted.name)).append(": missing on the platform\n");
        }
        else if (View(found->version) != View(wanted.version))
        {
            differences.append(View(wanted.name))
                .append(": expected ")
                .append(View(wanted.version))
                .append(", platform has ")
                .append(View(found->version))
                .append("\n");
        }
    }
    for (std::size_t i = 0U; i < actual.module_count; ++i)
    {
        if (FindModule(expected, View(actual.modules[i].name)) == nullptr)
        {
            differences.append(View(actual.modules[i].name)).append(": not part of the expected S-CORE version\n");
        }
    }
    return differences;
}

}  // namespace score::platform::heartbeat
