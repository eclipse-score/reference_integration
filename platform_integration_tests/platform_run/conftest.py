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
import copy

import pytest


@pytest.fixture
def dlt_config(dlt_config, target):
    """Point host_ip/target_ip at the Docker target's per-container bridge.

    Same override as feature_integration_tests/itf/conftest.py: the ITF Docker
    plugin puts each container on its own bridge, so the gateway in the static
    DLT config does not reach the host-side dlt-receive.
    """
    if not hasattr(target, "get_gateway"):
        return dlt_config

    gateway = target.get_gateway()
    cfg = copy.copy(dlt_config)
    cfg.host_ip = gateway
    cfg.target_ip = gateway
    return cfg
