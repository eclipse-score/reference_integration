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

// A "Reporting" launch_manager component that deterministically aborts on its
// first N startup attempts, then reports Running from attempt N+1 onward. The
// attempt count is persisted in a counter file so it survives across the
// process restarts that launch_manager performs in place, letting FITs
// exercise `ready_recovery_action.restart.number_of_attempts` (retry, and
// retry exhaustion) without relying on a real, racy startup failure.
//
// Must call report_running(): launch_manager's restart-in-place accounting is
// driven by the control-client channel that report_running() sets up. A plain
// "Native" process (no lifecycle API integration) never establishes that
// channel, so its startup failures go straight to the process group's
// recovery_action instead of being retried per `number_of_attempts`.

#include <unistd.h>
#include <csignal>
#include <cstdlib>
#include <atomic>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <thread>

#include <score/mw/lifecycle/report_running.h>

namespace {

std::atomic<bool> exit_requested{false};

void signal_handler(int signal)
{
    if (signal == SIGINT || signal == SIGTERM)
    {
        exit_requested = true;
    }
}

int read_attempt_count(const std::filesystem::path& counter_path)
{
    std::ifstream in(counter_path);
    int count = 0;
    if (in)
    {
        in >> count;
    }
    return count;
}

void write_attempt_count(const std::filesystem::path& counter_path, int count)
{
    std::ofstream out(counter_path, std::ios::trunc);
    out << count;
}

}  // namespace

int main(int argc, char** argv)
{
    if (argc < 3)
    {
        std::cerr << "usage: flaky_startup_app <counter_file> <crashes_before_success>" << std::endl;
        return EXIT_FAILURE;
    }

    const std::filesystem::path counter_path{argv[1]};
    const int crashes_before_success = std::atoi(argv[2]);

    const int attempt = read_attempt_count(counter_path);
    write_attempt_count(counter_path, attempt + 1);

    if (attempt < crashes_before_success)
    {
        std::cerr << "flaky_startup_app: simulating crash on attempt " << attempt << std::endl;
        std::abort();
    }

    std::cerr << "flaky_startup_app: starting successfully on attempt " << attempt << std::endl;
    score::mw::lifecycle::report_running();

    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    while (!exit_requested)
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return EXIT_SUCCESS;
}
