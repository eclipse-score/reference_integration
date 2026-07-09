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
load("@score_tooling//cpp/libclang:libclang_toolchain.bzl", "libclang_toolchain")

# libclang toolchain for the score_tooling C++ parser. score_tooling deliberately
# does not register a libclang toolchain for its consumers, so the reference
# integration provides and registers its own (see .bazelrc --extra_toolchains).
# It wraps the LLVM installation declared in
# //bazel_common:score_llvm_libclang.MODULE.bazel.
libclang_toolchain(
    name = "score_ref_int_libclang",
    cxx_builtin_include = "@llvm_toolchain_llvm//:cxx_builtin_include",
    extra_config_site = "@llvm_toolchain_llvm//:extra_config_site",
    libclang = "@llvm_toolchain_llvm//:lib/libclang.so",
    visibility = ["//visibility:public"],
)

toolchain(
    name = "score_ref_int_libclang_toolchain",
    toolchain = ":score_ref_int_libclang",
    toolchain_type = "@score_tooling//cpp/libclang:libclang_toolchain_type",
    visibility = ["//visibility:public"],
)
