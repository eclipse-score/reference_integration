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

# QNX Network Trace Collection Script
# Provides easy integration between QNX tcpdump and Wireshark

set -euo pipefail

# Configuration
QNX_HOST=${QNX_HOST:-localhost}
SSH_PORT=${SSH_PORT:-2222}
CAPTURE_PORT=${CAPTURE_PORT:-9999}
SSH_USER=${SSH_USER:-root}
SSH_OPTIONS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10"

usage() {
    echo "QNX Network Trace Collection for Wireshark"
    echo "==========================================="
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  capture [filter]    - Start local packet capture and save to file"
    echo "  stream [filter]     - Start real-time streaming to Wireshark"
    echo "  wireshark [filter]  - Launch Wireshark with live capture"
    echo "  list               - List captured files on QNX system"
    echo "  download [file]    - Download capture file from QNX"
    echo "  status             - Show capture status on QNX"
    echo "  stop               - Stop all captures on QNX"
    echo "  help               - Show this help"
    echo ""
    echo "Filter examples:"
    echo "  \"tcp port 22\"      - SSH traffic only"
    echo "  \"icmp\"             - Ping traffic only"
    echo "  \"tcp\"              - All TCP traffic"
    echo "  \"host 10.0.2.2\"    - Traffic to/from host gateway"
    echo ""
    echo "Environment variables:"
    echo "  QNX_HOST=$QNX_HOST           # QNX system IP/hostname"
    echo "  SSH_PORT=$SSH_PORT           # SSH port (forwarded)"
    echo "  CAPTURE_PORT=$CAPTURE_PORT   # Packet streaming port (forwarded)"
    echo "  SSH_USER=$SSH_USER           # SSH username"
    echo ""
    echo "Prerequisites:"
    echo "  - QNX system running with SSH access"
    echo "  - Port forwarding configured: localhost:$SSH_PORT -> guest:22"
    echo "  - Port forwarding configured: localhost:$CAPTURE_PORT -> guest:9999"
    echo "  - Wireshark installed on host system"
}

check_qnx_connection() {
    echo "Checking QNX connection..."
    if ! ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "echo 'QNX connection successful'" >/dev/null 2>&1; then
        echo "Error: Cannot connect to QNX system at $SSH_USER@$QNX_HOST:$SSH_PORT"
        echo "Please ensure:"
        echo "  1. QNX system is running"
        echo "  2. SSH is working: ssh -p $SSH_PORT $SSH_USER@$QNX_HOST"
        echo "  3. Port forwarding is configured correctly"
        return 1
    fi
    echo "✓ QNX connection verified"
}

check_network_capture_tool() {
    echo "Checking network capture tool on QNX..."
    if ! ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "test -x /etc/network_capture" 2>/dev/null; then
        echo "Error: network_capture tool not found on QNX system"
        echo "Please ensure the QNX image includes the network capture script"
        return 1
    fi
    echo "✓ Network capture tool available"
}

check_wireshark() {
    if ! command -v wireshark >/dev/null 2>&1; then
        echo "Warning: Wireshark not found on host system"
        echo "To install Wireshark:"
        echo "  Ubuntu/Debian: sudo apt install wireshark"
        echo "  RHEL/CentOS: sudo yum install wireshark"
        echo "  macOS: brew install wireshark"
        return 1
    fi
    echo "✓ Wireshark available"
    return 0
}

