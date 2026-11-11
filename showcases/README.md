# Logging App Demo
 
This Logging App demonstrates logging using mw::log with all log levels and configured backends (kConsole|kRemote|kFile) enabled.

For remote (DLT) logging, please refer to the following documentation:
 
[Remote logging](https://github.com/eclipse-score/logging/blob/main/score/datarouter/doc/guideline/dlt_capture_demo.md)

# S-CORE Platform Run

`/showcases/bin/cli --examples 'S-CORE Platform Run'` hands control to the
deployed launch manager. It runs `timeout 60 /usr/bin/launch_manager` in
`/showcases/data/platform_run`, where the launch manager finds its configuration
under `etc/` (built from [platform_run/launch_manager_config.json](platform_run/launch_manager_config.json)).

## Sequence

1. **Platform daemons.** The launch manager starts the `datarouter`, then the
   `platform_info_service`. Both are long-running and count as ready once their
   process is `Running`. The component `platform_ready` (`/bin/true`) depends on
   both and marks the boundary between platform and tests.
2. **Test applications.** After `platform_ready`, the launch manager starts the
   test applications one after another. Each depends on the previous one and
   counts as ready only once it has terminated with exit code 0:

   | Component                | Binary                   | From showcase       |
   |--------------------------|--------------------------|---------------------|
   | `logging_app`            | `logging_app`            | LoggingApp Demo     |
   | `dlt_generator`          | `dlt_generator`          | LoggingApp Demo     |
   | `log_builtin`            | `log_builtin`            | Baselibs            |
   | `log_custom`             | `log_custom`             | Baselibs            |
   | `log_cpp_init`           | `log_cpp_init`           | Baselibs            |
   | `kyron_safety_task`      | `safety_task`            | Kyron               |
   | `kyron_main_macro`       | `main_macro`             | Kyron               |
   | `com_api_example`        | `com-api-example`        | Communication       |
   | `platform_info_consumer` | `platform_info_consumer` | Platform Version Check |

   The Kyron select example is left out: its assertion depends on which of three
   concurrent jobs finishes first and fails intermittently.
3. **Verdict.** Once the last test application has exited successfully, the
   launch manager reaches the `PlatformRun` run target and logs
   `Completed the request for Run Target PlatformRun`. The component
   `platform_run_passed` prints `S-CORE platform run: PASSED` and stops the
   launch manager with `SIGTERM`.
4. **Failure.** If a test application exits with a non-zero code, terminates
   unexpectedly or does not get ready in time, the launch manager switches to the
   fallback run target. It keeps the `datarouter` and starts
   `platform_run_failed`, which prints `S-CORE platform run: FAILED` and stops
   the launch manager. If `PlatformRun` is not reached within 60 s, `timeout`
   stops the launch manager and the wrapper prints
   `S-CORE platform run: FAILED (PlatformRun not reached within 60 s)`.

## Logging

All processes log via mw::log to the console and, through the datarouter, as DLT
(UDP multicast `239.255.42.99:3490`). Run `dlt-receive` or DLT Viewer next to it
to see them. The launch manager passes each process its own mw::log
configuration via `MW_LOG_CONFIG_FILE`; the launch manager itself reads
[platform_run/logging.json](platform_run/logging.json).

The launch manager logs at debug level to DLT but only at info level to the
console. Its debug messages report every process start and termination.

| DLT app id | Process                  | Context ids                          |
|------------|--------------------------|--------------------------------------|
| `LM`       | launch manager           | `LM`, `lola` (mw::com internals)     |
| `DR`       | datarouter               | `DFLT`, `STAT`                       |
| `EXA`      | `logging_app`            | `DFLT`                               |
| `LGGG`     | `dlt_generator`          | `LOGG`                               |
| `PINS`     | `platform_info_service`  | `PINF`, `lola` (mw::com internals)   |
| `PINC`     | `platform_info_consumer` | `PINF`, `lola` (mw::com internals)   |
| `COMA`     | `com-api-example`        | mw::com internals                    |

Every mw::log client also sends its statistics under context id `STAT`. The
baselibs and Kyron examples log to stdout only.

## Platform integration test

`//platform_integration_tests/platform_run` (part of
`//platform_integration_tests:pit`, Linux x86_64 only) runs the showcase in the
Docker image and checks the DLT traffic:

1. It routes DLT multicast out of the container
   (`ip route add 224.0.0.0/4 dev eth0`) and starts `dlt-receive` on the host
   through the ITF DLT plugin. The recording is written to `platform_run.dlt` in
   the test's undeclared outputs. CI uploads it as artifact
   `platform-run-dlt-<sha>`.
2. It runs the showcase through the showcase CLI. The CLI must exit with 0 and
   report `Example 'S-CORE Platform Run' finished successfully`.
3. **DLT checks.** For every entry in `EXPECTED_DLT` the recording must contain
   at least one message with exactly this app id and context id whose decoded
   payload matches the regular expression:

   | App id | Context id | Payload                                                              |
   |--------|------------|----------------------------------------------------------------------|
   | `DR`   | `DFLT`     | `successfully completed initialization`                              |
   | `EXA`  | `DFLT`     | `Logging Application DoLogging`                                      |
   | `LGGG` | `LOGG`     | `DLT generator finished`                                             |
   | `PINC` | `PINF`     | `platform_info_consumer: S-CORE version check passed`                |
   | `LM`   | `LM`       | `Completed the request for Run Target PlatformRun`                   |
   | `LM`   | `LM`       | `Starting process ( <app> )`, for each test application              |
   | `LM`   | `LM`       | `Process <app> ( pid <n> ) terminated with status 0`, for each test application |

   The test applications are those in the table under [Sequence](#sequence)
   (`TEST_APPS` in the test). The status is the raw wait status, so `0` means
   exit code 0. The per-application checks name the application that did not
   start or failed; the run target check alone only shows that one of them did.
   Platform daemons are not checked this way: the launch manager starts them
   before or while the datarouter comes up, so these messages may not reach
   DLT.

   In addition, the recording must not contain any message from the entries in
   `FORBIDDEN_DLT`, the warnings of the launch manager:

   | App id | Context id | Payload                             |
   |--------|------------|-------------------------------------|
   | `LM`   | `LM`       | `unexpected termination of process` |
   | `LM`   | `LM`       | `Problem discovered`                |
   | `LM`   | `LM`       | `did not meet its ready condition`  |

   The verdict `S-CORE platform run: PASSED` is printed by the showcase's shell
   wrapper and is not checked: it follows from reaching `PlatformRun`.
4. All findings are collected and reported together with the console output.

To add a DLT check, extend `EXPECTED_DLT` or `FORBIDDEN_DLT` in
[test_platform_run.py](../platform_integration_tests/platform_run/test_platform_run.py).
To check a new test application, add it to `launch_manager_config.json`, to the
`PlatformRun` run target and to `TEST_APPS`.