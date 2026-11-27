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
"""Check that diagnostics uses a separate LoLa instance and application ID."""

import json
import sys
from pathlib import Path


def main():
    original = json.loads(Path(sys.argv[1]).read_text())
    diagnostics = json.loads(Path(sys.argv[2]).read_text())
    instances = original["serviceInstances"]
    assert {instance["instanceSpecifier"] for instance in instances} == {
        "LaunchManager/StateManager/Instance",
        "StateManager/LaunchManager/Instance",
    }
    for service in instances:
        assert service["serviceTypeName"] == "/score/mw/lifecycle/LmControlService"
        assert len(service["instances"]) == 1
        assert service["instances"][0]["instanceId"] == 1
        service["instances"][0]["instanceId"] = 2
    assert original["global"]["applicationID"] == 1000
    original["global"]["applicationID"] = 1001
    assert diagnostics == original


if __name__ == "__main__":
    main()
