# Platform heartbeat service (communication)

Communication and baselibs ship as libraries. A library cannot be checked from
outside the process that links it, so the platform deploys a small mw::com
service built on both. A consumer in layer 3 has to find that service and
talk to it; if the platform does not deploy it, or deploys something that does
not speak S-CORE communication, the consumer fails.

See [`deploy/README.md`](../README.md) for the layering and the layer 2 /
layer 3 contract this service is part of.

## What is deployed

| Path on target | Content |
| --- | --- |
| `/usr/bin/communication/heartbeat_service` | Provider of the service |
| `/usr/bin/communication/etc/mw_com_config.json` | mw::com configuration of the service; consumers use this deployed file |

## Service `score/platform/heartbeat`

The interface is defined in [`heartbeat.h`](heartbeat.h) and shared by
provider and consumer.

| Element | Kind | Content |
| --- | --- | --- |
| `heartbeat` | event | One `Heartbeat` every 100 ms: sequence number, a payload derived from it and a baselibs CRC32 over both |
| `platform_info` | field | `PlatformInfo`: the S-CORE version the platform was built from, sealed with a baselibs CRC32 |

### S-CORE version (`platform_info`)

`PlatformInfo` holds the `timestamp` of `known_good.json` and, for every
module in its `target_sw` group, the module name and its `version` (or the
pinned commit `hash` if it has no version).

The values are generated at build time: `gen_platform_info.py` turns
`//:known_good.json` into `platform_info_data.h`. Bazel regenerates the header
whenever `known_good.json` changes, so provider and consumer always carry the
versions they were built from. If the data does not fit the fixed-size
`PlatformInfo` (max. 16 modules, see the sizes in `heartbeat.h`), the build
fails.

The service publishes the field before it offers the service and logs the
version on start-up:

```text
heartbeat_service: offering score/platform/heartbeat for S-CORE known_good 2026-08-28T09:19:12Z
  score_baselibs ee40fece5abacb28ea641b448446a04175038b17
  ...
```

## Consumer

[`//showcases/standalone:heartbeat_consumer`](../../showcases/standalone/heartbeat_consumer.cpp)
brings no provider of its own. It exits 0 only if it

1. finds `score/platform/heartbeat` via mw::com service discovery,
2. receives `platform_info` with an intact CRC32,
3. finds the same S-CORE version it was built for (it compiles in the same
   generated header) — otherwise it lists the differing modules, and
4. receives 10 heartbeats with an intact CRC32.

It runs as the showcase `Communication Platform Heartbeat`
([`com_heartbeat.score.json`](../../showcases/standalone/com_heartbeat.score.json)),
which the platform integration test
`test_communication_platform_heartbeat` executes.

## Running it locally

```sh
bazel build --config=linux-x86_64 //deploy/communication:heartbeat_service //showcases/standalone:heartbeat_consumer
mkdir -p /tmp/mw_com_lola/service_discovery
cd deploy/communication
../../bazel-bin/deploy/communication/heartbeat_service &
../../bazel-bin/showcases/standalone/heartbeat_consumer --service_instance_manifest etc/mw_com_config.json
kill %1
```

## Limitations

- The reported version is self-declared. It shows which S-CORE version a
  platform claims to be and catches a wrongly assembled platform, but it is
  no proof of origin; that needs a comparison of the deployed binaries with
  the reference build (hash or SBOM).
- It reflects `known_good.json`, not the patches in `//patches` that are
  applied on top of the pinned commits.
- The showcase still starts the service itself. Starting it at boot is up to
  the image.
