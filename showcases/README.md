# Logging App Demo
 
This Logging App demonstrates logging using mw::log with all log levels and configured backends (kConsole|kRemote|kFile) enabled.

For remote (DLT) logging, please refer to the following documentation:
 
[Remote logging](https://github.com/eclipse-score/logging/blob/main/score/datarouter/doc/guideline/dlt_capture_demo.md)

# Drive Replay Demo

A scripted 40 s highway lap is replayed on the target (e.g. a Raspberry Pi) into a forward
collision warning. All processes run under the launch manager:

| Process | DLT app id | Role |
|---|---|---|
| `launch_manager` | `LM` | starts the Run Target `Drive`, supervises `warn_app` |
| `datarouter` | `DR` | streams all logs as DLT to `239.255.42.99:3490` |
| `drive_state_manager` | `DSM` | reports Run Target changes, requests `Drive` again after a recovery |
| `replay_app` | `RPLY` | publishes the drive frames via `mw::com` (`score/showcases/drive_replay/DriveData`) |
| `warn_app` | `FCW` | computes the time to collision, heartbeat to the health monitor, counters in the persistency KVS |

If `warn_app` hangs or crashes, the launch manager switches to the degraded
`fallback_run_target` (drive continues, warning off). The state manager requests `Drive`
again after 3 s; the restarted `warn_app` restores its counters from the KVS.

On the target:

```sh
# scripted (~65 s, hang after 20 s, crash after 45 s): select it in the showcase CLI
# live, until Ctrl-C:
cd /showcases/data/drive_replay && /usr/bin/launch_manager
# inject a fault from a second shell:
/showcases/bin/lifecycle_signal.sh warn_app SIGUSR1   # hang (no more heartbeats)
/showcases/bin/lifecycle_signal.sh warn_app SIGKILL   # crash
```

The apps send their live data as JSON via UDP to `239.255.42.99:9001`; to use unicast instead, add
`DRIVE_VIZ_ADDR=<ip>:<port>` to the `environmental_variables` of the apps in
[drive_replay/configs/launch_manager_config.json](drive_replay/configs/launch_manager_config.json).

On the laptop in the same network:

```sh
pip install -r showcases/drive_replay/viz/requirements.txt
python3 showcases/drive_replay/viz/foxglove_bridge.py --interface <laptop ip>
```

In Lichtblick open the connection `Foxglove WebSocket` -> `ws://127.0.0.1:8765` and add:

* 3D panel: topic `/scene`, display frame `ego`
* Plot panel: `/adas/fcw.ttc`, `/drive/frame.gap`, `/drive/frame.ego_kmh`, `/drive/frame.lead_kmh`
* State Transitions panel: `/system/state.run_target`, `/adas/fcw.level`
* Indicator panel: `/system/health.fcw_alive`
* Log panel: topic `/log` (DLT messages of LM, DSM, RPLY, FCW and the datarouter)

The launch manager needs POSIX ACL support on `/dev/shm` (alive supervision). Docker Desktop
(linuxkit kernel) does not provide it; Raspberry Pi OS and Ubuntu do.

## Platform integration test

`//platform_integration_tests/drive_replay` (Linux x86_64) runs the scripted showcase and
records its DLT traffic; CI uploads it as artifact `drive-replay-dlt-<sha>` (open it in the
DLT Viewer). The test checks the chain in the trace: drive and warnings (`RPLY`, `FCW`),
exactly one supervision failure of `warn_app` and only after the injected hang, two
recoveries (`LM` `fallback_run_target`, `DSM` requesting `Drive`, `LM` `Drive` again) and
the restarted `warn_app` restoring its counters (`start #3, restored warn_count>0`).

# S-CORE Platform Run

`/showcases/bin/cli --examples 'S-CORE Platform Run'` starts the launch manager
with [platform_run/launch_manager_config.json](platform_run/launch_manager_config.json).
It starts the datarouter and the platform info service, then the test
applications one after another; each must exit with code 0. Once all have, the
launch manager reaches the run target `PlatformRun` and the run prints
`S-CORE platform run: PASSED`, otherwise `FAILED` (at the latest after 60 s).

All processes log via mw::log to the console and as DLT through the datarouter
(UDP multicast `239.255.42.99:3490`). The launch manager logs at debug level to
DLT ([platform_run/logging.json](platform_run/logging.json)), including every
process start and termination.

## Platform integration test

`//platform_integration_tests/platform_run` (Linux x86_64) records the DLT
traffic while the showcase runs; CI uploads it as artifact
`platform-run-dlt-<sha>`. The test requires the `PASSED` line on the console,
no `FAILED` line, and in the DLT trace:

| App id / context | Expected payload                                                            |
|------------------|-----------------------------------------------------------------------------|
| `DR` / `DFLT`    | `successfully completed initialization`                                     |
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
