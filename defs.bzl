"""ITF public Bazel interface"""

load("@score_itf//bazel:py_itf_test.bzl", local_py_itf_test = "py_itf_test")

py_itf_test = local_py_itf_test
