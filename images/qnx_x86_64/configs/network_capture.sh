#!/bin/sh

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


# Network Packet Capture Script for QNX
# Provides tcpdump-based packet capture with remote access via netcat

# Configuration
CAPTURE_INTERFACE="vtnet0"
CAPTURE_PORT="9999"
LOG_DIR="/tmp_ram/capture"
MAX_PACKETS="10000"
CAPTURE_FILTER=""

usage() {
    echo "Network Packet Capture for QNX"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start [filter]     - Start packet capture (optionally with filter)"
    echo "  stop               - Stop all running captures"
    echo "  status             - Show capture status"
    echo "  stream [filter]    - Start real-time streaming to port $CAPTURE_PORT"
    echo "  list               - List saved capture files"
    echo "  help               - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Capture all packets"
    echo "  $0 start \"tcp port 22\"     # Capture SSH traffic only"
    echo "  $0 start \"icmp\"            # Capture ping traffic only"
    echo "  $0 stream \"tcp\"            # Stream TCP traffic to port $CAPTURE_PORT"
    echo ""
    echo "For Wireshark analysis:"
    echo "  1. Run: $0 stream [filter]"
    echo "  2. In Wireshark: Capture -> Options -> Manage Interfaces"
    echo "  3. Add remote interface: TCP@<qnx-ip>:$CAPTURE_PORT"
    echo "  4. Or with port forwarding: TCP@localhost:<forwarded-port>"
    echo ""
    echo "Saved captures: $LOG_DIR"
    echo "Network interface: $CAPTURE_INTERFACE"
}

# Ensure capture directory exists
mkdir -p "$LOG_DIR"

