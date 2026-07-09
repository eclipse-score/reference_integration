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

import logging


logger = logging.getLogger(__name__)


def test_com_api_example_app_is_deployed(target):
    exit_code, out = target.execute("test -f /showcases/bin/com-api-example")
    assert exit_code == 0


def test_com_api_example_app_is_running(target):
    exit_code, out = target.execute(
        "cd /showcases/data/comm; /showcases/bin/com-api-example -s /showcases/data/comm/etc/mw_com_config.json"
    )
    logger.info(out)
    assert exit_code == 0


def test_run_all_showcases(target):
    exit_code, out = target.execute("/showcases/bin/cli --examples=all")
    logger.info(out)
    assert exit_code == 0
