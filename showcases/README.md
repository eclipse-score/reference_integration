# Logging App Demo
 
This Logging App demonstrates logging using mw::log with all log levels and configured backends (kConsole|kRemote|kFile) enabled.

For remote (DLT) logging, please refer to the following documentation:
 
[Remote logging](https://github.com/eclipse-score/logging/blob/main/score/datarouter/doc/guideline/dlt_capture_demo.md)

# S-CORE Platform Run

`/showcases/bin/cli --examples 'S-CORE Platform Run'` hands control to the
deployed launch manager ([platform_run/launch_manager_config.json](platform_run/launch_manager_config.json)):

1. It starts the platform daemons first (today the datarouter).
2. Once they run, it starts the test applications: logging, baselibs, Kyron and
   communication examples. Each must exit with code 0.
3. Only then it reaches the `PlatformRun` run target and the run prints
   `S-CORE platform run: PASSED`. Otherwise it prints `FAILED` after 60 s.

The applications log via mw::log to the console and, through the datarouter, as
DLT (UDP multicast `239.255.42.99:3490`). Run `dlt-receive` or DLT Viewer next to
it to see them. `//platform_integration_tests/platform_run` records that DLT
traffic with ITF and checks it after the run.