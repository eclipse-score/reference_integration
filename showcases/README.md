# Logging App Demo
 
This Logging App demonstrates logging using mw::log with all log levels and configured backends (kConsole|kRemote|kFile) enabled.

For remote (DLT) logging, please refer to the following documentation:
 
[Remote logging](https://github.com/eclipse-score/logging/blob/main/score/datarouter/doc/guideline/dlt_capture_demo.md)

# S-CORE Platform Run

`/showcases/bin/cli --examples 'S-CORE Platform Run'` hands control to the
deployed launch manager ([platform_run/launch_manager_config.json](platform_run/launch_manager_config.json)):

1. It starts the platform daemons first: the datarouter, then the platform info
   service. The component `platform_ready` depends on all of them and marks the
   boundary.
2. Once `platform_ready` is reached, it starts the test applications, which
   depend only on `platform_ready`: logging, baselibs, Kyron and
   communication examples and the platform version check. Each must exit with
   code 0. The Kyron select example is left out: its assertion depends on
   which of three concurrent jobs finishes first and fails intermittently.
3. Only then it reaches the `PlatformRun` run target and the run prints
   `S-CORE platform run: PASSED`. Otherwise it prints `FAILED`, at the latest
   after 60 s.

The applications log via mw::log to the console and, through the datarouter, as
DLT (UDP multicast `239.255.42.99:3490`). Run `dlt-receive` or DLT Viewer next to
it to see them. `//platform_integration_tests/platform_run` records that DLT
traffic with ITF and checks it after the run.