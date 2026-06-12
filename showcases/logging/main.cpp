// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// <https://www.apache.org/licenses/LICENSE-2.0>
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************

#include "score/mw/log/logger.h"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <string_view>
#include <thread>

using namespace std::chrono_literals;

namespace integration
{

    namespace config
    {
        // logging routing contexts
        constexpr std::string_view kSensorContext{"SENSOR"};
        constexpr std::string_view kControlContext{"CTRL"};
    } // namespace config

    class SensorPipeline
    {
    public:
        SensorPipeline()
            : logger_{score::mw::log::CreateLogger(
                  config::kSensorContext.data(),
                  "Sensor")}
        {
            // log info: sensor service startup
            logger_.LogInfo()
                << "sensor initialized";
        }

        void Process(std::uint32_t frame_id)
        {
            // log debug: frame entry tracking
            logger_.LogDebug()
                << "frame received=" << frame_id;

            // log info: frame processed successfully
            logger_.LogInfo()
                << "frame processed"
                << " id=" << frame_id;

            if (frame_id == 3U)
            {
                // log warn : processing delay detected
                logger_.LogWarn()
                    << "processing delay frame=" << frame_id;
            }

            if (frame_id == 5U)
            {
                // log error : frame processing failure
                logger_.LogError()
                    << "processing failed frame=" << frame_id;
            }
        }

    private:
        score::mw::log::Logger &logger_;
    };

    class VehicleController
    {
    public:
        VehicleController()
            : logger_{score::mw::log::CreateLogger(
                  config::kControlContext.data(),
                  "Control")}
        {
            // log info : controller initialization complete
            logger_.LogInfo()
                << "controller ready mode=AUTO";
        }

        void Execute(std::uint32_t frame_id)
        {
            const std::uint32_t speed{frame_id * 10U};

            // log debug : control cycle execution trace
            logger_.LogDebug()
                << "control cycle=" << frame_id;

            // log info : control decision applied
            logger_.LogInfo()
                << "control applied"
                << " id=" << frame_id;

            if (frame_id >= 6U)
            {
                // log warn : high speed condition detected
                logger_.LogWarn()
                    << "high speed frame=" << frame_id;
            }

            if (frame_id == 7U)
            {
                // log fatal : emergency stop
                logger_.LogFatal()
                    << "emergency stop triggered at frame=" << frame_id;
            }
        }

    private:
        score::mw::log::Logger &logger_;
    };

    class Application
    {
    public:
        void Run()
        {
            std::cout << "\nLogging Example\n";

            SensorPipeline sensor;
            VehicleController control;

            for (std::uint32_t frame{1U}; frame <= 8U; ++frame)
            {
                std::cout << "Frame=" << frame << '\n';

                sensor.Process(frame);
                control.Execute(frame);

                std::this_thread::sleep_for(300ms);
            }

            std::cout << "\nLogging Example finished\n";
        }
    };

} // namespace integration

int main()
{
    integration::Application app;
    app.Run();
    return EXIT_SUCCESS;
}