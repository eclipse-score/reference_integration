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
booted that way, so `build/build_image.sh` writes the files with `debugfs` into the root partition
of a copy of the image. This needs `debugfs` (e2fsprogs) and `python3`, and no privileges.

Like the QEMU image, it allows root login without a password and is meant for integration tests,
not for production.
