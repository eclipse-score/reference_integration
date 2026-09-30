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
"""Helper for driving showcases via the showcase CLI entrypoint."""

import logging

logger = logging.getLogger(__name__)

_CLI = "/showcases/bin/cli"


def run_showcases(target, *names: str) -> None:
    """Run the named showcases via the showcase entrypoint and assert success.

    ``run_score`` in the showcase CLI prints a per-example completion banner
    and exits 0 once every app of an example has been spawned and joined, so
    both the exit code and the banner are checked to confirm the showcase ran
    end-to-end on the platform.
    """
    selection = ",".join(names)
    exit_code, out = target.execute(f"{_CLI} --examples='{selection}'")
    output = out.decode(errors="replace")
    logger.info(output)
    assert exit_code == 0, f"Showcase CLI exited with {exit_code}:\n{output}"
    for name in names:
        assert f"Example '{name}' finished successfully" in output, (
            f"Showcase '{name}' did not finish successfully:\n{output}"
        )
