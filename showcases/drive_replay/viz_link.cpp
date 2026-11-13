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

#include "showcases/drive_replay/viz_link.h"

#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <string>

namespace score::showcases::drive_replay
{
namespace
{

// Read relative to the working directory, so the feed can be switched on without rebuilding the launch manager config.
constexpr const char* kAddressFile{"etc/drive_viz_addr"};

std::string ConfiguredDestination()
{
    const char* configured = std::getenv("DRIVE_VIZ_ADDR");
    if (configured != nullptr && configured[0] != '\0')
    {
        return configured;
    }
    std::ifstream file{kAddressFile};
    std::string address{};
    file >> address;
    return address;
}

}  // namespace

VizLink::VizLink() noexcept
{
    destination_text_ = ConfiguredDestination();
    if (destination_text_.empty())
    {
        destination_text_ = "off";
        return;
    }

    const auto colon = destination_text_.rfind(':');
    if (colon == std::string::npos)
    {
        destination_text_ = "off (invalid address '" + destination_text_ + "')";
        return;
    }
    const std::string host = destination_text_.substr(0U, colon);
    const long port = std::strtol(destination_text_.c_str() + colon + 1U, nullptr, 10);
    if ((port <= 0L) || (port > 65535L))
    {
        destination_text_ = "off (invalid address '" + destination_text_ + "')";
        return;
    }

    destination_.sin_family = AF_INET;
    destination_.sin_port = htons(static_cast<std::uint16_t>(port));
    if (inet_pton(AF_INET, host.c_str(), &destination_.sin_addr) != 1)
    {
        destination_text_ = "off (invalid address '" + destination_text_ + "')";
        return;
    }
    socket_ = ::socket(AF_INET, SOCK_DGRAM, 0);
}

VizLink::~VizLink() noexcept
{
    if (socket_ >= 0)
    {
        ::close(socket_);
    }
}

void VizLink::Send(const std::string& json) const noexcept
{
    if (socket_ < 0)
    {
        return;
    }
    // Visualization is best effort: a missing receiver must never block the vehicle functions.
    static_cast<void>(::sendto(socket_,
                               json.data(),
                               json.size(),
                               MSG_DONTWAIT,
                               reinterpret_cast<const sockaddr*>(&destination_),
                               sizeof(destination_)));
}

const std::string& VizLink::Destination() const noexcept
{
    return destination_text_;
}

}  // namespace score::showcases::drive_replay
