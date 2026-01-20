#!/usr/bin/env bash
set -uo pipefail

# Integration unit test script.

CONFIG=${CONFIG:-bl-x86_64-linux}
LOG_DIR=${LOG_DIR:-_logs/logs_ut}
SUMMARY_FILE=${SUMMARY_FILE:-_logs/ut_summary.md}
mkdir -p "${LOG_DIR}" || true

declare -A UT_TARGET_GROUPS=(
    [baselibs]="@score_baselibs//score/...  -- \
        -@score_baselibs//score/language/safecpp/aborts_upon_exception:abortsuponexception_toolchain_test \
        -@score_baselibs//score/containers:dynamic_array_test \
        -@score_baselibs//score/mw/log/configuration:*  \
        -@score_baselibs//score/json/examples:*"
    # DISABLED: All communication tests fail with linker error:
    # undefined reference to 'score::mw::log::detail::CreateRecorderFactory()'
    # The logging library symbols are not properly available during linking.
    # This affects both direct communication tests and tests that depend on logging.
    # [communication]="@score_communication//score/mw/com/impl/...   -- \
    #     -@score_communication//score/mw/com/impl:unit_test_runtime_single_exec \
    #     -@score_communication//score/mw/com/impl/configuration:config_parser_test \
    #     -@score_communication//score/mw/com/impl/configuration:configuration_test \
    #     -@score_communication//score/mw/com/impl/tracing/configuration:tracing_filter_config_parser_test"
    [persistency]="@score_persistency//:unit_tests -- \
        -@score_persistency//src/cpp/tests:test_kvs_cpp" # C++ test has linker issues with logging library
    [orchestrator]="@score_orchestrator//src/..." # ok
    [kyron]="@score_kyron//:unit_tests" # ok
    [feo]="@score_feo//... --build_tests_only" # ok (flag required or error from docs)
    [logging]="@score_logging//score/... \
        --@score_baselibs//score/memory/shared/flags:use_typedshmd=False \
        --@score_baselibs//score/json:base_library=nlohmann \
        --@score_logging//score/datarouter/build_configuration_flags:persistent_logging=False \
        --@score_logging//score/datarouter/build_configuration_flags:persistent_config_feature_enabled=False \
        --@score_logging//score/datarouter/build_configuration_flags:enable_nonverbose_dlt=False \
        --@score_logging//score/datarouter/build_configuration_flags:enable_dynamic_configuration_in_datarouter=False \
        --@score_logging//score/datarouter/build_configuration_flags:dlt_file_transfer_feature=False \
        --@score_logging//score/datarouter/build_configuration_flags:use_local_vlan=True \
        --test_tag_filters=-manual \
        -- -@score_logging//score/datarouter/test/ut/ut_logging:dltprotocolUT \
        -@score_logging//score/datarouter/test/ut/ut_logging:persistentLogConfigUT \
        -@score_logging//score/datarouter/test/ut/ut_logging:socketserverConfigUT \
        -@score_logging//score/mw/log/legacy_non_verbose_api:unit_test "
)

# Markdown table header
echo -e "Status\tPassed\tFailed\tSkipped\tTotal\tGroup\tDuration(s)" >> "${SUMMARY_FILE}"

# Track if any test failed
any_failed=0

for group in "${!UT_TARGET_GROUPS[@]}"; do
    targets="${UT_TARGET_GROUPS[$group]}"
    command="bazel test --config="${CONFIG}" ${targets}"
    echo "==========================================="
    echo "Running unit tests for group: $group"
    echo "${command}"
    echo "==========================================="
    start_ts=$(date +%s)
    out=$(bazel test --test_summary=testcase --test_output=errors --nocache_test_results --config="${CONFIG}" ${targets} 2>&1 | tee "${LOG_DIR}/ut_${group}_output.log")
    build_status=${PIPESTATUS[0]}
    end_ts=$(date +%s)
    duration=$(( end_ts - start_ts ))

    # Parse bazel output
    tests_passed=$(echo "$out" | grep -Eo '[0-9]+ passing' | grep -Eo '[0-9]+' | head -n1)
    tests_failed=$(echo "$out" | grep -Eo '[0-9]+ failing' | grep -Eo '[0-9]+' | head -n1)
    tests_skipped=$(echo "$out" | grep -Eo '[0-9]+ skipped' | grep -Eo '[0-9]+' | head -n1)
    tests_executed=$(echo "$out" | grep -Eo '[0-9]+ test cases' | grep -Eo '[0-9]+' | head -n1)
    if [[ ${build_status} -eq 0 ]]; then
        status_symbol="✅"
    else
        status_symbol="❌"
        any_failed=1
    fi

    # Append as a markdown table row
    echo -e "${status_symbol}\t${tests_passed}\t${tests_failed}\t${tests_skipped}\t${tests_executed}\t${group}\t${duration}s" | tee -a "${SUMMARY_FILE}"
    echo "==========================================="
    echo -e "\n\n"
done

# Align the summary table columns
column -t -s $'\t' "${SUMMARY_FILE}" > "${SUMMARY_FILE}.tmp" && mv "${SUMMARY_FILE}.tmp" "${SUMMARY_FILE}"

# Final check: exit with non-zero if any test failed
if [[ $any_failed -ne 0 ]]; then
    echo "Some unit test groups failed. Exiting with non-zero status."
    exit 1
fi
