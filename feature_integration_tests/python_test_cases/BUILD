load("@pip_score_venv_test//:requirements.bzl", "all_requirements")
load("@rules_python//python:pip.bzl", "compile_pip_requirements")
load("@score_tooling//python_basics:defs.bzl", "score_py_pytest", "score_virtualenv")

# In order to update the requirements, change the `requirements.txt` file and run:
# `bazel run //feature_integration_tests/python_test_cases:requirements.update`.
# This will update the `requirements.txt.lock` file.
# To upgrade all dependencies to their latest versions, run:
# `bazel run //feature_integration_tests/python_test_cases:requirements.update -- --upgrade`.
compile_pip_requirements(
    name = "requirements",
    srcs = [
        "requirements.txt",
        "@score_tooling//python_basics:requirements.txt",
    ],
    requirements_txt = "requirements.txt.lock",
    tags = [
        "manual",
    ],
)

score_virtualenv(
    name = "python_tc_venv",
    reqs = all_requirements,
    venv_name = ".python_tc_venv",
)

# Tests targets
score_py_pytest(
    name = "fit",
    srcs = glob(["tests/**/*.py"]) + ["conftest.py", "fit_scenario.py", "test_properties.py"],
    args = [
        "--traces=all",
        "--rust-target-path=$(rootpath //feature_integration_tests/rust_test_scenarios)",
    ],
    data = [
        ":python_tc_venv",
        "//feature_integration_tests/rust_test_scenarios",
    ],
    env = {
        "RUST_BACKTRACE": "1",
    },
    pytest_ini = ":pytest.ini",
    deps = all_requirements,
)
