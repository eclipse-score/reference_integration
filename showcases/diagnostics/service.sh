#!/bin/sh
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

set -eu

DATA=/showcases/data/diagnostics

# Hold the lock from before the network wait until the manager has stopped. A
# boot service waits for a check that got there first; a check instead joins an
# existing service and waits for it to become ready.
lock=/run/score-diagnostics.lock.d
lock_owned=false
manager=
cleanup() {
    if [ -n "$manager" ]; then
        kill -s TERM "$manager" 2>/dev/null || true
        wait "$manager" 2>/dev/null || true
    fi
    if "$lock_owned"; then
        rmdir "$lock"
    fi
}
exec 9>/run/score-diagnostics.lock
if [ "$(uname -s)" = QNX ]; then
    # QNX has no util-linux flock. A trapped directory lock is shared by boot and checks.
    while ! mkdir "$lock" 2>/dev/null; do
        [ -d "$lock" ] || exit 1
        [ "${1:-}" != --if-not-running ] || exit 75
        sleep 1
    done
    lock_owned=true
elif [ "${1:-}" = --if-not-running ]; then
    flock -n -E 75 9 || exit $?
else
    flock 9
fi
trap cleanup EXIT
trap 'exit 0' TERM INT

has_address() {
    if [ "$(uname -s)" = QNX ]; then
        ifconfig -a | awk '$1 == "inet" && $2 != "127.0.0.1" { found = 1 } END { exit !found }'
    else
        ip -4 -o addr show 2>/dev/null | grep -qv ' lo ' ||
            [ -n "$(hostname -I 2>/dev/null)" ]
    fi
}

for _ in $(seq 1 60); do
    has_address && break
    sleep 1
done

cd "$DATA" || exit 1
# Under a name of its own: other showcases stop "their" launch manager by name (pkill -f
# launch_manager in simple_lifecycle), which must not stop this service. Both Bash on Linux
# and ksh on QNX support exec -a; /bin/sh on Linux need not support it.
if [ "$(uname -s)" = QNX ]; then
    /bin/sh -c 'exec 9>&-; exec -a diagnostics_lm /usr/bin/launch_manager' &
else
    /bin/bash -c 'exec 9>&-; exec -a diagnostics_lm /usr/bin/launch_manager' &
fi
manager=$!
wait "$manager"
