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

#ifndef SHOWCASES_DRIVE_REPLAY_DRIVE_DATA_H
#define SHOWCASES_DRIVE_REPLAY_DRIVE_DATA_H

#include "score/mw/com/types.h"

#include <cstdint>
#include <string_view>

namespace score::showcases::drive_replay
{

inline constexpr std::string_view kDriveDataInstance{"score/showcases/drive_replay/DriveData"};

inline constexpr double kVehicleLengthM{4.5};

enum class DrivePhase : std::uint32_t
{
    kCruise = 0U,
    kLeadBraking = 1U,
    kEgoBraking = 2U,
    kRecovering = 3U,
};

struct DriveFrame
{
    std::uint64_t sequence;
    double sim_time_s;
    double ego_position_m;
    double ego_speed_mps;
    double lead_position_m;
    double lead_speed_mps;
    DrivePhase phase;
};

template <typename Trait>
class DriveDataInterface : public Trait::Base
{
  public:
    using Trait::Base::Base;

    typename Trait::template Event<DriveFrame> frame_{*this, "frame"};
};

using DriveDataSkeleton = score::mw::com::AsSkeleton<DriveDataInterface>;
using DriveDataProxy = score::mw::com::AsProxy<DriveDataInterface>;

}  // namespace score::showcases::drive_replay

#endif  // SHOWCASES_DRIVE_REPLAY_DRIVE_DATA_H
