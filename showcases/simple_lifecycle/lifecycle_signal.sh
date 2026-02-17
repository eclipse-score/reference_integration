#! /bin/sh
# This script sends a signal to a process by name. It uses `slay` on QNX and `pkill` on other systems.
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
else
    pkill -$signal -f $process_name
fi
