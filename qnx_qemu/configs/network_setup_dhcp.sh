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


# *******************************************************************************
# Simple DHCP Network Configuration Script
# Configures networking using DHCP with minimal configuration
# *******************************************************************************

echo "---> Starting Networking with simple DHCP"
io-sock -m phy -m pci -d vtnet_pci    # Start network stack with PHY and PCI modules, load VirtIO network driver
waitfor /dev/socket                    # Wait for socket device to become available before proceeding

echo "---> Bringing up network interface"
if_up -p vtnet0                        # Bring up the vtnet0 network interface in promiscuous mode

echo "---> Starting DHCP client with minimal config"
# Start DHCP client with minimal configuration
dhcpcd -b -f /etc/dhcpcd.conf vtnet0 &
DHCP_PID=$!                            # Store DHCP process ID

# Wait for DHCP to complete (up to 30 seconds)
echo "---> Waiting for DHCP lease acquisition..."
sleep 3                                # Initial wait for DHCP negotiation

# Check if we got an IP address
RETRY_COUNT=0
MAX_RETRIES=10                         # 10 retries * 3 seconds = 30 seconds total

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Get current IP address for vtnet0
    IP_ADDR=$(ifconfig vtnet0 | grep 'inet ' | awk '{print $2}')
    
    if [ -n "$IP_ADDR" ] && [ "$IP_ADDR" != "0.0.0.0" ]; then
        echo "---> DHCP successful! Acquired IP"
        # Get additional network info
        NETMASK=$(ifconfig vtnet0 | grep 'inet ' | awk '{print $4}')
        echo "---> Network configuration:"
        
        # Save basic DHCP status
        echo "DHCP_SUCCESS" > /tmp_ram/dhcp_status
        IP_ADDR=$(ifconfig vtnet0 | grep 'inet ' | awk '{print $2}')
        echo "IP: $IP_ADDR" >> /tmp_ram/dhcp_status
        echo "Date: $(date)" >> /tmp_ram/dhcp_status
        break
    fi
    
    echo "---> Still waiting for DHCP lease... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 3
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

# Check final status
IP_ADDR=$(ifconfig vtnet0 | grep 'inet ' | awk '{print $2}')
if [ -z "$IP_ADDR" ] || [ "$IP_ADDR" = "0.0.0.0" ]; then
    echo "---> DHCP failed! Falling back to static IP configuration..."
    # Kill DHCP client if still running
    if kill -0 $DHCP_PID 2>/dev/null; then
        kill $DHCP_PID 2>/dev/null
    fi
    
    # Configure static IP as fallback
    echo "---> Configuring static IP fallback: 192.168.122.100"
    ifconfig vtnet0 192.168.122.100 netmask 255.255.255.0
    route add default 192.168.122.1  # Add default gateway
    
    # Save fallback status
    echo "DHCP_FAILED_STATIC_FALLBACK" > /tmp_ram/dhcp_status
    echo "IP: 192.168.122.100" >> /tmp_ram/dhcp_status
    echo "Date: $(date)" >> /tmp_ram/dhcp_status
else
    echo "---> DHCP configuration completed successfully"
fi

# Configure system network settings
sysctl -w net.inet.icmp.bmcastecho=1 > /dev/null        # Enable ICMP broadcast echo (responds to broadcast pings)

echo "---> Network configuration completed"
