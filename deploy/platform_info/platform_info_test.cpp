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

#include "deploy/platform_info/platform_info.h"

#include <gtest/gtest.h>

#include <initializer_list>
#include <string_view>
#include <utility>

namespace score::platform::info
{
namespace
{

template <std::size_t N>
void Set(std::array<char, N>& target, const std::string_view value)
{
    target.fill('\0');
    value.copy(target.data(), N - 1U);
}

// Unsealed (crc32 = 0): Compare and ToString do not look at the checksum.
PlatformInfo Info(const std::string_view timestamp,
                  std::initializer_list<std::pair<std::string_view, std::string_view>> modules)
{
    PlatformInfo info{};
    Set(info.known_good_timestamp, timestamp);
    for (const auto& [name, version] : modules)
    {
        Set(info.modules[info.module_count].name, name);
        Set(info.modules[info.module_count].version, version);
        ++info.module_count;
    }
    return info;
}

TEST(MakePlatformInfo, IsValidAndListsTheTargetSwModules)
{
    const auto info = MakePlatformInfo();

    EXPECT_TRUE(IsValid(info));
    EXPECT_GT(info.module_count, 0U);
    EXPECT_LE(info.module_count, kMaxModules);
    EXPECT_NE(ToString(info).find("\n  score_baselibs "), std::string::npos) << ToString(info);
}

TEST(IsValid, RejectsAChangedVersion)
{
    auto info = MakePlatformInfo();
    info.modules[0].version[0] ^= 0x01;

    EXPECT_FALSE(IsValid(info));
}

TEST(IsValid, RejectsAChangedChecksum)
{
    auto info = MakePlatformInfo();
    info.crc32 ^= 0x01U;

    EXPECT_FALSE(IsValid(info));
}

TEST(IsValid, RejectsTooManyModules)
{
    auto info = MakePlatformInfo();
    info.module_count = kMaxModules + 1U;

    EXPECT_FALSE(IsValid(info));
}

TEST(IsValid, RejectsAnUnterminatedString)
{
    auto info = MakePlatformInfo();
    info.modules[0].name.fill('x');

    EXPECT_FALSE(IsValid(info));
}

TEST(Compare, IsEmptyForTheSameVersion)
{
    EXPECT_EQ(Compare(MakePlatformInfo(), MakePlatformInfo()), "");
}

TEST(Compare, ReportsEveryDifference)
{
    const auto expected = Info("2026-11-01T00:00:00Z", {{"score_a", "1.0.0"}, {"score_b", "2.0.0"}});
    const auto actual = Info("2026-11-02T00:00:00Z", {{"score_a", "1.1.0"}, {"score_c", "3.0.0"}});

    EXPECT_EQ(Compare(expected, actual),
              "known_good: expected 2026-11-01T00:00:00Z, platform has 2026-11-02T00:00:00Z\n"
              "score_a: expected 1.0.0, platform has 1.1.0\n"
              "score_b: missing on the platform\n"
              "score_c: not part of the expected S-CORE version\n");
}

TEST(Compare, IgnoresTheModuleOrder)
{
    const auto expected = Info("t", {{"score_a", "1.0.0"}, {"score_b", "2.0.0"}});
    const auto actual = Info("t", {{"score_b", "2.0.0"}, {"score_a", "1.0.0"}});

    EXPECT_EQ(Compare(expected, actual), "");
}

TEST(ToString, ListsTimestampAndOneLinePerModule)
{
    const auto info = Info("2026-11-01T00:00:00Z", {{"score_a", "1.0.0"}, {"score_b", "0123abcd"}});

    EXPECT_EQ(ToString(info), "known_good 2026-11-01T00:00:00Z\n  score_a 1.0.0\n  score_b 0123abcd");
}

}  // namespace
}  // namespace score::platform::info
