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


def test_com_apps_are_deployed(target):
    exit_code, out = target.execute("test -f /showcases/bin/producer_app && test -f /showcases/bin/consumer_app")
    assert exit_code == 0


def test_com_apps_are_running(target):
    # The consumer's synchronous discovery needs the producer's service already offered.
    exit_code, out = target.execute(
        "cd /showcases/data/comm; cfg=/showcases/data/comm/etc/mw_com_config.json; "
        "/showcases/bin/producer_app -s $cfg & producer=$!; sleep 1; "
        "/showcases/bin/consumer_app -s $cfg && wait $producer"
    )
    logger.info(out)
    assert exit_code == 0
