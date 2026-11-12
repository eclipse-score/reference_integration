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

#ifndef SHOWCASES_DRIVE_REPLAY_VIZ_LINK_H
#define SHOWCASES_DRIVE_REPLAY_VIZ_LINK_H

#include <netinet/in.h>

#include <string>

namespace score::showcases::drive_replay
{

/// Fire-and-forget UDP sender for JSON records consumed by viz/foxglove_bridge.py.
/// The destination is taken from DRIVE_VIZ_ADDR ("<ipv4>:<port>"), default 239.255.42.99:9001.
class VizLink
{
  public:
    VizLink() noexcept;
    ~VizLink() noexcept;
    VizLink(const VizLink&) = delete;
    VizLink& operator=(const VizLink&) = delete;
    VizLink(VizLink&&) = delete;
    VizLink& operator=(VizLink&&) = delete;

    void Send(const std::string& json) const noexcept;
    const std::string& Destination() const noexcept;

  private:
    int socket_{-1};
    sockaddr_in destination_{};
    std::string destination_text_{};
};

}  // namespace score::showcases::drive_replay

#endif  // SHOWCASES_DRIVE_REPLAY_VIZ_LINK_H
