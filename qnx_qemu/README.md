# QNX QEMU x86 Minimal Image

## Overview

This project provides a minimal QNX 8.0 image designed to run on x86_64 QEMU virtual machines. It's specifically configured for the Eclipse SCORE (Safety Critical Object-Oriented Real-time Embedded) project, offering a lightweight yet functional QNX environment suitable for development, testing, and demonstration purposes.

## Quick Start Guide

### 1. Prerequisites

Before starting, ensure the following tools are available on your Linux host:

- **Bazel**
- **QEMU** (with `qemu-bridge-helper` installed at `/usr/lib/qemu/qemu-bridge-helper`)
- Valid **QNX SDP 8.0 license** from <https://www.qnx.com/>. See this YT video for more info <https://www.youtube.com/watch?v=DtWA5E-cFCo>

### 2. Installation/ Configuration

- **Clone the integration & toolchain repos**

```bash
git clone https://github.com/eclipse-score/reference_integration.git
git clone https://github.com/eclipse-score/toolchains_qnx.git
cd reference_integration/qnx_qemu
```

Toolchain repo contains the Bazel rules and credential helper used to download and register the QNX SDP toolchain.

- **Provide QNX download credentials**

You can pass credentials via environment variables.

```bash
export SCORE_QNX_USER="<qnx_username>"
export SCORE_QNX_PASSWORD="<qnx_password>"
```

- **Download QNX Software Center for Linux**

**Using GUI:**

