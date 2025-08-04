#!/bin/bash
# *******************************************************************************
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

set -euo pipefail

# QNX QEMU Port Forwarding Test Script
# Tests QNX QEMU image with port forwarding (NAT networking)

# Default configuration
TIMEOUT=${TIMEOUT:-120}
SSH_PORT=${SSH_PORT:-2222}
SSH_USER=${SSH_USER:-root}
BOOT_WAIT=${BOOT_WAIT:-15}
QNX_HOST=""
IFS_IMAGE=""

# Parse command line arguments
usage() {
    echo "Usage: $0 <qnx_host> <ifs_image> [options]"
    echo "Options:"
    echo "  --timeout=N       Boot timeout in seconds (default: 120)"
    echo "  --ssh-port=N      SSH port for testing (default: 2222)"
    echo "  --ssh-user=USER   SSH user for testing (default: root)"
    echo "  --boot-wait=N     Additional wait after boot (default: 15)"
    echo "  --no-ssh          Skip SSH connectivity test"
    echo "  --help            Show this help"
    echo ""
    echo "Note: This test uses port forwarding (NAT networking) - no ping test available"
    exit 1
}

# Parse arguments
TEST_SSH=true
while [[ $# -gt 0 ]]; do
    case $1 in
        --timeout=*)
            TIMEOUT="${1#*=}"
            shift
            ;;
        --ssh-port=*)
            SSH_PORT="${1#*=}"
            shift
            ;;
        --ssh-user=*)
            SSH_USER="${1#*=}"
            shift
            ;;
        --boot-wait=*)
            BOOT_WAIT="${1#*=}"
            shift
            ;;
        --no-ssh)
            TEST_SSH=false
            shift
            ;;
        --help)
            usage
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            if [ -z "$QNX_HOST" ]; then
                QNX_HOST="$1"
            elif [ -z "$IFS_IMAGE" ]; then
                IFS_IMAGE="$1"
            else
                echo "Too many arguments"
                usage
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [ -z "$QNX_HOST" ] || [ -z "$IFS_IMAGE" ]; then
    echo "Error: Missing required arguments"
    usage
fi

# Validate files exist
if [ ! -d "$QNX_HOST" ]; then
    echo "Error: QNX host directory not found: $QNX_HOST"
    exit 1
fi

if [ ! -f "$IFS_IMAGE" ]; then
    echo "Error: IFS image not found: $IFS_IMAGE"
    exit 1
fi

# Global variables
QEMU_PID=""
OUTPUT_LOG="/tmp/qnx_qemu_portforward_test_$$.log"

echo "============================================================"
echo "QNX QEMU Port Forwarding Test"
echo "============================================================"
echo "QNX Host: $QNX_HOST"
echo "IFS Image: $IFS_IMAGE"
echo "Timeout: ${TIMEOUT}s"
echo "SSH Port: $SSH_PORT (forwarded from localhost)"
echo "SSH User: $SSH_USER"
if [ "$TEST_SSH" = true ]; then
    echo "SSH Test: Enabled"
else
    echo "SSH Test: Disabled"
fi
echo "Boot Wait: ${BOOT_WAIT}s"
echo "Network Mode: Port Forwarding (NAT)"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up..."
    
    # Kill QEMU process
    if [ -n "$QEMU_PID" ] && kill -0 "$QEMU_PID" 2>/dev/null; then
        echo "Terminating QEMU process (PID: $QEMU_PID)"
        kill "$QEMU_PID" 2>/dev/null || true
        sleep 3
        if kill -0 "$QEMU_PID" 2>/dev/null; then
            echo "Force killing QEMU process"
            kill -9 "$QEMU_PID" 2>/dev/null || true
        fi
    fi
    
    # Clean up files
    rm -f "/tmp/qemu.pid" "$OUTPUT_LOG" 2>/dev/null || true
    
    echo "Cleanup completed"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Function to start QEMU with port forwarding
