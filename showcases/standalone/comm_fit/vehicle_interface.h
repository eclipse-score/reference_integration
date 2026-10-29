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

// VehicleInterface template for the C++ FIT binaries.
// Matches the /bmw/adp/VehicleInterface service type used by the Rust FIT
// binaries so C++ and Rust binaries are wire-compatible over the same SHM.

#ifndef SHOWCASES_STANDALONE_COMM_FIT_VEHICLE_INTERFACE_H
#define SHOWCASES_STANDALONE_COMM_FIT_VEHICLE_INTERFACE_H

namespace score::mw::com::comm_fit
{

struct Tire
{
    float pressure;
};

struct Exhaust
{
};

template <typename Trait>
class VehicleInterface : public Trait::Base
{
  public:
    using Trait::Base::Base;
    typename Trait::template Event<Tire> left_tire{*this, "left_tire"};
    typename Trait::template Event<Exhaust> exhaust{*this, "exhaust"};
};

}  // namespace score::mw::com::comm_fit

#endif  // SHOWCASES_STANDALONE_COMM_FIT_VEHICLE_INTERFACE_H
