# QNX QEMU Reference Integration

This directory contains the configuration and build files for creating a minimal QNX system that runs in QEMU. It demonstrates how to set up a basic QNX environment with essential system components, utilities, and services.

## Directory Overview

The QNX QEMU integration provides a virtualized QNX environment suitable for development, testing, and demonstration purposes. It includes a carefully curated set of system components that provide core functionality while maintaining a minimal footprint.

## Key Files

### `system.build`

The main system partition definition file that specifies:

- **Essential utilities**: File manipulation tools (toybox-based), system administration utilities
- **Shared libraries**: Core runtime libraries including C library, compression, cryptographic, and system-specific libraries  
- **Configuration files**: System settings, user accounts, hardware configuration, and environment setup
- **System services**: PCI management, cryptographic services, logging, and device management

### `init.build`

Initial file system (IFS) definition containing the kernel and boot-critical components that are loaded into RAM during system startup.

### `run_qemu.sh`

Shell script to launch the QNX system in QEMU with appropriate hardware emulation settings.

### Build System Files

- `BUILD`: Bazel build configuration
- `MODULE.bazel`: Bazel module definition
- `.bazelrc` & `.bazelversion`: Bazel configuration and version specification

## System Architecture

### Partition Layout

The QNX system uses a multi-partition approach however, currently everything is packed within IFS image but later it could be changed to the following structure:

1. **IFS (Image File System)**: Contains kernel and essential boot components
2. **System Partition**: Contains utilities, libraries, and configuration files (defined in `system.build`)
3. **Data Partition**: User data, applications, and persistent storage

### Key Components

#### File System Utilities

- Uses **toybox** as the primary source of Unix-compatible utilities
- Provides essential commands: `ls`, `cp`, `cat`, `chmod`, `rm`, `grep`, etc.
- Minimal footprint while maintaining POSIX compatibility

#### Shared Libraries

- **Core libraries**: `libc.so`, `libm.so`, `libgcc_s.so.1` for basic system operation
- **File system support**: `fs-qnx6.so`, `fs-dos.so` for different file system types
- **Compression**: `libz.so`, `libbz2.so.1`, `liblzma.so.5` for data compression
- **Cryptographic**: `libqcrypto.so.1.0`, `openssl` for security operations
- **Hardware access**: `libpci.so.3.0`, CAM libraries for device interaction

#### System Services

- **PCI Server**: Manages PCI bus enumeration and device configuration
- **Device Managers**: Block devices (`devb-ram`), pseudo-terminals (`devc-pty`)
- **Network Stack**: Interface configuration tools (`ifconfig`, `if_up`)
- **Security**: Packet filtering (`pfctl`), encryption services

#### Configuration Management

- **User Management**: Standard `/etc/passwd` and `/etc/group` files
- **Environment Setup**: Global shell profile with PATH and library path configuration
- **Hardware Configuration**: PCI device interrupt routing for QEMU environment
- **Service Configuration**: Cryptographic modules, system logging

## Usage

### Building the System

```bash
# Build the QNX system image
bazel build //...
```

### Running in QEMU

```bash
# Launch the system in QEMU
./run_qemu.sh
```

### System Access

Once booted, the system provides:

- Root shell access with standard Unix utilities
- Network interface configuration capabilities
- File system management tools
- Hardware device access through PCI services

## Development Notes

### Customization

- Modify `system.build` to add/remove utilities, libraries, or configuration files
- Update `init.build` for kernel-level changes
- Adjust QEMU parameters in `run_qemu.sh` for different hardware emulation

### Debugging

- PCI debugging is available through `pci_debug2.so`
- System logging via `slogger2` service
- Process information available through `pidin` utility

### Security Considerations

- System runs with root privileges by default
- Cryptographic services available through OpenSSL integration
- User and group management configured for multi-service architecture

## Integration with SCORE Project

This QNX QEMU configuration serves as a reference implementation for:

- Embedded system development workflows
- Cross-platform build system integration
- Hardware abstraction layer testing
- Real-time system behavior validation

The minimal footprint and carefully selected components make it suitable for CI/CD pipelines and automated testing scenarios while providing sufficient functionality for development and debugging tasks.
