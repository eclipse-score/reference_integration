# Logging App Demo
 
This Logging App demonstrates logging using mw::log with all log levels and configured backends (kConsole|kRemote|kFile) enabled.

For remote (DLT) logging, please refer to the following documentation:
 
[Remote logging](https://github.com/eclipse-score/logging/blob/main/score/datarouter/doc/guideline/dlt_capture_demo.md)

# Drive Replay Demo

A scripted highway drive into a forward collision warning, supervised by the launch
manager: a hanging or crashing warning function is detected, the system falls back to a
degraded mode and recovers, visible step by step in the DLT log. See
[drive_replay/README.md](drive_replay/README.md).

# S-CORE Platform Run

`/showcases/bin/cli --examples 'S-CORE Platform Run'` starts the launch manager
with [platform_run/launch_manager_config.json](platform_run/launch_manager_config.json).
It starts the datarouter, the platform info service and the config daemon,
then the test applications one after another; each must exit with code 0.
Once all have, the launch manager reaches the run target `PlatformRun` and the
run prints `S-CORE platform run: PASSED`, otherwise `FAILED` (at the latest
after 60 s).

All processes log via mw::log to the console and as DLT through the datarouter
(UDP multicast `239.255.42.99:3490`). The launch manager logs at debug level to
DLT ([platform_run/logging.json](platform_run/logging.json)), including every
process start and termination.

## Config management

The platform deploys the config daemon (`//deploy/config_management`). In the
platform run the launch manager keeps it running as a platform daemon, with
[platform_run/logging_config_daemon.json](platform_run/logging_config_daemon.json)
as its mw::log configuration (app id `CFGD`).

`/showcases/bin/cli --examples 'Config Management Daemon Example'` runs the
deployed daemon on its own: it loads the demo parameters from
`/usr/bin/config_management/etc/demo_parameters.json`, offers them over mw::com
and is stopped with SIGTERM after 10 s. The test
`//platform_integration_tests/config_management` runs this showcase and checks
that the daemon offered its config provider service and loaded the parameters.
The `[Lifecycle client] FD 111 is invalid for kRunning report` error line is
expected there, as the daemon runs without the launch manager.

## Platform integration test

`//platform_integration_tests/platform_run` (Linux x86_64) records the DLT
traffic while the showcase runs; CI uploads it as artifact
`platform-run-dlt-<sha>`. The test requires the `PASSED` line on the console,
no `FAILED` line, and in the DLT trace:

| App id / context | Expected payload                                                            |
|------------------|-----------------------------------------------------------------------------|
| `DR` / `DFLT`    | `successfully completed initialization`                                     |
| `CFGD` / `App`   | `ConfigDaemon:: Run InternalConfigProviderService offered`                  |
| `CFGD` / `DemJ`  | `DemoJson:: Run - Demo parameters loaded`                                   |
| `EXA` / `DFLT`   | `Logging Application DoLogging`                                             |
| `LGGG` / `LOGG`  | `DLT generator finished`                                                    |
| `PINC` / `PINF`  | `platform_info_consumer: S-CORE version check passed`                       |
| `LM` / `LM`      | `Completed the request for Run Target PlatformRun`                          |
| `LM` / `LM`      | per test application: `Starting process ( <app> )` and `Process <app> ( pid <n> ) terminated with status 0` |

It fails on any launch manager warning in the trace (`unexpected termination of
process`, `Problem discovered`, `did not meet its ready condition`).

To add a check, extend `EXPECTED_DLT` or `FORBIDDEN_DLT` in
[test_platform_run.py](../platform_integration_tests/platform_run/test_platform_run.py).
To add a test application, add it to `launch_manager_config.json`, to the
`PlatformRun` run target and to `TEST_APPS`.
