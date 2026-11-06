# Platform info service

A platform service of its own, not part of any S-CORE module: it reports the
S-CORE version the platform was built from. It is built on S-CORE
communication (mw::com) and baselibs (CRC32). A consumer in layer 3 has to
find the service and read the version; if the platform does not deploy it,
deploys something that does not speak mw::com, or runs a different S-CORE
version, the consumer fails.

See [`deploy/README.md`](../README.md) for the layering and the layer 2 /
layer 3 contract this service is part of.

## What is deployed

| Path on target | Content |
| --- | --- |
| `/usr/bin/platform_info/platform_info_service` | Provider of the service |
| `/usr/bin/platform_info/etc/mw_com_config.json` | mw::com configuration of the service; consumers use this deployed file |

## Service `score/platform/info`

The interface is defined in [`platform_info.h`](platform_info.h) and shared by
provider and consumer. It has a single field, `platform_info`.

`PlatformInfo` holds the `timestamp` of `known_good.json` and, for every
module in its `target_sw` group, the module name and its `version` (or the
pinned commit `hash` if it has no version), sealed with a baselibs CRC32.

The values are generated at build time: `gen_platform_info.py` turns
`//:known_good.json` into `platform_info_data.h`. Bazel regenerates the header
whenever `known_good.json` changes, so provider and consumer always carry the
versions they were built from. If the data does not fit the fixed-size
`PlatformInfo` (max. 16 modules, see the sizes in `platform_info.h`), the build
fails.

The service publishes the field before it offers the service and logs the
version on start-up:

```text
platform_info_service: offering score/platform/info for S-CORE known_good 2026-08-28T09:19:12Z
  score_baselibs ee40fece5abacb28ea641b448446a04175038b17
  ...
```

## Consumer

[`//showcases/standalone:platform_info_consumer`](../../showcases/standalone/platform_info_consumer.cpp)
brings no provider of its own. It exits 0 only if it

1. finds `score/platform/info` via mw::com service discovery,
2. receives `platform_info` with an intact CRC32, and
3. finds the same S-CORE version it was built for (it compiles in the same
   generated header) — otherwise it lists the differing modules.

On success it logs `platform_info_consumer: S-CORE version check passed`.
It runs as the showcase `Platform Version Check`
([`com_platform_info.score.json`](../../showcases/standalone/com_platform_info.score.json)),
which the platform integration test
`test_platform_version` executes.

## Running it locally

```sh
bazel build --config=linux-x86_64 //deploy/platform_info:platform_info_service //showcases/standalone:platform_info_consumer
mkdir -p /tmp/mw_com_lola/service_discovery
cd deploy/platform_info
../../bazel-bin/deploy/platform_info/platform_info_service &
../../bazel-bin/showcases/standalone/platform_info_consumer --service_instance_manifest etc/mw_com_config.json
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
