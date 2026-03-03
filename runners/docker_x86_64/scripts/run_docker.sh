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

OCI_TARBALL_IMAGE_SCRIPT=$1
OCI_TARBALL_IMAGE_SCRIPT_ABS_PATH=$(realpath ${OCI_TARBALL_IMAGE_SCRIPT})

if [ -z "${OCI_IMAGE:-}" ]; then
  echo "Error: OCI_IMAGE environment variable is not set."
  exit 1
fi

OCI_IMAGE=${OCI_IMAGE:=score_showcases:latest}


echo "Starting docker with OCI image tarball at: ${OCI_TARBALL_IMAGE_SCRIPT_ABS_PATH}"

${OCI_TARBALL_IMAGE_SCRIPT_ABS_PATH}

echo "Running docker with image: ${OCI_IMAGE}"
docker run --rm -it \
    ${OCI_IMAGE} \
    bash -c "/showcases/bin/cli; exec bash"
