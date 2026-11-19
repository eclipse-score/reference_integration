#!/bin/bash
# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
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

# The diagnostics stack as a service, in the foreground: the launch manager starts the CDA and then
# the gateway (etc/ holds its configuration), and supervises them. The CDA finds the ECUs by DoIP
# broadcast from the address that the host picks for it, so this waits until the host has an
# address. The image starts it at boot (crinit task diagnostics), the showcase check starts it
# when it does not run yet.

DATA=/showcases/data/diagnostics

has_address() {
    [[ -n "$(ip -4 -o addr show 2>/dev/null | grep -v ' lo ')" || -n "$(hostname -I 2>/dev/null)" ]]
}

for _ in $(seq 1 60); do
    has_address && break
    sleep 1
done

cd "$DATA" || exit 1
# Under a name of its own: other showcases stop "their" launch manager by name (pkill -f
# launch_manager in simple_lifecycle), which must not stop this service.
exec -a diagnostics_lm /usr/bin/launch_manager
