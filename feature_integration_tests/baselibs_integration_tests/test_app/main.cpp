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

// On-target test app for the Eclipse S-CORE base libraries.
//
// Each subcommand exercises exactly one baselibs feature library and prints a
// single deterministic "<name>: ..." line to stdout. The baselibs integration
// tests in feature_integration_tests/baselibs_integration_tests run these
// subcommands on the deployed target image and assert on the printed line,
// thereby verifying the corresponding feat_req__baselibs__* feature
// requirement.

#include "score/bitmanipulation/bit_manipulation.h"
#include "score/containers/dynamic_array.h"
#include "score/hash/code/crc/crc32_ieee.h"
#include "score/json/json_parser.h"
#include "score/result/error.h"
#include "score/result/result.h"
#include "score/utils/base64.h"

#include "score/span.hpp"

#include <cstdint>
#include <iostream>
#include <string>
#include <string_view>
#include <vector>

namespace
{

// Minimal self-contained error domain so the result subcommand can exercise the
// error path without pulling in a logging backend.
enum class AppErrc : score::result::ErrorCode
{
    kDivideByZero = 1,
};

class AppErrorDomain final : public score::result::ErrorDomain
{
  public:
    std::string_view MessageFor(const score::result::ErrorCode& code) const noexcept override
    {
        return (static_cast<AppErrc>(code) == AppErrc::kDivideByZero) ? "division by zero" : "unknown error";
    }
};

constexpr AppErrorDomain kAppErrorDomain;

score::result::Error MakeError(const AppErrc code, const std::string_view user_message = "") noexcept
{
    return score::result::Error{static_cast<score::result::ErrorCode>(code), kAppErrorDomain, user_message};
}

score::Result<int> SafeDivide(const int numerator, const int denominator)
{
    if (denominator == 0)
    {
        return score::MakeUnexpected(AppErrc::kDivideByZero, "cannot divide by zero");
    }
    return numerator / denominator;
}

// feat_req__baselibs__json_library
int RunJson()
{
    static constexpr char kDocument[] = R"({"name":"baselibs","version":2,"libs":["json","result"]})";

    const score::json::JsonParser parser;
    const auto root = parser.FromBuffer(kDocument);
    if (!root.has_value())
    {
        std::cout << "json: parse_error\n";
        return 1;
    }

    const auto& object_result = root.value().As<score::json::Object>();
    if (!object_result.has_value())
    {
        std::cout << "json: not_an_object\n";
        return 1;
    }
    const auto& object = object_result.value().get();

    const auto name = object.find("name")->second.As<std::string>();
    const auto version = object.find("version")->second.As<std::uint64_t>();
    const auto libs = object.find("libs")->second.As<score::json::List>();

    std::cout << "json: name=" << name.value().get() << " version=" << version.value()
              << " libs_count=" << libs.value().get().size() << "\n";
    return 0;
}

// feat_req__baselibs__utils_library
int RunBase64()
{
    const std::vector<std::uint8_t> input{'f', 'o', 'o', 'b', 'a', 'r'};
    const std::string encoded = score::utils::EncodeBase64(input);
    const std::vector<std::uint8_t> decoded = score::utils::DecodeBase64(encoded);
    const bool roundtrip = (decoded == input);

    const std::string decoded_text{decoded.begin(), decoded.end()};
    std::cout << "base64: encoded=" << encoded << " decoded=" << decoded_text
              << " roundtrip=" << (roundtrip ? "ok" : "fail") << "\n";
    return roundtrip ? 0 : 1;
}

// feat_req__baselibs__bitmanipulation
int RunBitManip()
{
    std::uint8_t value{0U};
    score::platform::SetBit(value, 1U);   // -> 0b00000010 (2)
    score::platform::SetBit(value, 4U);   // -> 0b00010010 (18)
    const bool bit4_set = score::platform::CheckBit(value, 4U);
    score::platform::ToggleBit(value, 1U);  // -> 0b00010000 (16)

    std::cout << "bitmanip: value=" << static_cast<unsigned>(value) << " check_bit4=" << (bit4_set ? 1 : 0)
              << "\n";
    return 0;
}

// feat_req__baselibs__hash_library
int RunCrc32()
{
    const std::vector<std::uint8_t> data{'1', '2', '3', '4', '5', '6', '7', '8', '9'};

    score::hash::Crc32IeeeHashCalculator calculator;
    const auto update_result = calculator.Update(score::cpp::span<const std::uint8_t>{data.data(), data.size()});
    if (!update_result.has_value())
    {
        std::cout << "crc32: update_error\n";
        return 1;
    }
    const std::uint32_t checksum = static_cast<std::uint32_t>(calculator.GetChecksum());

    std::cout << "crc32: checksum=0x" << std::hex << checksum << std::dec << "\n";
    return 0;
}

// feat_req__baselibs__containers_library
int RunContainers()
{
    score::containers::DynamicArray<int> array{4U};
    array[0U] = 10;
    array[1U] = 20;
    array[2U] = 30;
    array[3U] = 40;

    int sum{0};
    for (const int element : array)
    {
        sum += element;
    }

    std::cout << "containers: size=" << array.size() << " sum=" << sum << "\n";
    return 0;
}

// feat_req__baselibs__result_library
int RunResult()
{
    const auto ok = SafeDivide(84, 2);
    const auto err = SafeDivide(1, 0);

    std::cout << "result: ok_value=" << ok.value() << " error_handled=" << (err.has_value() ? 0 : 1)
              << " error_msg=" << err.error().Message() << "\n";
    return 0;
}

}  // namespace

int main(int argc, char** argv)
{
    if (argc < 2)
    {
        std::cerr << "usage: baselibs_test_app <json|base64|bitmanip|crc32|containers|result>\n";
        return 2;
    }

    const std::string_view command{argv[1]};
    if (command == "json")
    {
        return RunJson();
    }
    if (command == "base64")
    {
        return RunBase64();
    }
    if (command == "bitmanip")
    {
        return RunBitManip();
    }
    if (command == "crc32")
    {
        return RunCrc32();
    }
    if (command == "containers")
    {
        return RunContainers();
    }
    if (command == "result")
    {
        return RunResult();
    }

    std::cerr << "unknown command: " << command << "\n";
    return 2;
}
