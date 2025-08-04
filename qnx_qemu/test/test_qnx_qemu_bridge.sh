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

# QNX QEMU Bridge Network Test Script
# Tests QNX QEMU image with bridge networking and fixed IP

# Default configuration
TIMEOUT=${TIMEOUT:-120}
SSH_PORT=${SSH_PORT:-2222}
SSH_USER=${SSH_USER:-root}
BOOT_WAIT=${BOOT_WAIT:-15}
QNX_IP=${QNX_IP:-192.168.122.100}
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
    echo "  --qnx-ip=IP       QNX system IP for ping test (default: 192.168.122.100)"
    echo "  --no-ssh          Skip SSH connectivity test"
    echo "  --no-ping         Skip ping connectivity test"
    echo "  --help            Show this help"
    echo ""
    echo "Note: This test uses bridge networking with fixed IP"
    exit 1
}

# Parse arguments
TEST_SSH=true
TEST_PING=true
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
        --qnx-ip=*)
            QNX_IP="${1#*=}"
            shift
            ;;
        --no-ssh)
            TEST_SSH=false
            shift
            ;;
        --no-ping)
            TEST_PING=false
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
OUTPUT_LOG="/tmp/qnx_qemu_bridge_test_$$.log"

echo "============================================================"
echo "QNX QEMU Bridge Network Test"
echo "============================================================"
echo "QNX Host: $QNX_HOST"
echo "IFS Image: $IFS_IMAGE"
echo "Timeout: ${TIMEOUT}s"
echo "QNX IP: $QNX_IP (bridge network)"
if [ "$TEST_SSH" = true ]; then
    echo "SSH Test: Enabled (direct connection)"
    echo "SSH User: $SSH_USER"
else
    echo "SSH Test: Disabled"
fi
if [ "$TEST_PING" = true ]; then
    echo "Ping Test: Enabled"
else
    echo "Ping Test: Disabled"
fi
echo "Boot Wait: ${BOOT_WAIT}s"
echo "Network Mode: Bridge (virbr0)"
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

