# QNX QEMU Integration Tests

This directory contains integration tests for the QNX QEMU environment that verify system boot and SSH connectivity.

## Test Script Features

The main test script `test_qnx_qemu.sh` provides comprehensive testing of:

### 1. QEMU Boot Testing
- Starts QEMU instance with network forwarding
- Monitors boot process for completion indicators
- Validates system initialization
- Configurable boot timeout

### 2. SSH Connectivity Testing  
- Tests SSH port forwarding (localhost:2222 -> guest:22)
- Validates network stack functionality
- SSH connection establishment verification
- Optional SSH testing (can be disabled)

### 3. System Functionality Testing
- Process monitoring (QEMU health)
- System output analysis
- Boot indicator validation
- System stabilization verification

## Usage

### With Bazel (Recommended)
```bash
# Run the complete test suite
bazel run //:test_qemu

# Run just the QEMU instance (for manual testing)
bazel run //:run_qemu
```

### Manual Execution
```bash
# Make script executable
chmod +x test/test_qnx_qemu.sh

# Run with built components
./test/test_qnx_qemu.sh <qnx_host_dir> <ifs_image> [options]

# Example:
./test/test_qnx_qemu.sh ./bazel-bin/external/toolchains_qnx_sdp/host/linux/x86_64 ./bazel-bin/build/init.ifs
```

### Using the Manual Test Runner
```bash
# Run automated manual tests
chmod +x test/run_manual_tests.sh
./test/run_manual_tests.sh
```

## Configuration Options

The test script supports various configuration options:

```bash
./test_qnx_qemu.sh <qnx_host> <ifs_image> [options]

Options:
  --timeout=N       Boot timeout in seconds (default: 120)
  --ssh-port=N      SSH port for testing (default: 2222)  
  --ssh-user=USER   SSH user for testing (default: root)
  --boot-wait=N     Additional wait after boot (default: 30)
  --no-ssh          Skip SSH connectivity test
  --help            Show help message
```

### Examples

```bash
# Quick test without SSH
./test/test_qnx_qemu.sh $QNX_HOST $IFS_IMAGE --timeout=60 --no-ssh

# Full test with custom SSH port
./test/test_qnx_qemu.sh $QNX_HOST $IFS_IMAGE --ssh-port=2222 --timeout=120

# Test with minimal wait time
./test/test_qnx_qemu.sh $QNX_HOST $IFS_IMAGE --boot-wait=10
```

## Test Phases

### Phase 1: QEMU Startup
- Launches QEMU with KVM acceleration
- Configures SSH port forwarding (localhost:2222 -> guest:22)
- Sets up network interface with virtio-net
- Enables hardware random number generator

### Phase 2: Boot Monitoring
- Monitors QEMU output for boot indicators:
  - "Welcome to QNX" messages
  - "QNX OS" system identification
  - Shell startup ("Starting shell", "# ", "/bin/sh")
  - Login prompts
  - Startup script execution
- Configurable timeout with process health checking

### Phase 3: System Stabilization
- Optional wait period for system services to start
- Allows network services and SSH daemon to initialize
- Configurable stabilization time

### Phase 4: Functionality Testing
- Verifies QEMU process is still running
- Analyzes system output for functionality indicators
- Validates basic system health

### Phase 5: SSH Connectivity Testing
- Tests SSH port accessibility using netcat or telnet
- Generates temporary SSH keys for connection testing
- Attempts SSH connection to validate network stack
- Distinguishes between connection refused vs authentication failures

### Phase 6: Final Status Report
- Displays final system status
- Shows recent system output
- Provides connection information for manual access

## Network Configuration

The test automatically configures networking:

- **Host Port**: 2222 (configurable)
- **Guest Port**: 22 (SSH standard)
- **Interface**: virtio-net-pci (better performance)
- **Access**: `ssh -p 2222 root@localhost`

## Cleanup

The test script includes comprehensive cleanup:

- Graceful QEMU process termination
- Force kill if graceful termination fails  
- Temporary file cleanup (logs, SSH keys, PID files)
- Signal handling for interruption (Ctrl+C)

## Troubleshooting

### Common Issues

1. **QEMU fails to start**
   ```bash
   # Check if QEMU is installed
   which qemu-system-x86_64
   
   # Check if KVM is available
   ls -la /dev/kvm
   ```

2. **Boot timeout**
   - Increase timeout: `--timeout=180`
   - Check system output in `/tmp/qnx_qemu_test_*.log`
   - Verify IFS image integrity

3. **SSH connection fails**
   - Ensure SSH daemon is configured in the QNX image
   - Check port forwarding: `netstat -an | grep 2222`
   - Try without SSH: `--no-ssh`

4. **Permission errors**
   ```bash
   # Make scripts executable
   chmod +x test/*.sh
   
   # Check file permissions
   ls -la test/
   ```

### Debug Information

The test script provides detailed logging:

- Real-time QEMU output monitoring
- Boot sequence analysis
- Network connectivity testing
- SSH connection diagnostics
- Process health monitoring

### Manual Testing

For debugging, you can run components manually:

```bash
# Start QEMU manually (based on run_qemu.sh)
qemu-system-x86_64 \
    -smp 2 --enable-kvm \
    -cpu Cascadelake-Server-v5 \
    -m 1G -nographic \
    -kernel ./bazel-bin/build/init.ifs \
    -netdev user,id=net0,hostfwd=tcp::2222-:22 \
    -device virtio-net-pci,netdev=net0

# Test SSH connectivity
ssh -p 2222 root@localhost

# Monitor boot process
tail -f /tmp/qnx_qemu_test_*.log
```

## Integration with CI/CD

The tests are designed for integration with automated testing:

- Exit codes: 0 = success, 1 = failure
- Structured output for parsing
- Configurable timeouts for different environments
- Optional SSH testing for headless environments
- Comprehensive cleanup for resource management

## Files

- `test_qnx_qemu.sh` - Main integration test script
- `run_manual_tests.sh` - Manual test runner with examples
- `BUILD` - Bazel build configuration
- `README.md` - This documentation
