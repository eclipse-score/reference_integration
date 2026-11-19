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

# Checks the OpenSOVD gateway and the classic diagnostic adapter (CDA) that the platform deploys:
# the gateway answers and forwards to the CDA, it lists the app of the CDA next to its own. There
# is no ECU here. If the stack does not run yet (the image of the EB QEMU target starts it as a
# service at boot), this starts it with service.sh for the check and stops it afterwards.
# Prints "diagnostics_check: PASSED" on success.

DATA=/showcases/data/diagnostics
LOG_DIR="$(mktemp -d)"

launch_manager=
stop() {
    [[ -n "$launch_manager" ]] || return 0
    kill -s TERM "$launch_manager" 2>/dev/null
    wait 2>/dev/null
}
trap stop EXIT

fail() {
    echo "diagnostics_check: FAILED: $1"
    for log in "$LOG_DIR"/*.log; do
        echo "--- $log"
        tail -n 20 "$log"
    done
    exit 1
}

# The addresses of this host to try, the loopback address first: the gateway listens on all
# addresses, or on the Raspberry Pi images on the address of the image only.
hosts() {
    echo 127.0.0.1
    ip -4 -o addr show 2>/dev/null | awk '$2 != "lo" { sub("/.*", "", $4); print $4 }'
}

# request <port> <path>: prints the status line and, on the next line, the body of a GET to the
# first address of this host that answers. Prints nothing if nothing listens or the whole answer
# does not arrive within 5 seconds, so a listener that never answers cannot block the check.
request() {
    local host
    for host in $(hosts); do
        timeout 5 bash -c '
            exec 3<>"/dev/tcp/$1/$2" || exit 1
            printf "GET %s HTTP/1.0\r\nHost: %s:%s\r\n\r\n" "$3" "$1" "$2" >&3
            read -r status <&3
            body="$(cat <&3 | tr -d "\r" | sed "1,/^\$/d")"
            echo "$status"
            echo "$body"' request "$host" "$1" "$2" 2>/dev/null && return 0
    done
}

# The CDA offers the app sovd2uds, the gateway its own app score-diagnostics: both are listed only
# if the gateway forwards to the CDA.
lists_both_apps() {
    [[ "$(head -1 <<<"$1")" == *" 200"* && "$1" == *'"sovd2uds"'* && "$1" == *'"score-diagnostics"'* ]]
}

if [[ -n "$(request 7690 /sovd/v1/apps | head -1)" ]]; then
    echo "diagnostics_check: the diagnostics service is running"
else
    "$DATA/service.sh" >"$LOG_DIR/service.log" 2>&1 &
    launch_manager=$!
fi

# The gateway starts after the CDA, and it can answer with its own app only while the CDA still
# loads the databases: wait until it lists both.
answer=
for _ in $(seq 1 120); do
    answer="$(request 7690 /sovd/v1/apps)"
    lists_both_apps "$answer" && break
    [[ -z "$launch_manager" ]] || kill -0 "$launch_manager" 2>/dev/null || fail "the launch manager exited"
    sleep 1
done
[[ -n "$answer" ]] || fail "the gateway does not answer on port 7690"
echo "diagnostics_check: the gateway answers on port 7690"
lists_both_apps "$answer" || fail "the gateway does not list the apps of the CDA next to its own: $answer"
echo "diagnostics_check: the gateway lists the app of the CDA next to its own"

echo "diagnostics_check: PASSED"