start_qemu() {
    echo "1. Starting QEMU with port forwarding..."
    
    # Start QEMU in background with port forwarding (NAT networking)
    qemu-system-x86_64 \
        -smp 2 \
        --enable-kvm \
        -cpu Cascadelake-Server-v5 \
        -m 1G \
        -pidfile /tmp/qemu.pid \
        -nographic \
        -kernel "$IFS_IMAGE" \
        -serial mon:stdio \
        -object rng-random,filename=/dev/urandom,id=rng0 \
        -device virtio-rng-pci,rng=rng0 \
        -netdev user,id=net0,hostfwd=tcp::${SSH_PORT}-:22,hostfwd=tcp::8080-:80,hostfwd=tcp::8443-:443,hostfwd=tcp::9999-:9999 \
        -device virtio-net-pci,netdev=net0 \
        > "$OUTPUT_LOG" 2>&1 &
    
    QEMU_PID=$!
    echo "✓ QEMU started (PID: $QEMU_PID)"
    echo "✓ Port forwarding: SSH($SSH_PORT->22), HTTP(8080->80), HTTPS(8443->443), Capture(9999->9999)"
    echo "✓ Guest uses NAT networking (10.0.2.x subnet)"
}

# Function to wait for boot completion
wait_for_boot() {
    echo ""
    echo "2. Waiting for boot completion (timeout: ${TIMEOUT}s)..."
    
    local start_time=$(date +%s)
    local boot_complete=false
    
    # Look specifically for hostname confirmation message
    local hostname_pattern="Hostname set to: Qnx_S-core"
    
    echo "Waiting for hostname confirmation: '$hostname_pattern'"
    
    while [ $(($(date +%s) - start_time)) -lt "$TIMEOUT" ]; do
        # Check if QEMU process is still running
        if ! kill -0 "$QEMU_PID" 2>/dev/null; then
            echo "✗ QEMU process terminated unexpectedly"
            echo "Last output:"
            tail -20 "$OUTPUT_LOG" 2>/dev/null || echo "No output available"
            return 1
        fi
        
        # Check for hostname confirmation message
        if grep -q "$hostname_pattern" "$OUTPUT_LOG" 2>/dev/null; then
            echo "✓ Boot completion detected: Found hostname confirmation"
            boot_complete=true
            break
        fi
        
        # Show progress every 10 seconds
        local elapsed=$(($(date +%s) - start_time))
        if [ $((elapsed % 10)) -eq 0 ] && [ $elapsed -gt 0 ]; then
            echo "  ... still waiting (${elapsed}s elapsed)"
        fi
        
        sleep 2
    done
    
    if [ "$boot_complete" = true ]; then
        echo "✓ System fully booted and hostname configured"
        return 0
    else
        echo "✗ Boot timeout reached - hostname confirmation not found"
        echo "Recent QEMU output:"
        echo "----------------------------------------"
        tail -20 "$OUTPUT_LOG" 2>/dev/null || echo "No output available"
        echo "----------------------------------------"
        return 1
    fi
}

# Function to wait additional time for system stabilization
wait_for_stabilization() {
    if [ "$BOOT_WAIT" -gt 0 ]; then
        echo ""
        echo "3. Waiting for system stabilization (${BOOT_WAIT}s)..."
        sleep "$BOOT_WAIT"
        echo "✓ Stabilization wait completed"
    fi
}

# Function to test system functionality
test_system_functionality() {
    echo ""
    echo "4. Testing system functionality..."
    
    # Check if QEMU is still running
    if ! kill -0 "$QEMU_PID" 2>/dev/null; then
        echo "✗ QEMU process is not running"
        return 1
    fi
    echo "✓ QEMU process is still running"
    
    # Check for system indicators in output
    local system_indicators=(
        "qnx"
        "Welcome"
        "shell"
        "startup"
    )
    
    local found_indicators=0
    for indicator in "${system_indicators[@]}"; do
        if grep -i -q "$indicator" "$OUTPUT_LOG" 2>/dev/null; then
            echo "✓ Found system indicator: $indicator"
            ((found_indicators++))
        fi
    done
    
    if [ "$found_indicators" -gt 0 ]; then
        echo "✓ System functionality indicators found ($found_indicators)"
        return 0
    else
        echo "✗ No system functionality indicators found"
        return 1
    fi
}

