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

"""Tests for the commit timestamp conversion used by the repository rule."""

load(":opensovd_build_stamp.bzl", "timestamp_to_epoch")

def _test_impl(ctx):
    for timestamp, expected in [
        ("1970-01-01T00:00:00Z", 0),
        ("2000-02-29T12:34:56Z", 951827696),
        ("2026-11-24T15:25:37Z", 1795533937),
        ("2100-03-01T00:00:00Z", 4107542400),
    ]:
        actual = timestamp_to_epoch(timestamp)
        if actual != expected:
            fail("%s: expected %s, got %s" % (timestamp, expected, actual))
    executable = ctx.actions.declare_file(ctx.label.name + ".sh")
    ctx.actions.write(executable, "#!/bin/sh\nexit 0\n", is_executable = True)
    return [DefaultInfo(executable = executable)]

opensovd_build_stamp_test = rule(implementation = _test_impl, test = True)
