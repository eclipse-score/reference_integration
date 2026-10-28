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
"""s-core TCK - Test Compatibility Kit for SCORE Platform Distributions.

This package implements a TCK inspired by the Jakarta EE Platform TCK model.
It lets vendors verify their SCORE distribution is compatible with the main
platform requirements (APIs, SBOM policy, behavioral conformance).

The runner is a self-contained Python zipapp that can run offline. It bundles:
- Golden reference data (SBOM, requirement mappings, policy)
- Check implementations (SBOM comparison, API diff, behavioral)
- Report generation (JSON + HTML)

Usage:
    score-tck run --config dist.toml --report ./report
"""

__version__ = "0.1.0"