case "${1:-help}" in
    capture)
        FILTER="${2:-}"
        
        check_qnx_connection
        check_network_capture_tool
        
        echo ""
        echo "Starting packet capture on QNX system..."
        if [ -n "$FILTER" ]; then
            echo "Filter: $FILTER"
            ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture start '$FILTER'"
        else
            echo "Filter: none (all packets)"
            ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture start"
        fi
        
        echo ""
        echo "Capture started on QNX system"
        echo "To stop: $0 stop"
        echo "To check status: $0 status"
        echo "To list files: $0 list"
        ;;
        
    stream)
        FILTER="${2:-}"
        
        check_qnx_connection
        check_network_capture_tool
        
        echo ""
        echo "Starting real-time packet streaming from QNX..."
        if [ -n "$FILTER" ]; then
            echo "Filter: $FILTER"
        else
            echo "Filter: none (all packets)"
        fi
        echo "Stream endpoint: localhost:$CAPTURE_PORT"
        echo ""
        echo "Starting stream on QNX system..."
        
        # Start streaming on QNX in background
        if [ -n "$FILTER" ]; then
            ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stream '$FILTER'" &
        else
            ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stream" &
        fi
        
        QNX_STREAM_PID=$!
        
        echo "QNX streaming started (PID: $QNX_STREAM_PID)"
        echo ""
        echo "To capture in Wireshark:"
        echo "  1. Open Wireshark"
        echo "  2. Go to Capture -> Options"
        echo "  3. Click 'Manage Interfaces'"
        echo "  4. Go to 'Remote Interfaces' tab"
        echo "  5. Add interface: TCP@localhost:$CAPTURE_PORT"
        echo "  6. Start capture"
        echo ""
        echo "Or use: $0 wireshark"
        echo ""
        echo "Press Ctrl+C to stop streaming"
        
        # Wait for stream process
        trap 'echo ""; echo "Stopping stream..."; kill $QNX_STREAM_PID 2>/dev/null; ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stop" 2>/dev/null; exit 0' INT TERM
        wait $QNX_STREAM_PID
        ;;
        
    wireshark)
        FILTER="${2:-}"
        
        check_qnx_connection
        check_network_capture_tool
        
        if ! check_wireshark; then
            exit 1
        fi
        
        echo ""
        echo "Launching Wireshark with QNX live capture..."
        if [ -n "$FILTER" ]; then
            echo "Filter: $FILTER"
        else
            echo "Filter: none (all packets)"
        fi
        
        # Start streaming on QNX
        echo "Starting packet stream on QNX..."
        if [ -n "$FILTER" ]; then
            ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stream '$FILTER'" &
        else
            ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stream" &
        fi
        
        QNX_STREAM_PID=$!
        
        # Give stream time to start
        sleep 3
        
        echo "Launching Wireshark..."
        # Launch Wireshark with remote capture
        wireshark -k -i TCP@localhost:$CAPTURE_PORT &
        WIRESHARK_PID=$!
        
        echo ""
        echo "Wireshark launched (PID: $WIRESHARK_PID)"
        echo "QNX streaming (PID: $QNX_STREAM_PID)"
        echo ""
        echo "Press Ctrl+C to stop both Wireshark and QNX streaming"
        
        # Wait and cleanup
        trap 'echo ""; echo "Stopping Wireshark and QNX stream..."; kill $WIRESHARK_PID $QNX_STREAM_PID 2>/dev/null; ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stop" 2>/dev/null; exit 0' INT TERM
        
        # Wait for either process to end
        wait $WIRESHARK_PID 2>/dev/null || wait $QNX_STREAM_PID 2>/dev/null
        
        # Cleanup remaining processes
        kill $QNX_STREAM_PID $WIRESHARK_PID 2>/dev/null || true
        ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stop" 2>/dev/null || true
        ;;
        
    list)
        check_qnx_connection
        check_network_capture_tool
        
        echo "Listing capture files on QNX system..."
        ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture list"
        ;;
        
    download)
        FILENAME="${2:-}"
        
        if [ -z "$FILENAME" ]; then
            echo "Error: Filename required"
            echo "Usage: $0 download <filename>"
            echo "Use '$0 list' to see available files"
            exit 1
        fi
        
        check_qnx_connection
        
        echo "Downloading capture file from QNX..."
        echo "Remote file: /tmp_ram/capture/$FILENAME"
        echo "Local file: ./$FILENAME"
        
        if scp $SSH_OPTIONS -P "$SSH_PORT" "$SSH_USER@$QNX_HOST:/tmp_ram/capture/$FILENAME" "./$FILENAME"; then
            echo "✓ File downloaded successfully"
            echo ""
            echo "To analyze in Wireshark:"
            echo "  wireshark ./$FILENAME"
        else
            echo "✗ Download failed"
            exit 1
        fi
        ;;
        
    status)
        check_qnx_connection
        check_network_capture_tool
        
        echo "QNX network capture status:"
        ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture status"
        ;;
        
    stop)
        check_qnx_connection
        check_network_capture_tool
        
        echo "Stopping all network captures on QNX..."
        ssh $SSH_OPTIONS -p "$SSH_PORT" "$SSH_USER@$QNX_HOST" "network_capture stop"
        echo "✓ All captures stopped"
        ;;
        
    help|*)
        usage
        ;;
esac
