# Eclipse S-CORE on Raspberry Pi OS Lite, Raspberry Pi 4B

The Raspberry Pi OS counterpart of [`../ebclfsa_rpi4b`](../ebclfsa_rpi4b): the 64-bit
Raspberry Pi OS Lite release image (pinned in `bazel_common/score_images.MODULE.bazel`) with the
S-CORE platform (`//deploy:platform_tar`), the showcases (`//showcases:showcases_pkg_tar`) and the
diagnostics service deployed in it. The platform and the showcases are the Linux aarch64 build, so
the image needs `--config=linux-aarch64`:

```bash
bazel build --config=linux-aarch64 //images/rpios_rpi4b:image
```

The result is `bazel-bin/images/rpios_rpi4b/deployed/raspios-rpi4b.wic`. Flash it to an SD card,
for example with the Raspberry Pi Imager ("Use custom") or `dd`.

The build needs no privileges and does not boot the image:

1. `build/prepare.py` grows the root partition of the release image to 4 GiB, so that the files
   fit, and enables the systemd unit of SSH.
2. `../ebclfsa_rpi4b/build/build_image.py`, the same script as for the EB corbos image, writes the
   files with `debugfs` into the root partition: the platform, the showcases, the systemd unit
   `build/diagnostics.service`, which starts the diagnostics stack at boot, and the network
   configuration (see below).

It needs `xz`, `e2fsprogs` (`debugfs`, `e2fsck`, `resize2fs`) and `python3`.

Like the EB corbos image, it allows root login over SSH without a password and is meant for
integration tests, not for production.

## Network

The image has a static address, `192.168.7.2/24` on `eth0`, gateway `192.168.7.1`, set by a
NetworkManager profile in place of the automatic DHCP connection. Set another one at build time:

```bash
SCORE_PI_ADDRESS=10.0.0.20/24 SCORE_PI_GATEWAY=10.0.0.1 bazel build --config=linux-aarch64 //images/rpios_rpi4b:image
```

See [`../network/README.md`](../network/README.md).
