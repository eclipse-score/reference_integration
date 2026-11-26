<!--
Copyright (c) 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at
https://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
-->

# Eclipse S-CORE on Elektrobit corbos Linux for Safety Applications, Raspberry Pi 4B

This is the Raspberry Pi 4B counterpart of [`../ebclfsa_aarch64`](../ebclfsa_aarch64): the
`fastdev` image of the EB corbos toolkit (the same release as for QEMU) with the S-CORE platform
(`//deploy:platform_tar`), the showcases (`//showcases:showcases_pkg_tar`) and the init task of the
diagnostics service deployed in it.

```bash
bazel build --config=eb-aarch64 //images/ebclfsa_rpi4b:image
```

The result is `bazel-bin/images/ebclfsa_rpi4b/build/ebcl-rpi4b-deployed/fastdev-trixie-ebclfsa-rpi4b.wic`.
Flash it to an SD card, for example with the Raspberry Pi Imager ("Use custom") or `dd`.

The QEMU image is deployed by booting it and copying the files in. A Raspberry Pi image cannot be
booted that way, so `build/build_image.py` writes the files with `debugfs` into the root partition
of a copy of the image. This needs `debugfs` (e2fsprogs) and `python3`, and no privileges.

Empty passwords in the base image are locked. Provision unique credentials using the base
image's instructions before enabling remote access, and remove any bundled development keys.
This image is meant for integration tests, not for production.

## Network

The image has a static address, `192.168.7.2/24` on `eth0` (bridge `br0`), gateway `192.168.7.1`,
and no DHCP or link-local fallback. Set another one at build time:

```bash
SCORE_PI_ADDRESS=10.0.0.20/24 SCORE_PI_GATEWAY=10.0.0.1 bazel build --config=eb-aarch64 //images/ebclfsa_rpi4b:image
```

See [`../network/README.md`](../network/README.md). The Raspberry Pi OS image is in
[`../rpios_rpi4b`](../rpios_rpi4b/README.md).
