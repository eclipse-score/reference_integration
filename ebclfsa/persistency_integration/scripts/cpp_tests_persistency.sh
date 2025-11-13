#!/bin/bash
# Script to run C++ persistency tests inside the QEMU environment
# Wrapper due to quoting issues when calling directly from Bazel
cpp_tests_persistency --name basic.basic --input '{"kvs_parameters":{"instance_id":0}}'
