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


# --- begin runfiles.bash initialization v3 ---
# Copy-pasted from the Bazel Bash runfiles library v3.
# https://github.com/bazelbuild/rules_shell/blob/main/shell/runfiles/runfiles.bash
set -uo pipefail; set +e; f=bazel_tools/tools/bash/runfiles/runfiles.bash
source "${RUNFILES_DIR:-/dev/null}/$f" 2>/dev/null || \
  source "$(grep -sm1 "^$f " "${RUNFILES_MANIFEST_FILE:-/dev/null}" | cut -f2- -d' ')" 2>/dev/null || \
  source "$0.runfiles/$f" 2>/dev/null || \
  source "$(grep -sm1 "^$f " "$0.runfiles_manifest" | cut -f2- -d' ')" 2>/dev/null || \
  source "$(grep -sm1 "^$f " "$0.exe.runfiles_manifest" 2>/dev/null | cut -f2- -d' ')" 2>/dev/null || \
  { echo>&2 "ERROR: cannot find $f"; exit 1; }; f=; set -e
# --- end runfiles.bash initialization v3 ---

set -euo pipefail

# Export the runfiles environment variables (RUNFILES_DIR, RUNFILES_MANIFEST_FILE, etc.)
# into the process environment so that child scripts inherit them. This is required because
# the OCI_TARBALL_IMAGE_SCRIPT (oci_load.sh) is itself a Bazel-generated runfiles-aware
# script that relies on these variables to locate the OCI image tarball within the runfiles
# tree at runtime. Without exporting them here, oci_load.sh would be unable to resolve its
# own runfiles paths and would fail to find the image.
# This might be related to a bug ticket in rules_oci https://github.com/bazel-contrib/rules_oci/issues/874
runfiles_export_envvars

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
