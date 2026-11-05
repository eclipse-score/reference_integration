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
Modules that ship only libraries (for example communication or persistency)
have nothing to deploy and get no package here.

Long term each S-CORE module should export its own deployment package
upstream, so that "deployed correctly" becomes checkable rather than agreed.
Until then this directory is the distribution's local stand-in for it.

## Release downloads: layer 2 and layer 3 separately

Every GitHub release carries both upper layers as separate downloads, one
pair of archives per target the CI builds. QNX archives are not published:
they contain binaries built with the licensed QNX SDP.

| Target | Layer 2 (platform) | Layer 3 (showcases) | Built with |
| --- | --- | --- | --- |
| Linux x86_64 | `score-platform-linux-x86_64.tar.gz` | `score-showcases-linux-x86_64.tar.gz` | `--config=linux-x86_64` |
| Linux aarch64 | `score-platform-linux-aarch64.tar.gz` | `score-showcases-linux-aarch64.tar.gz` | `--config=linux-aarch64` |
| AutoSD x86_64 | `score-platform-autosd-x86_64.tar.gz` | `score-showcases-autosd-x86_64.tar.gz` | `--config=autosd-x86_64` |
| EB corbos aarch64 | `score-platform-eb-aarch64.tar.gz` | `score-showcases-eb-aarch64.tar.gz` | `--config=eb-aarch64` |

The platform archive is `//deploy:platform_tar` (unpacks to `/usr/bin/...`),
the showcases archive is `//showcases:showcases_pkg_tar` (unpacks to
`/showcases`). Both are relative to `/`:

```sh
tar -xzf score-platform-<target>.tar.gz -C /     # only if the image does not ship S-CORE itself
tar -xzf score-showcases-<target>.tar.gz -C /
/showcases/bin/cli --examples all
```

To check an image that claims to ship S-CORE, copy only the showcases
archive onto it. The showcases then run against whatever platform the image
deploys, without rebuilding it — as long as it fulfils the contract above.

### Linux aarch64, e.g. Raspberry Pi 4

The Linux aarch64 archives are built with the S-CORE GCC 12.2 toolchain
(glibc 2.31 sysroot). They need glibc 2.31 or newer and, for the Rust
showcases, the system's `libstdc++` from GCC 12 or newer — for example
Raspberry Pi OS Lite (64-bit, Bookworm or newer), Debian 12 or Ubuntu 22.04
arm64 and newer. They contain
no part of the operating system or the board firmware; installing those is up
to the owner of the device.

1. Flash Raspberry Pi OS Lite (64-bit) with the Raspberry Pi Imager and enable SSH.
2. Copy both archives of a release to the Pi and install them:

   ```sh
   sudo tar -xzf score-platform-linux-aarch64.tar.gz -C /
   sudo tar -xzf score-showcases-linux-aarch64.tar.gz -C /
   ```

3. Run the showcases: `sudo /showcases/bin/cli --examples all`.

The showcases start the platform daemons they need themselves; nothing has to
be started beforehand. CI runs exactly these steps on a stock Ubuntu 24.04
arm64 runner (`build_and_test_linux.yml`, job `aarch64-run`).
