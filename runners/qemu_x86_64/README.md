# QNX QEMU x86 Runner

## Configure QEMU networking

To allow QEMU bridge helper to create TAP devices and to make sure **TUN** is available:

Give qemu-bridge-helper the required capabilities.

Make sure that bridge virbr0 is installed for successful QEMU startup

```bash
sudo apt update
sudo apt install -y libvirt-daemon-system qemu-kvm
sudo systemctl enable --now libvirtd
sudo virsh net-define /usr/share/libvirt/networks/default.xml || true
sudo virsh net-autostart default
sudo virsh net-start default
```

Create /etc/qemu if it doesn’t exist.

```bash
sudo install -d -m 755 /etc/qemu
echo "allow virbr0" | sudo tee /etc/qemu/bridge.conf
```

On Debian/Ubuntu (most common path):

```bash
sudo setcap cap_net_admin,cap_net_raw+ep /usr/lib/qemu/qemu-bridge-helper
```

Verify:

```bash
getcap /usr/lib/qemu/qemu-bridge-helper
# or
getcap /usr/libexec/qemu-bridge-helper
```

You should see:

```bash
/usr/lib/qemu/qemu-bridge-helper = cap_net_admin,cap_net_raw+ep
```

Enable TUN device

Make sure the TUN kernel module is loaded:

```bash
sudo modprobe tun
```

Check that the device exists:

```bash
ls -l /dev/net/tun
```

If successful, you’ll see:

```bash
crw-rw-rw- 1 root root 10, 200 ... /dev/net/tun
```
