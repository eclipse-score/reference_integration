#!/bin/bash
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
# Script to run C++ persistency tests inside the QEMU environment
# Wrapper due to quoting issues when calling directly from Bazel
cpp_tests_persistency --name basic.basic --input '{"kvs_parameters":{"instance_id":0}}'
