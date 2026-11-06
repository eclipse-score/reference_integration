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
# This script sends a signal to a process by name. It uses `slay` on QNX, `pkill` where available
# and otherwise scans /proc, so it also works on minimal Linux systems without procps.
# Usage: lifecycle_signal.sh <process_name> <signal>
# Example: lifecycle_signal.sh my_process SIGTERM

running_on_qnx() {
    [ -x "$(command -v slay)" ]
}

process_name=$1
signal=$2

if running_on_qnx
then
    slay -s $signal -f $process_name
elif [ -x "$(command -v pkill)" ]
then
    pkill -$signal -f $process_name
else
    for proc in /proc/[0-9]*
    do
        pid=${proc#/proc/}
        # Like pkill, skip this script, whose own command line contains the name.
        [ "$pid" = "$$" ] && continue
        if tr '\0' ' ' 2>/dev/null < "$proc/cmdline" | grep -q -- "$process_name"
        then
            kill -s "${signal#SIG}" "$pid" 2>/dev/null
        fi
    done
fi
