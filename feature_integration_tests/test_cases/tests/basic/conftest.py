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
import pytest


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Tolerate an empty ``-m cpp`` selection under tests/basic/ instead of failing the build.

    fit_cpp_orch runs ``-m cpp`` here, but every test under tests/basic/ is currently
    @pytest.mark.rust-only, so today's selection is legitimately empty. Without this,
    pytest's NO_TESTS_COLLECTED exit code would fail fit_cpp_orch permanently until a cpp
    test exists. Once a cpp-marked test is added under tests/basic/, testscollected > 0
    and this hook no longer applies - the target then runs (and can fail) normally.
    """
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED and session.testscollected == 0:
        markexpr = session.config.getoption("markexpr", "")
        if "cpp" in markexpr:
            print(
                "fit_cpp_orch: no @pytest.mark.cpp tests exist under tests/basic/ yet - "
                "treating the empty selection as a pass. Add one and this target will "
                "start actually running it."
            )
            session.exitstatus = pytest.ExitCode.OK