Download **QNX Software Center 2.0.4 Build 202501021438 - Linux Hosts** from the [QNX Software Center page](https://www.qnx.com/download/group.html?programid=29178), then install it.

**Using CLI:**

URL to installer must be determined manually:

- Go to [QNX page]<https://blackberry.qnx.com/en> and log in using "SIGN IN".

- Go to [QNX Software Center page]<https://www.qnx.com/download/group.html?programid=29178>.

- Scroll down and click the link labeled `QNX Software Center <VERSION> Build <BUILD_NUMBER> - Linux Hosts`.

- Right-click "Download Now" button and copy the installer URL.

- Verify installer checksum after download!

```bash
# Create directory.
mkdir ~/.qnx 
# Log-in and download installer.
curl -v --cookie-jar ~/.qnx/myqnxcookies.auth --form "userlogin=$SCORE_QNX_USER" --form "password=$SCORE_QNX_PASSWORD" https://www.qnx.com/account/login.html -o login_response.html
curl -v -L --cookie ~/.qnx/myqnxcookies.auth installer_URL  > qnx-setup-lin.run
# Verify checksum.
sha256sum qnx-setup-lin.run
# Make the installer executable.
chmod +x ./qnx-setup-lin.run
# Run installer.
~/qnx-setup-lin.run force-override disable-auto-start agree-to-license-terms ~/qnxinstall
```

- **Download QNX SDP 8.0**

**Using GUI:**

Using **QNX Software Center - Linux Hosts** we previously installed , install **QNX Software Development Platform 8.0**.

**Using CLI:**

```bash
cd ~/qnxinstall/qnxsoftwarecenter
./qnxsoftwarecenter_clt -syncLicenseKeys -myqnx.user="$SCORE_QNX_USER" -myqnx.password="$SCORE_QNX_PASSWORD" -addLicenseKey license_key -listLicenseKeys
./qnxsoftwarecenter_clt -mirrorBaseline="qnx800" -myqnx.user="$SCORE_QNX_USER" -myqnx.password="$SCORE_QNX_PASSWORD"
./qnxsoftwarecenter_clt -cleanInstall -destination ~/qnx800 -installBaseline com.qnx.qnx800 -myqnx.user="$SCORE_QNX_USER" -myqnx.password="$SCORE_QNX_PASSWORD"
cd - > /dev/null
```

This contains the toolchains and `license` folder required for activation.
check this QNX link for more info <https://www.qnx.com/developers/docs/qsc/com.qnx.doc.qsc.inst_larg_org/topic/create_headless_installation_linux_macos.html>

- **Source SDP environment**

```bash
source ~/qnx800/qnxsdp-env.sh 
#The commands below confirm the environment was sourced successfully.
echo "$QNX_HOST" "$QNX_TARGET"
```

- **Register QNX license**

```bash
sudo mkdir -p /opt/score_qnx/license
sudo cp ~/.qnx/license/licenses /opt/score_qnx/license/licenses
sudo chmod 644 /opt/score_qnx/license/licenses
```

OR we can use symbolic linking

```bash
sudo install -d -m 755 /opt/score_qnx/license
LIC_SRC="$(readlink -f "$HOME/.qnx/license/licenses")"
sudo ln -sfn "$LIC_SRC" /opt/score_qnx/license/licenses
chmod 644 "$LIC_SRC"
```

- **Configure QEMU networking**

to allow QEMU bridge helper to create TAP devices and to make sure **TUN** is available:

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

### 3. Build & run the QNX image on qemu

Run Bazel with the credential helper:

```bash
bazel build --config=x86_64-qnx \
  --credential_helper=*.qnx.com=$(pwd)/../toolchains_qnx/tools/qnx_credential_helper.py \
  //build:init
```

- First run downloads ~1.6 GiB of QNX SDP

- Resulting IFS: `bazel-bin/build/init.ifs`

at this stage Build shall succeed.

- **Run QNX in QEMU**

verify bridge virbr0 is up and running

```bash
ip link show virbr0
```

- QEMU can use KVM for near-native performance. The wrapper below auto-enables **KVM** when available and falls back to **TCG** with a visible warning if /dev/kvm isn’t accessible

```bash
sudo tee /usr/local/bin/qemu-system-x86_64 >/dev/null <<'EOF'
#!/usr/bin/env bash
# Smart QEMU shim: auto-enable KVM when possible; warn & fall back otherwise.
set -euo pipefail
REAL="${QEMU_BIN:-/usr/bin/qemu-system-x86_64}"

have_kvm() {
  [[ -e /dev/kvm && -r /dev/kvm && -w /dev/kvm ]] || return 1
  [[ -d /sys/module/kvm ]] && { [[ -d /sys/module/kvm_intel || -d /sys/module/kvm_amd ]] ; } || true
}

args=("$@")
want_kvm=false
for a in "${args[@]}"; do
  [[ "$a" == "--enable-kvm" ]] && want_kvm=true
done

if have_kvm; then
  $want_kvm || args+=(--enable-kvm)
else
  # Strip any --enable-kvm and warn
  filtered=()
  for a in "${args[@]}"; do
    [[ "$a" == "--enable-kvm" ]] && continue
    filtered+=("$a")
  done
  args=("${filtered[@]}")
  echo "Warning: KVM not available: /dev/kvm missing or not accessible; using software emulation (TCG)." >&2
  sleep 2  # fixed 2s pause so the warning is visible
fi

exec "$REAL" "${args[@]}"
EOF
```

make the script executable

```bash
sudo chmod +x /usr/local/bin/qemu-system-x86_64
```

Tip: ensure /usr/local/bin comes before /usr/bin so the wrapper is used:

```bash
export PATH=/usr/local/bin:$PATH
hash -r
```

- Run QEMU

```bash
bazel run --config=x86_64-qnx //:run_qemu
```

## Features

### Core System Components

- **QNX 8.0 Neutrino RTOS** - Real-time operating system with SMP support
- **x86_64 Architecture** - Optimized for modern 64-bit Intel/AMD processors
- **Multiboot Support** - Compatible with GRUB and other multiboot loaders
- **56MB Image Size** - Compact footprint while maintaining essential functionality
- **Host: Ubuntu 24.04** - Developed and tested on Ubuntu 24.04 as host machine

### Networking Capabilities

- **VirtIO Network Driver** - High-performance virtualized networking
- **Bridge Networking** - Direct network access with configurable IP
- **Port Forwarding** - Alternative NAT-based networking mode
- **SSH Server** - Remote access with passwordless authentication
- **DHCP Client** - Automatic IP configuration with dhcpcd
- **Network Packet Capture** - tcpdump integration with Wireshark support
- **ICMP Support** - Ping connectivity for network testing
- **SFTP Server** - Secure file transfer capabilities

### Development Tools

- **Toybox Utilities** - Comprehensive set of Unix command-line tools
- **Shell Environment** - Korn shell (ksh) with standard Unix tools
- **SSH Client/Server** - Full SSH stack for remote development
- **OpenSSL** - Cryptographic libraries and tools
- **File System Support** - QNX6 and DOS file systems

### Storage and I/O

- **RAM Disk** - 10MB temporary storage with 512KB cache
- **IDE/SATA Support** - Block device access for persistent storage
- **Serial Console** - 115200 baud serial interface for debugging
- **PCI Hardware Support** - Comprehensive PCI device management

### Security Features

- **User Management** - Root and regular user accounts
- **SSH Key Authentication** - RSA host keys pre-configured
- **File Permissions** - Standard Unix-style permissions
- **Chroot Environment** - SSH privilege separation

## Directory Structure

```text
qnx_qemu/
├── README.md                          # This documentation file
├── BUILD                              # Bazel build configuration with multiple run targets
├── MODULE.bazel                       # Bazel module configuration
├── .bazelrc                           # Bazel configuration file
│
├── build/                             # Image build definitions
│   ├── BUILD                          # Build targets for QNX image creation
│   ├── init.build                     # IFS (Image FileSystem) definition
│   └── system.build                   # System content definition (libraries, tools, configs)
│
├── configs/                           # Configuration files and scripts
│   ├── BUILD                          # Build configuration for config files
│   ├── startup.sh                     # Main system startup script
│   ├── network_setup.sh               # Standard network configuration
│   ├── network_setup_dhcp.sh          # DHCP-based network configuration
│   ├── network_capture.sh             # Network packet capture utility
│   ├── dhcpcd.conf                    # DHCP client configuration
│   ├── sshd_config                    # SSH daemon configuration (passwordless)
│   ├── ssh_host_rsa_key               # SSH server private key
│   ├── ssh_host_rsa_key.pub           # SSH server public key
│   ├── pci_server.cfg                 # PCI bus server configuration
│   ├── pci_hw.cfg                     # PCI hardware configuration
│   ├── qcrypto.conf                   # Cryptographic library configuration
│   ├── passwd                         # User account database
│   ├── group                          # Group membership database
│   ├── hostname                       # System hostname definition
│   └── profile                        # Shell environment configuration
│
├── scripts/                           # Utility scripts
│   ├── run_qemu.sh                    # QEMU launcher with bridge networking
│   ├── run_qemu_portforward.sh        # QEMU launcher with port forwarding
│   └── qnx_wireshark.sh               # Wireshark integration for network analysis
│
└── test/                              # Testing framework
   ├── test_qnx_qemu_bridge.sh        # Bridge networking integration tests
   └── test_qnx_qemu_portforward.sh   # Port forwarding integration tests
```

### Key Files Explained

- **`init.build`** - Defines the bootable image structure, kernel parameters, and essential boot-time utilities
- **`system.build`** - Specifies all system libraries, tools, and configuration files for the running system
- **`startup.sh`** - Orchestrates system service initialization (logging, PCI, networking, SSH)
- **`network_setup.sh`** - Configures network interfaces with static IP addressing
- **`network_setup_dhcp.sh`** - Configures network interfaces with DHCP
- **`network_capture.sh`** - Network packet capture tool with Wireshark integration
- **`run_qemu.sh`** - Launches QEMU with bridge networking for direct IP access
- **`run_qemu_portforward.sh`** - Launches QEMU with port forwarding (NAT networking)
- **`qnx_wireshark.sh`** - Host-side script for Wireshark network analysis integration
- **`test_qnx_qemu_bridge.sh`** - Automated testing for bridge networking mode
- **`test_qnx_qemu_portforward.sh`** - Automated testing for port forwarding mode

## Building the Image

### Prerequisites

- Bazel build system
- QNX SDP (Software Development Platform) toolchain
- Linux host system with KVM support

### Build Commands

```bash
# Build the QNX image
bazel build --config=x86_64-qnx //build:init

# Build and run QEMU with bridge networking
bazel run --config=x86_64-qnx //:run_qemu

# Build and run QEMU with port forwarding
bazel run --config=x86_64-qnx //:run_qemu_portforward

# Run integration tests for bridge networking
bazel run --config=x86_64-qnx //:test_qemu_bridge

# Run integration tests for port forwarding
bazel run --config=x86_64-qnx //:test_qemu_portforward

# Run ITF tests for ssh
bazel test --config=qemu-integration //:test_ssh_qemu --test_output=streamed
```

In order to provide credentials for qnx.com pass to bazel command:

```bash
--credential_helper=*.qnx.com=<path_to_toolchains-qnx>/tools/qnx_credential_helper.py
```

See more in [toolchains_qnx README](https://github.com/eclipse-score/toolchains_qnx?tab=readme-ov-file#using-pre-packaged-qnx-80-sdp).

## Running the System

### Using Bazel (Recommended)

#### Bridge Networking Mode

```bash
# Start the QNX system with bridge networking (direct IP access)
bazel run --config=x86_64-qnx //:run_qemu
```

This mode provides:

- Direct IP access to QNX system
- Ping connectivity from host
- SSH access via direct IP e.g.: `ssh root@192.168.122.100`

#### Port Forwarding Mode

```bash
# Start the QNX system with port forwarding (NAT networking)
bazel run --config=x86_64-qnx //:run_qemu_portforward
```

This mode provides:

- SSH access via port forwarding: `ssh -p 2222 root@localhost`
- HTTP port forwarding: `localhost:8080` → `guest:80`
- HTTPS port forwarding: `localhost:8443` → `guest:443`
- Packet capture port: `localhost:9999` → `guest:9999`

### Manual QEMU Execution

#### Bridge Networking

```bash
qemu-system-x86_64 \
    -smp 2 \
    --enable-kvm \
    -cpu Cascadelake-Server-v5 \
    -m 1G \
    -nographic \
    -kernel path/to/ifs_image \
    -serial mon:stdio \
    -object rng-random,filename=/dev/urandom,id=rng0 \
    -netdev bridge,id=net0,br=virbr0 \
    -device virtio-net-pci,netdev=net0 \
    -device virtio-rng-pci,rng=rng0
```

#### Port Forwarding

```bash
qemu-system-x86_64 \
    -smp 2 \
    --enable-kvm \
    -cpu Cascadelake-Server-v5 \
    -m 1G \
    -nographic \
    -kernel path/to/ifs_image \
    -serial mon:stdio \
    -object rng-random,filename=/dev/urandom,id=rng0 \
    -netdev user,id=net0,hostfwd=tcp::2222-:22,hostfwd=tcp::8080-:80,hostfwd=tcp::8443-:443,hostfwd=tcp::9999-:9999 \
    -device virtio-net-pci,netdev=net0 \
    -device virtio-rng-pci,rng=rng0
```

### QEMU Parameters Explained

- **`-smp 2`** - Enable 2 CPU cores for SMP support
- **`--enable-kvm`** - Use hardware virtualization for better performance
- **`-cpu Cascadelake-Server-v5`** - Emulate modern Intel CPU features for older Ubuntu versions change that to `-cpu host` in case of errors
- **`-m 1G`** - Allocate 1GB of RAM
- **`-nographic`** - Disable graphical display (console-only)
- **`-netdev bridge`** - Connect to host bridge network for direct IP access
- **`-device virtio-net-pci`** - Use VirtIO network driver for optimal performance
- **`-device virtio-rng-pci`** - Provide hardware random number generation

## Network Configuration

### Default Network Settings

#### Bridge Network Configuration

- **IP Address**: DHCP client for QNX SDP 8.0 is dhcpcd. It also provides the IPv4 Link Local addressing and IPv6 Router Solicitation functionality that was previously provided by autoipd
- **Subnet Mask**: `255.255.255.0`
- **Network Interface**: `vtnet0` (VirtIO network)
- **SSH Port**: `22`

#### Port Forward Network Configuration

- **IP Address**: `10.0.2.15` (QEMU user networking)
- **Subnet Mask**: `255.255.255.0`
- **Network Interface**: `vtnet0` (VirtIO network)
- **SSH Port**: `22` (forwarded to host port `2222`)

### Changing the IP Address

To modify the default IP address, edit the network configuration:

1. **Edit network setup script**:

   ```bash
   vim configs/network_setup.sh
   ```

2. **Example on modify the IP configuration line**:

   ```bash
   # Change this line to your desired IP
   ifconfig vtnet0 192.168.122.100 netmask 255.255.255.0

   # Example: Change to 192.168.1.50
   ifconfig vtnet0 192.168.1.50 netmask 255.255.255.0
   ```

3. **Update test script IP** (if using tests):

   ```bash
   vim test/test_qnx_qemu_bridge.sh
   ```

   Change the default IP in the bridge test script:

   ```bash
   QNX_IP=${QNX_IP:-192.168.1.50}  # Update default IP
   ```

4. **Rebuild the image**:

   ```bash
   bazel build --config=x86_64-qnx //build:init
   ```

### Network Bridge Setup (Host)

For direct IP access, ensure your host has a bridge network configured:

```bash
# Create bridge (if not exists)
sudo ip link add name virbr0 type bridge
sudo ip link set virbr0 up
sudo ip addr add 192.168.122.1/24 dev virbr0

# Enable IP forwarding
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

In case of failed to parse default acl file /etc/qemu/bridge.conf'

1. Check acl of `/etc/qemu/bridge.conf`
2. If file does not exist; create that file and add the following line in it
`allow virbr0`
3. Run qemu with Sudo as debug option in case of failure with acl

In case of error "Operation not permitted" for `qemu-bridge-helper` run

```bash
sudo chmod u+s /usr/lib/qemu/qemu-bridge-helper
```

## User Accounts and Access

### Available Users

| Username | UID | GID | Home Directory | Shell | Password |
|----------|-----|-----|----------------|-------|----------|
| root | 0 | 0 | / | /bin/sh | None (passwordless) |
| qnxuser | 1000 | 1000 | / | /bin/sh | None (passwordless) |
| sshd | 15 | 6 | / | /bin/false | N/A (service account) |

### SSH Access

The system is configured for passwordless SSH access:

#### SSH via Bridge Network

```bash
# Connect via bridge network (DHCP or fallback IP)
ssh root@192.168.122.100  # If using fallback IP
# OR check actual DHCP-assigned IP first:
# ssh root@<dhcp-assigned-ip>

# Connect as regular user
ssh qnxuser@192.168.122.100  # If using fallback IP
```

#### SSH via Port Forwarding

```bash
# Connect via port forwarding (recommended for NAT networking)
ssh -p 2222 root@localhost

# Connect as regular user via port forwarding
ssh -p 2222 qnxuser@localhost
```

**Note**: No password is required. The system accepts empty passwords for simplicity in development environments.

## Testing

### Automated Test Suite

The project includes comprehensive test suites for both networking modes that validate:

- System boot and initialization
- Network connectivity (ping tests for bridge mode)
- SSH server functionality
- System service status
- File system operations
- Network-specific features

### Running Tests

#### Bridge Networking Tests

```bash
# Run bridge networking test suite
bazel run --config=x86_64-qnx //:test_qemu_bridge

# Run with custom parameters
bazel run --config=x86_64-qnx //:test_qemu_bridge -- --timeout=120 --boot-wait=20 --qnx-ip=192.168.1.50
```

#### Port Forwarding Tests

```bash
# Run port forwarding test suite
bazel run --config=x86_64-qnx //:test_qemu_portforward

# Run with custom parameters
bazel run --config=x86_64-qnx //:test_qemu_portforward -- --timeout=120 --boot-wait=20
```

### Test Script Options

#### Bridge Networking Test Options

```bash
./test_qnx_qemu_bridge.sh <qnx_host> <ifs_image> [options]

Options:
  --timeout=N       Boot timeout in seconds (default: 120)
  --ssh-port=N      SSH port for testing (default: 2222)
  --ssh-user=USER   SSH user for testing (default: root)
  --boot-wait=N     Additional wait after boot (default: 15)
  --qnx-ip=IP       QNX system IP for ping test (default: 192.168.122.100)
  --no-ssh          Skip SSH connectivity test
  --no-ping         Skip ping connectivity test
  --help            Show help message
```

#### Port Forwarding Test Options

```bash
./test_qnx_qemu_portforward.sh <qnx_host> <ifs_image> [options]

Options:
  --timeout=N       Boot timeout in seconds (default: 120)
  --ssh-port=N      SSH port for testing (default: 2222)
  --ssh-user=USER   SSH user for testing (default: root)
  --boot-wait=N     Additional wait after boot (default: 15)
  --no-ssh          Skip SSH connectivity test
  --help            Show help message

Note: Port forwarding mode does not support ping tests due to NAT networking.
```

### Expected Test Output

```text
============================================================
QNX QEMU Integration Test
============================================================
QNX Host: /path/to/qnx/host
IFS Image: /path/to/ifs/image
Timeout: 90s
QNX IP: 192.168.122.100
SSH Port: 2222
SSH User: root
Ping Test: Enabled
Boot Wait: 15s

1. Starting QEMU with bridge networking...
✓ QEMU started (PID: 12345)
✓ Bridge networking: 192.168.122.100 (for ping test)
✓ SSH port forwarding: localhost:2222 -> guest:22

2. Waiting for boot completion (timeout: 90s)...
Waiting for hostname confirmation: 'Hostname set to: Qnx_S-core'
✓ Boot completion detected: Found hostname confirmation
✓ System fully booted and hostname configured

3. Waiting for system stabilization (15s)...
✓ Stabilization wait completed

4. Testing ping connectivity to QNX system...
Testing ping to 192.168.122.100...
✓ Ping test successful - QNX system is reachable at 192.168.122.100
Ping statistics:
PING 192.168.122.100 (192.168.122.100) 56(84) bytes of data.
64 bytes from 192.168.122.100: icmp_seq=1 ttl=64 time=0.234 ms
64 bytes from 192.168.122.100: icmp_seq=2 ttl=64 time=0.187 ms
64 bytes from 192.168.122.100: icmp_seq=3 ttl=64 time=0.198 ms

5. Testing system functionality...
✓ QEMU process is still running
✓ Found system indicator: qnx
✓ Found system indicator: Welcome
✓ Found system indicator: startup
✓ System functionality indicators found (3)

6. Testing SSH connectivity...
Testing SSH port connectivity on localhost:2222...
✓ SSH port 2222 is open on localhost
Testing direct SSH connection to QNX system...
Attempting SSH connection to root@192.168.122.100...
✓ SSH connection to 192.168.122.100 successful
✓ Checked /tmp/hostname contents

7. Final system status...
✓ QEMU process is running (PID: 12345)

Recent system output:
----------------------------------------
---> Starting sshd
Hostname set to: Qnx_S-core
#
----------------------------------------

============================================================
✓ ALL TESTS PASSED
QNX QEMU integration is working correctly!
QEMU is running on PID: 12345
QNX system IP: 192.168.122.100 (pingable)
SSH port forwarding: localhost:2222 -> guest:22
============================================================
```

### Test Failure Scenarios

If tests fail, check:

1. **Boot Timeout**: Increase `--timeout` value
2. **Network Issues**: Verify bridge setup and IP configuration
3. **SSH Problems**: Check SSH daemon startup and port forwarding
4. **Host Permissions**: Ensure user can access KVM and bridge networking

## System Capabilities

### Available Commands

The system includes a comprehensive set of Unix-like utilities through Toybox:

**File Operations**: `ls`, `cp`, `mv`, `rm`, `cat`, `grep`, `find`, `chmod`, `chown`
**Text Processing**: `awk`, `sed`, `sort`, `cut`, `tr`, `wc`, `head`, `tail`
**System Info**: `ps` (pidin), `uname`, `whoami`, `id`, `hostname`
**Network Tools**: `ifconfig`, `ssh`, `scp`, `ping` (through system), `tcpdump`
**Network Analysis**: `network_capture` - Packet capture with Wireshark integration
**Compression**: `gzip`, `gunzip`, `tar`, `bzip2`
**Development**: `openssl`, `hexdump`, `od`, `strings`

### System Services

- **System Logger** (`slogger2`) - Centralized logging with 4KB buffer
- **PCI Server** - Hardware device management
- **SSH Daemon** - Remote access service
- **File System Event Manager** - File change notifications
- **Message Queues** - POSIX IPC support
- **Random Number Generator** - Entropy service
- **Network Stack** - TCP/IP with VirtIO drivers

### File Systems

- **Root File System** - Image File System (IFS) in memory
- **QNX6 File System** - On RAM disk (`/tmp_ram`)
- **DOS File System** - For compatibility
- **Pseudo File Systems** - `/proc`, `/dev`, `/tmp`

## Network Trace Collection

### Network Analysis Overview

The QNX system includes comprehensive network packet capture capabilities with Wireshark integration. This enables real-time analysis of network traffic for debugging, security analysis, and performance monitoring.

### Packet Capture Methods

#### 1. Direct Capture on QNX System

Access the QNX system and use the built-in capture tool:

```bash
# SSH into QNX system
ssh -p 2222 root@localhost

# Start packet capture (saves to file)
network_capture start

# Capture with filter (e.g., SSH traffic only)
network_capture start "tcp port 22"

# Check capture status
network_capture status

# List captured files
network_capture list

# Stop capture
network_capture stop
```

#### 2. Real-time Streaming to Wireshark

Stream packets directly to Wireshark running on the host system:

```bash
# On QNX system: Start packet streaming
network_capture stream

# On host system: Launch Wireshark with remote capture
# Method 1: Use integration script (recommended)
./scripts/qnx_wireshark.sh wireshark

# Method 2: Manual Wireshark configuration
# 1. Open Wireshark
# 2. Go to Capture -> Options -> Manage Interfaces
# 3. Add remote interface: TCP@localhost:9999
# 4. Start capture
```

### Host Integration Script

The `scripts/qnx_wireshark.sh` script provides seamless integration:

```bash
# Launch Wireshark with live QNX capture
./scripts/qnx_wireshark.sh wireshark

# Start streaming (manual Wireshark setup)
./scripts/qnx_wireshark.sh stream

# Download saved capture files
./scripts/qnx_wireshark.sh list
./scripts/qnx_wireshark.sh download capture_20250129_143022.pcap

# Check QNX capture status
./scripts/qnx_wireshark.sh status

# Stop all captures
./scripts/qnx_wireshark.sh stop
```

### Network Filtering Examples

Common packet filters for targeted analysis:

```bash
# SSH traffic analysis
network_capture start "tcp port 22"

# ICMP/ping analysis
network_capture start "icmp"

# All TCP traffic
network_capture start "tcp"

# Traffic to/from gateway
network_capture start "host 10.0.2.2"

# HTTP/HTTPS traffic
network_capture start "tcp port 80 or tcp port 443"

# DNS queries
network_capture start "udp port 53"
```

### Port Forwarding Configuration

The system is configured with port forwarding for network analysis:

- **SSH**: `localhost:2222` → `guest:22`
- **HTTP**: `localhost:8080` → `guest:80`
- **HTTPS**: `localhost:8443` → `guest:443`
- **Packet Stream**: `localhost:9999` → `guest:9999`

### Wireshark Analysis Workflow

1. **Start QNX System**:

   ```bash
   bazel run --config=x86_64-qnx //:run_qemu_portforward
   ```

2. **Launch Live Capture**:

   ```bash
   ./scripts/qnx_wireshark.sh wireshark "tcp"
   ```

3. **Generate Traffic**:

   - SSH connections: `ssh -p 2222 root@localhost`
   - Network tests: `ping` from within QNX
   - Application traffic through port forwarding

4. **Analyze in Wireshark**:
   - Real-time packet inspection
   - Protocol analysis
   - Network performance metrics
   - Security analysis

### Saved Capture Analysis

For offline analysis of saved captures:

```bash
# List available captures
./scripts/qnx_wireshark.sh list

# Download specific capture
./scripts/qnx_wireshark.sh download capture_20250129_143022.pcap

# Open in Wireshark
wireshark capture_20250129_143022.pcap
```

### Troubleshooting Network Capture

**Connection Issues**:

- Verify SSH connectivity: `ssh -p 2222 root@localhost`
- Check port forwarding: `netstat -tlnp | grep 9999`
- Ensure QNX system is running: `./scripts/qnx_wireshark.sh status`

**Wireshark Integration**:

- Install Wireshark: `sudo apt install wireshark` (Ubuntu/Debian)
- Add user to wireshark group: `sudo usermod -a -G wireshark $USER`
- Verify remote capture support in Wireshark

**Packet Loss**:

- Reduce capture load with specific filters
- Use file-based capture for high-throughput analysis
- Monitor system resources on QNX

### Network Security Considerations

- Packet captures may contain sensitive data
- Use filters to limit captured data scope
- Secure transfer of capture files from QNX system
- Regular cleanup of capture files in `/tmp_ram/var/capture`

## Troubleshooting

### Common Issues

1. **System Won't Boot**
   - Check QNX SDP toolchain installation
   - Verify image file permissions
   - Ensure KVM is available and accessible

2. **Network Connectivity Issues**
   - Verify bridge network configuration on host
   - Check IP address conflicts
   - Ensure firewall allows bridge traffic

3. **SSH Connection Refused**
   - Wait for full system boot (look for "Hostname set to: Qnx_S-core")
   - Check SSH daemon startup in console output
   - Verify port forwarding configuration

4. **Performance Issues**
   - Enable KVM acceleration (`--enable-kvm`)
   - Increase memory allocation (`-m 2G`)
   - Use VirtIO drivers for I/O

### Debug Information

- **Boot Messages**: Monitor serial console for startup progress
- **System Logs**: Use `slog2info` within the system
- **Process List**: Use `pidin` to see running processes
- **Network Status**: Use `ifconfig` to check interface configuration

### Host Requirements

- **Linux Distribution**: Ubuntu 20.04+ or equivalent
- **Virtualization**: KVM support enabled
- **Memory**: Minimum 4GB host RAM (1GB allocated to guest)
- **Network**: Bridge networking capability
- **Privileges**: Access to `/dev/kvm` and bridge creation

## Development and Customization

### Adding New Software

1. **Edit system.build**: Add new binaries and libraries
2. **Update dependencies**: Include required shared libraries
3. **Rebuild image**: `bazel build --config=x86_64-qnx //build:init`

### Modifying Services

1. **Edit startup.sh**: Modify service startup sequence
2. **Add configuration files**: Place in `configs/` directory
3. **Update BUILD file**: Include new configuration files

### Security Considerations

This image is configured for development convenience with:

- Passwordless SSH access
- Root login enabled
- Relaxed security policies

For production use, implement:

- Strong authentication mechanisms
- User privilege restrictions
- Network access controls
- Audit logging

## Contributing

This project is part of the Eclipse SCORE initiative. Contributions should follow Eclipse Foundation guidelines and maintain compatibility with the SCORE architecture.

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

---

**Eclipse SCORE** - Safety Critical Object-Oriented Real-time Embedded Systems
