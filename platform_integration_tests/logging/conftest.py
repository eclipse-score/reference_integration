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
    """Override the session-scoped dlt_config so host_ip/target_ip track the
    Docker target's actual per-container bridge.

    Since score_itf 0.5.0 (commit bb3a788, "docker: Create per-container bridge
    network") the Docker plugin no longer places the container on the default
    ``bridge`` network. It creates a dedicated ``score_itf_<rand>`` bridge with
    its own subnet, so the ``172.17.0.1`` value hardcoded in
    ``configs/dlt_config_x86_64.json`` no longer matches the container's real
    gateway and DLT UDP multicast never reaches the host-side ``dlt-receive``.

    On QEMU targets (QNX) ``get_gateway`` is not available; the static IPs from
    the JSON config are still correct there and we return the session-scoped
    value unchanged.
    """
    if not hasattr(target, "get_gateway"):
        return dlt_config

    gateway = target.get_gateway()
    cfg = copy.copy(dlt_config)
    cfg.host_ip = gateway
    cfg.target_ip = gateway
    return cfg
