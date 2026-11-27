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


def run_showcases(target, *names: str) -> str:
    """Run the named showcases via the showcase entrypoint and return output.

    The exit code and the per-example banner only prove the CLI spawned and
    joined every app; they do NOT prove each app succeeded, because the CLI
    discards the apps' exit codes (``// anyhow::bail!`` is commented out in
    ``cli/main.rs``).  Callers must assert meaningful content in the returned
    output to confirm that the platform feature under test actually worked.
    """
    selection = ",".join(names)
    # Apps such as the lifecycle control daemon report on stderr; merge it so
    # the returned output is complete on every target backend.
    exit_code, out = target.execute(f"{_CLI} --examples='{selection}' 2>&1")
    output = out.decode(errors="replace")
    logger.info(output)
    assert exit_code == 0, f"Showcase CLI exited with {exit_code}:\n{output}"
    for name in names:
        assert f"Example '{name}' finished successfully" in output, (
            f"Showcase '{name}' did not finish successfully:\n{output}"
        )
    return output
