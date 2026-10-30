# Platform deployment (layer 2)

The image content of this distribution is split into three layers:

| Layer | Location | Content |
| --- | --- | --- |
| 1 — Image | `//images/<variant>` | Boot, kernel, drivers, root filesystem skeleton |
| 2 — Platform | `//deploy` | The S-CORE modules as deployed — the system under test |
| 3 — Showcases | `//showcases` | Applications that demonstrate and verify the platform |

A production image ships layers 1 and 2. Layer 3 must be removable without
changing either of them.

## Why layer 2 and layer 3 are separate

The showcases are the probe, the platform is the probe's subject. If a
showcase shipped the component it exercises — as the lifecycle showcase did
with the launch manager before this split — then the check would be verifying
the binary it brought along rather than the one the distribution deployed. A
distribution that fails to deploy an S-CORE module would still pass.

Keeping them apart gives the property that makes the checks meaningful: the
showcase applications run against whatever platform the image provides, and
fail when it is missing.

That is also why a module's binaries can end up in different layers. The
lifecycle launch manager is deployed here; the applications it supervises,
and the launch manager configuration that declares them, live in
`//showcases/simple_lifecycle`.

## Contract between layer 2 and layer 3

Layer 3 may rely on the following, and on nothing else:

| Component | Deployed location |
| --- | --- |
| `launch_manager` | `/usr/bin/launch_manager` |
| `datarouter` | `/usr/bin/datarouter/datarouter`, config in `/usr/bin/datarouter/etc` |
| `config_daemon` | `/usr/bin/config_management/config_daemon`, config in `/usr/bin/config_management/etc` |
| `heartbeat_service` | `/usr/bin/communication/heartbeat_service`, config in `/usr/bin/communication/etc`; offers the mw::com service `score/platform/heartbeat` with the `heartbeat` event and the `platform_info` field, which reports the S-CORE module versions from `known_good.json` (interface in `deploy/communication/heartbeat.h`) |

There is no system-wide mw::com configuration: mw::com reads
`./etc/mw_com_config.json` relative to the working directory, or the file
passed with `-s`. mw::log only has an optional ECU-wide
`/etc/ecu_logging_config.json`; the application configuration
(`etc/logging.json` next to the executable or in the working directory, or
`MW_LOG_CONFIG_FILE`) belongs to the application. Every application ships its
own configuration.

Layer 2 never references anything under `/showcases`. The one place where
layer 2 reads layer 3 data is the launch manager, which is started by the
showcase with a working directory that holds the showcase's own
configuration — the configuration is passed in, not deployed alongside the
daemon.

## Adding a module

Add a `deploy/<module>/BUILD` that packages the module's binaries and
configuration with `pkg_files`, then list those targets in
`//deploy:platform_bundle`. Configuration that is deployed onto the target
is kept in `deploy/<module>/etc/`, not in a test directory. Keep examples,
demo applications and test binaries out; those belong in `//showcases`.
Modules that ship only libraries (for example persistency) have nothing to
deploy and get no package here. Communication is the exception: a library
cannot be checked from outside the process that links it, so the platform
deploys a heartbeat service built on it. The communication showcase consumes
that service and fails unless the platform provides it.

Long term each S-CORE module should export its own deployment package
upstream, so that "deployed correctly" becomes checkable rather than agreed.
Until then this directory is the distribution's local stand-in for it.