# Function to test SSH connectivity
test_ssh_connectivity() {
    if [ "$TEST_SSH" != true ]; then
        echo ""
        echo "5. SSH test skipped (disabled)"
        return 0
    fi
    
    echo ""
    echo "5. Testing SSH connectivity via port forwarding..."
    
    # Test if SSH port is open on localhost (port forwarding)
    echo "Testing SSH port connectivity on localhost:$SSH_PORT..."
    if command -v nc >/dev/null 2>&1; then
        if nc -z -w5 localhost "$SSH_PORT"; then
            echo "✓ SSH port $SSH_PORT is open on localhost"
        else
            echo "✗ SSH port $SSH_PORT is not accessible on localhost"
            return 1
        fi
    elif command -v telnet >/dev/null 2>&1; then
        if timeout 5 telnet localhost "$SSH_PORT" </dev/null >/dev/null 2>&1; then
            echo "✓ SSH port $SSH_PORT is open on localhost"
        else
            echo "✗ SSH port $SSH_PORT is not accessible on localhost"
            return 1
        fi
    else
        echo "⚠ No network testing tools available (nc or telnet)"
        echo "Skipping port connectivity test"
    fi
    
    # Test SSH connection via port forwarding
    echo "Testing SSH connection via port forwarding..."
    if command -v ssh >/dev/null 2>&1; then
        echo "Attempting SSH connection to $SSH_USER@localhost:$SSH_PORT..."
        
        # Try SSH connection with password authentication (no keys, empty password)
        if timeout 15 ssh -o ConnectTimeout=10 \
                          -o StrictHostKeyChecking=no \
                          -o UserKnownHostsFile=/dev/null \
                          -o PreferredAuthentications=password \
                          -o PubkeyAuthentication=no \
                          -o PasswordAuthentication=yes \
                          -o BatchMode=yes \
                          -p "$SSH_PORT" \
                          "$SSH_USER@localhost" \
                          "echo 'SSH connection successful via port forwarding'; hostname 2>/dev/null || echo 'hostname command not available'; ifconfig vtnet0 2>/dev/null | grep 'inet ' || echo 'Network info not available'" 2>/dev/null; then
            echo "✓ SSH connection via port forwarding successful"
            echo "✓ Retrieved system information from guest"
        else
            echo "✗ SSH connection via port forwarding failed"
            return 1
        fi
    else
        echo "⚠ SSH client not available, skipping SSH connection test"
    fi
    
    return 0
}

# Function to show final system status
show_system_status() {
    echo ""
    echo "6. Final system status..."
    
    if kill -0 "$QEMU_PID" 2>/dev/null; then
        echo "✓ QEMU process is running (PID: $QEMU_PID)"
    else
        echo "✗ QEMU process is not running"
    fi
    
    echo ""
    echo "Recent system output:"
    echo "----------------------------------------"
    tail -15 "$OUTPUT_LOG" 2>/dev/null || echo "No output available"
    echo "----------------------------------------"
}

# Main execution
main() {
    local all_tests_passed=true
    
    # Start QEMU
    if ! start_qemu; then
        echo "✗ Failed to start QEMU"
        return 1
    fi
    
    # Wait for boot
    if ! wait_for_boot; then
        echo "✗ Boot test failed"
        all_tests_passed=false
    fi
    
    # Wait for stabilization
    wait_for_stabilization
    
    # Test system functionality
    if ! test_system_functionality; then
        echo "✗ System functionality test failed"
        all_tests_passed=false
    fi
    
    # Test SSH connectivity
    if ! test_ssh_connectivity; then
        echo "✗ SSH connectivity test failed"
        all_tests_passed=false
    fi
    
    # Show final status
    show_system_status
    
    # Results
    echo ""
    echo "============================================================"
    if [ "$all_tests_passed" = true ]; then
        echo "✓ ALL TESTS PASSED"
        echo "QNX QEMU port forwarding integration is working correctly!"
        echo "QEMU is running on PID: $QEMU_PID"
        echo "SSH access: ssh -p $SSH_PORT $SSH_USER@localhost"
        echo "Network mode: Port forwarding (NAT) - guest uses 10.0.2.x subnet"
        return 0
    else
        echo "✗ SOME TESTS FAILED"
        echo "Check the output above for details."
        return 1
    fi
}

# Run main function
main "$@"