case "${1:-help}" in
    start)
        CAPTURE_FILTER="${2:-}"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        CAPTURE_FILE="$LOG_DIR/capture_${TIMESTAMP}.pcap"
        
        echo "Starting packet capture..."
        echo "Interface: $CAPTURE_INTERFACE"
        echo "File: $CAPTURE_FILE"
        echo "Max packets: $MAX_PACKETS"
        if [ -n "$CAPTURE_FILTER" ]; then
            echo "Filter: $CAPTURE_FILTER"
        else
            echo "Filter: none (capturing all traffic)"
        fi
        echo ""
        
        # Start tcpdump in background
        if [ -n "$CAPTURE_FILTER" ]; then
            tcpdump -i "$CAPTURE_INTERFACE" -w "$CAPTURE_FILE" -c "$MAX_PACKETS" "$CAPTURE_FILTER" &
        else
            tcpdump -i "$CAPTURE_INTERFACE" -w "$CAPTURE_FILE" -c "$MAX_PACKETS" &
        fi
        
        TCPDUMP_PID=$!
        echo "Capture started with PID: $TCPDUMP_PID"
        echo "Capture file: $CAPTURE_FILE"
        echo ""
        echo "To stop: $0 stop"
        echo "To check status: $0 status"
        ;;
        
    stream)
        CAPTURE_FILTER="${2:-}"
        
        echo "Starting real-time packet streaming..."
        echo "Interface: $CAPTURE_INTERFACE"
        echo "Streaming port: $CAPTURE_PORT"
        if [ -n "$CAPTURE_FILTER" ]; then
            echo "Filter: $CAPTURE_FILTER"
        else
            echo "Filter: none (streaming all traffic)"
        fi
        echo ""
        echo "Connect Wireshark to: TCP@<this-ip>:$CAPTURE_PORT"
        echo "With port forwarding: TCP@localhost:<forwarded-port>"
        echo ""
        echo "Press Ctrl+C to stop streaming"
        echo ""
        
        # Create named pipe for tcpdump output
        PIPE_FILE="/tmp_ram/tcpdump_pipe"
        mkfifo "$PIPE_FILE" 2>/dev/null || true
        
        # Start tcpdump writing to pipe in background
        if [ -n "$CAPTURE_FILTER" ]; then
            tcpdump -i "$CAPTURE_INTERFACE" -w "$PIPE_FILE" -U "$CAPTURE_FILTER" &
        else
            tcpdump -i "$CAPTURE_INTERFACE" -w "$PIPE_FILE" -U &
        fi
        TCPDUMP_PID=$!
        
        # Stream pipe content via netcat
        # Note: This requires netcat to be available
        if command -v nc >/dev/null 2>&1; then
            nc -l -p "$CAPTURE_PORT" < "$PIPE_FILE" &
            NC_PID=$!
            echo "Streaming via netcat (PID: $NC_PID)"
        else
            echo "Warning: netcat not available - streaming not possible"
            echo "Install netcat or use file-based capture instead"
            kill $TCPDUMP_PID 2>/dev/null
            rm -f "$PIPE_FILE"
            exit 1
        fi
        
        # Wait for user interruption
        trap 'echo ""; echo "Stopping streaming..."; kill $TCPDUMP_PID $NC_PID 2>/dev/null; rm -f "$PIPE_FILE"; exit 0' INT TERM
        
        echo "Streaming active - tcpdump PID: $TCPDUMP_PID, netcat PID: $NC_PID"
        wait
        ;;
        
    stop)
        echo "Stopping all packet captures..."
        
        # Find and kill tcpdump processes
        TCPDUMP_PIDS=$(pidin arg | grep tcpdump | awk '{print $1}')
        if [ -n "$TCPDUMP_PIDS" ]; then
            for pid in $TCPDUMP_PIDS; do
                echo "Killing tcpdump process: $pid"
                kill "$pid" 2>/dev/null || true
            done
        else
            echo "No tcpdump processes found"
        fi
        
        # Find and kill netcat processes on capture port
        NC_PIDS=$(pidin arg | grep nc | awk '{print $1}')
        if [ -n "$NC_PIDS" ]; then
            for pid in $NC_PIDS; do
                echo "Killing netcat process: $pid"
                kill "$pid" 2>/dev/null || true
            done
        fi
        
        # Clean up pipes
        rm -f /tmp_ram/tcpdump_pipe
        
        echo "All captures stopped"
        ;;
        
    status)
        echo "Packet Capture Status"
        echo "===================="
        echo ""
        
        # Check for running tcpdump processes
        TCPDUMP_PIDS=$(pidin arg | grep tcpdump | awk '{print $1}')
        if [ -n "$TCPDUMP_PIDS" ]; then
            echo "Active tcpdump processes:"
            for pid in $TCPDUMP_PIDS; do
                echo "  PID: $pid"
            done
        else
            echo "No tcpdump processes running"
        fi
        
        # Check for netcat processes
        NC_PIDS=$(pidin arg | grep nc | awk '{print $1}')
        if [ -n "$NC_PIDS" ]; then
            echo "Active netcat processes:"
            for pid in $NC_PIDS; do
                echo "  PID: $pid"
            done
        fi
        
        echo ""
        echo "Network interface status:"
        ifconfig "$CAPTURE_INTERFACE" 2>/dev/null || echo "Interface $CAPTURE_INTERFACE not found"
        
        echo ""
        echo "Capture files:"
        if [ -d "$LOG_DIR" ] && [ "$(ls -A $LOG_DIR 2>/dev/null)" ]; then
            ls -la "$LOG_DIR"
        else
            echo "No capture files found"
        fi
        ;;
        
    list)
        echo "Saved capture files in $LOG_DIR:"
        echo ""
        if [ -d "$LOG_DIR" ] && [ "$(ls -A $LOG_DIR 2>/dev/null)" ]; then
            ls -la "$LOG_DIR"
            echo ""
            echo "To analyze with Wireshark:"
            echo "1. Copy files from QNX: scp -P 2222 root@localhost:$LOG_DIR/*.pcap ."
            echo "2. Open in Wireshark: wireshark <file>.pcap"
        else
            echo "No capture files found"
        fi
        ;;
        
    help|*)
        usage
        ;;
esac
