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
try:
    from attribute_plugin import add_test_properties  # type: ignore[import-untyped]
except ImportError:
    # Define no-op decorator if attribute_plugin is not available (outside bazel)
    # Keeps IDE debugging functionality
    def add_test_properties(*args, **kwargs):
        def decorator(func):
            return func  # No-op decorator

        return decorator
