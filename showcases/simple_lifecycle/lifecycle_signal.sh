#! /bin/sh
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
# This script sends a signal to a process by name. It uses `slay` on QNX and otherwise scans /proc,
# so it also works on minimal Linux systems without procps.
# Exits 0 if at least one process was signalled, 1 otherwise.
# Usage: lifecycle_signal.sh <process_name> <signal>
# Example: lifecycle_signal.sh my_process SIGTERM

running_on_qnx() {
    [ -x "$(command -v slay)" ]
}

process_name=$1
signal=$2

if running_on_qnx
then
    # slay exits with the number of processes it signalled.
    slay -s $signal -f $process_name
    [ $? -ne 0 ]
    exit
fi

# Not pkill -f: it would also match and kill this script, whose command line contains the name.
signalled=1
for proc in /proc/[0-9]*
do
    pid=${proc#/proc/}
    [ "$pid" = "$$" ] && continue
    if tr '\0' ' ' 2>/dev/null < "$proc/cmdline" | grep -q -- "$process_name"
    then
        kill -s "${signal#SIG}" "$pid" 2>/dev/null && signalled=0
    fi
done
exit $signalled