# Function to start QEMU with bridge networking
start_qemu() {
    echo "1. Starting QEMU with bridge networking..."
    
    # Start QEMU in background with bridge networking only (no port forwarding)
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
        -netdev bridge,id=net0,br=virbr0 \
        -device virtio-net-pci,netdev=net0 \
        > "$OUTPUT_LOG" 2>&1 &
    
    QEMU_PID=$!
    echo "✓ QEMU started (PID: $QEMU_PID)"
    echo "✓ Bridge networking enabled (DHCP with fallback: $QNX_IP)"
    echo "✓ Direct network access via bridge interface"
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

# Function to detect actual QNX IP address
detect_qnx_ip() {
    echo ""
    echo "4. Detecting QNX system IP address..."
    
    local detected_ip=""
    local dhcp_status=""
    
    # Try to get DHCP status from the system
    local dhcp_pattern="DHCP_SUCCESS\|DHCP_FAILED_STATIC_FALLBACK"
    local dhcp_wait=30
    local dhcp_start=$(date +%s)
    
    echo "Waiting for network configuration to complete..."
    
    while [ $(($(date +%s) - dhcp_start)) -lt "$dhcp_wait" ]; do
        if grep -q "$dhcp_pattern" "$OUTPUT_LOG" 2>/dev/null; then
            dhcp_status=$(grep "$dhcp_pattern" "$OUTPUT_LOG" | tail -1)
            echo "✓ Network configuration detected: $dhcp_status"
            break
        fi
        sleep 2
        echo "  ... waiting for network setup"
    done
    
    # Try to extract IP from DHCP status in logs
    local ip_pattern="IP: [0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+"
    if grep -q "$ip_pattern" "$OUTPUT_LOG" 2>/dev/null; then
        detected_ip=$(grep "$ip_pattern" "$OUTPUT_LOG" | tail -1 | sed 's/.*IP: \([0-9.]*\).*/\1/')
        if [ -n "$detected_ip" ] && [ "$detected_ip" != "0.0.0.0" ]; then
            echo "✓ Detected QNX IP address from logs: $detected_ip"
            QNX_IP="$detected_ip"
            return 0
        fi
    fi
    
    # If we couldn't detect IP from logs, use the fallback IP
    echo "⚠ Could not detect actual IP from logs, using fallback: $QNX_IP"
    echo "  (System may be using DHCP or static fallback)"
    
    return 0
}

# Function to test ping connectivity
test_ping_connectivity() {
    if [ "$TEST_PING" != true ]; then
        echo ""
        echo "5. Ping test skipped (disabled)"
        return 0
    fi
    
    echo ""
    echo "5. Testing ping connectivity to QNX system..."
    
    # Test ping connectivity to the QNX system
    echo "Testing ping to $QNX_IP..."
    
    if command -v ping >/dev/null 2>&1; then
        # Try ping with different approaches (some systems use different flags)
        local ping_success=false
        
        # Try standard ping (3 packets)
        if ping -c 3 -W 5 "$QNX_IP" >/dev/null 2>&1; then
            ping_success=true
        elif ping -c 3 -w 5 "$QNX_IP" >/dev/null 2>&1; then
            ping_success=true
        fi
        
        if [ "$ping_success" = true ]; then
            echo "✓ Ping test successful - QNX system is reachable at $QNX_IP"
            
            # Show ping statistics
            echo "Ping statistics:"
            ping -c 3 "$QNX_IP" 2>/dev/null || echo "  (statistics not available)"
        else
            echo "✗ Ping test failed - QNX system not reachable at $QNX_IP"
            echo "This could indicate:"
            echo "  - Bridge networking not properly configured"
            echo "  - QNX network setup failed or still in progress"
            echo "  - Host firewall blocking ICMP"
            echo "  - IP address detection was incorrect"
            return 1
        fi
    else
        echo "⚠ Ping command not available, skipping ping test"
    fi
    
    return 0
}

# Function to test system functionality
test_system_functionality() {
    echo ""
    echo "6. Testing system functionality..."
    
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
        echo "7. SSH test skipped (disabled)"
        return 0
    fi
    
    echo ""
    echo "7. Testing SSH connectivity..."
    
    # Test direct SSH connection to QNX system IP without key authentication
    echo "Testing direct SSH connection to QNX system..."
    if command -v ssh >/dev/null 2>&1; then
        echo "Attempting SSH connection to $SSH_USER@$QNX_IP..."
        
        # Try SSH connection with password authentication (no keys, empty password)
        if timeout 15 ssh -o ConnectTimeout=10 \
                          -o StrictHostKeyChecking=no \
                          -o UserKnownHostsFile=/dev/null \
                          -o PreferredAuthentications=password \
                          -o PubkeyAuthentication=no \
                          -o PasswordAuthentication=yes \
                          -o BatchMode=yes \
                          "$SSH_USER@$QNX_IP" \
                          "echo 'SSH connection successful'; hostname 2>/dev/null || echo 'hostname command not available'; ifconfig vtnet0 2>/dev/null | grep 'inet ' || echo 'Network info not available'" 2>/dev/null; then
            echo "✓ SSH connection to $QNX_IP successful"
            echo "✓ Executed remote commands successfully"
        else
            echo "✗ SSH connection to $QNX_IP failed"
            echo "This could indicate:"
            echo "  - SSH daemon not yet started"
            echo "  - Network connectivity issues"
            echo "  - SSH authentication problems"
            echo "  - Firewall blocking SSH port"
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
    echo "8. Final system status..."
    
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
    
    # Detect actual QNX IP address
    if ! detect_qnx_ip; then
        echo "✗ IP detection failed"
        all_tests_passed=false
    fi
    
    # Test ping connectivity
    if ! test_ping_connectivity; then
        echo "✗ Ping connectivity test failed"
        all_tests_passed=false
    fi
    
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
        echo "QNX QEMU bridge network integration is working correctly!"
        echo "QEMU is running on PID: $QEMU_PID"
        echo "QNX system IP: $QNX_IP (detected via bridge networking)"
        echo "SSH access: ssh $SSH_USER@$QNX_IP (direct bridge connection)"
        return 0
    else
        echo "✗ SOME TESTS FAILED"
        echo "Check the output above for details."
        return 1
    fi
}

# Run main function
main "$@"
