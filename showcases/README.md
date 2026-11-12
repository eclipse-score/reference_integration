# Logging App Demo
 
This Logging App demonstrates logging using mw::log with all log levels and configured backends (kConsole|kRemote|kFile) enabled.

For remote (DLT) logging, please refer to the following documentation:
 
[Remote logging](https://github.com/eclipse-score/logging/blob/main/score/datarouter/doc/guideline/dlt_capture_demo.md)

# Drive Replay Demo

A scripted 40 s highway lap is replayed on the target (e.g. a Raspberry Pi) into a forward
collision warning. All processes run under the launch manager:

| Process | DLT app id | Role |
|---|---|---|
| `launch_manager` | `LM` (console only) | starts the Run Target `Drive`, supervises `warn_app` |
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
* Log panel: topic `/log` (DLT messages of DSM, RPLY, FCW and the datarouter)

The launch manager needs POSIX ACL support on `/dev/shm` (alive supervision). Docker Desktop
(linuxkit kernel) does not provide it; Raspberry Pi OS and Ubuntu do.