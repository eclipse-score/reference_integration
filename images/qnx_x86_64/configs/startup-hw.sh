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

# x86_64-specific early hardware initialisation, sourced by the common
# /etc/startup.sh: start the PCI bus services and the IDE/SATA block driver.
# The IDE/SATA controller is a PCI device, so pci-server must come first.

echo "---> Starting PCI Services"
pci-server --config=/proc/boot/pci_server.cfg  # Start PCI server with configuration file
waitfor /dev/pci                        # Wait for PCI device manager to initialize

echo "---> Starting devb-eide"
devb-eide cam user=20:20 blk cache=64M,auto=partition,vnode=2000,ncache=2000,commit=low  # Start IDE/SATA block driver
waitfor /dev/hd0                        # Wait for first hard disk to be detected
