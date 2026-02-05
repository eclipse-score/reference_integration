#!/bin/sh

# This script is required to run a simple smoke test via itf.
# It starts the launch manager, lets it run a couple of seconds and terminates it.

cd /lifecycle/launch_manager
./launch_manager&
sleep 10
slay launch_manager

# Slay returns 1 if a single launch_manager process was found
retVal=$?
if [ $retVal -eq 1 ]; then
    exit 0
fi