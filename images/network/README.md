<!--
Copyright (c) 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at
https://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
-->

# Network of the Raspberry Pi images

Both Raspberry Pi images, `//images/ebclfsa_rpi4b:image` (EB corbos Linux for Safety Applications)
and `//images/rpios_rpi4b:image` (Raspberry Pi OS Lite), have a **static IPv4 address** on `eth0`.
There is no DHCP client and no link-local (`169.254.x.x`) fallback, and IPv6 is disabled. Without
configuration the address is the one of the EB corbos base image:

| | Default |
|---|---|
| Address | `192.168.7.2/24` |
| Gateway | `192.168.7.1` |
| DNS | `8.8.8.8` |

To reach the Raspberry Pi, give the machine that is connected to it an address in the same subnet
(for example `192.168.7.1/24`), then connect using credentials provisioned for the base image.

## Setting the address at build time

Set these environment variables when you run Bazel:

| Variable | Meaning | Default |
|---|---|---|
| `SCORE_PI_ADDRESS` | IPv4 address with prefix length | `192.168.7.2/24` |
| `SCORE_PI_GATEWAY` | IPv4 address of the gateway, empty for none | `192.168.7.1` |
| `SCORE_PI_DNS` | comma separated IPv4 addresses of DNS servers | `8.8.8.8` |

```sh
SCORE_PI_ADDRESS=10.0.0.20/24 SCORE_PI_GATEWAY=10.0.0.1 SCORE_PI_DNS=10.0.0.1,1.1.1.1 \
  bazel build --config=eb-aarch64 //images/ebclfsa_rpi4b:image

SCORE_PI_ADDRESS=10.0.0.20/24 SCORE_PI_GATEWAY=10.0.0.1 \
  bazel build --config=linux-aarch64 //images/rpios_rpi4b:image
```

The values are read by the repository rule in `repo.bzl` (`@score_pi_network`), which writes the
configuration files. A change rebuilds the two files and the images, not the platform. An invalid
value fails the build.

| Image | File in the image |
|---|---|
| EB corbos (`ebclfsa_rpi4b`) | `/etc/config/network` (netifd), replaces the one of the base image |
| Raspberry Pi OS (`rpios_rpi4b`) | `/etc/NetworkManager/system-connections/score-static.nmconnection` (NetworkManager, mode 0600) |

On Raspberry Pi OS the profile takes the place of the automatic DHCP connection of `eth0`.

## The addresses of the diagnostics

The diagnostics showcase is generic and uses `0.0.0.0`. Both Raspberry Pi images replace two of its
configuration files (`//images/network:diagnostics_config_tar`, deployed after the showcases):
the CDA uses the image address and the gateway listens on loopback only.

| File in the image | Setting | With the default address |
|---|---|---|
| `/showcases/data/diagnostics/opensovd-cda.toml` | `tester_address`, `tester_subnet` of the CDA | `192.168.7.2`, `255.255.255.0` |
| `/showcases/data/diagnostics/etc/launch_manager_config.bin` | `SOVD_URL` of the gateway | `http://127.0.0.1:7690/sovd` |

- The CDA sends its DoIP vehicle identification request (VIR) to `255.255.255.255` from its tester
  address. With `0.0.0.0` sending it needs a route: without one (for example with a link-local
  address and no gateway) the CDA stops at startup with `Failed to send VIR: ... Network is
  unreachable`. With the address of the image it is sent on the interface of that address. The CDA
  only accepts vehicle announcements from the subnet of the image.
- The gateway uses development authentication and listens only on loopback, port 7690; it is not
  announced on the network. Use an authenticated SSH tunnel for remote access. The CDA listens on
  the Unix socket `/run/opensovd-cda.sock`; its clients use the gateway.

How the copies are made:

1. `repo.bzl` writes two sed scripts next to the network configuration:
   `@score_pi_network//:diagnostics/cda.sed` and `@score_pi_network//:diagnostics/gateway.sed`.
2. `//images/network:cda_config` runs `cda.sed` over the CDA configuration of the showcase
   (`//showcases/diagnostics:cda_config`, which is `showcases/diagnostics/cda-config.toml` with
   the settings of the ECUs from `score_diagnostics` appended). `//images/network:launch_manager_json`
   runs `gateway.sed` over `showcases/diagnostics/launch_manager_config.json`, and
   `//images/network:launch_manager_config` compiles the result into the binary `.bin`. Each step
   fails the build if the required settings are missing or the gateway is not restricted to loopback.
3. `//images/network:diagnostics_config_tar` packs both files, and the build of each Raspberry Pi
   image deploys it after the showcases, so they overwrite the generic files.

The source files of the showcase keep `0.0.0.0` and are not changed: the QEMU image and the
platform packages use them as they are.

## Changing it afterwards

Edit the file above on the running Raspberry Pi (over ssh) or in the root partition of the `.wic`
file before flashing it, then restart the network or reboot. The diagnostics keep the address they
were built with: change `tester_address` and `tester_subnet` in
`/showcases/data/diagnostics/opensovd-cda.toml` to match. The gateway remains on loopback.
