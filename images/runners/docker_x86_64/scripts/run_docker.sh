#!/bin/bash

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

set -euo pipefail

OVERLAY_TREE=$1
OVERLAY_ABS_PATH=$(realpath ${OVERLAY_TREE})
echo "Starting docker with overlay image: ${OVERLAY_ABS_PATH}"
docker run --rm -it \
    -v "${OVERLAY_ABS_PATH}:/showcases" \
    ubuntu:22.04 \
    /showcases/bin/cli