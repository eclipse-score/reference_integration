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
(for example `192.168.7.1/24`), then `ssh root@192.168.7.2`.

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

## Changing it afterwards

Edit the file above on the running Raspberry Pi (over ssh) or in the root partition of the `.wic`
file before flashing it, then restart the network or reboot.
