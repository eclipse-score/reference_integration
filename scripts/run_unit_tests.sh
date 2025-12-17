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
        -@score_baselibs//score/containers:dynamic_array_test" # nok, error in @score_baselibs//score/json/examples:json_buffer
    [communication]="@score_communication//score/..." # nok, error from trlc in score_communication//score/mw/com/requirements/feature_requirements
    [persistency]="@score_persistency//:unit_tests" # ok
    [orchestrator]="@score_orchestrator//src/..." # ok
    [kyron]="@score_kyron//:unit_tests" # ok
    [feo]="@score_feo//... --build_tests_only" # ok (flag required or error from docs)
)

# Markdown table header
echo -e "Status\tPassed\tFailed\tSkipped\tTotal\tGroup\tDuration(s)" >> "${SUMMARY_FILE}"

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
    fi
    
    # Append as a markdown table row
    echo -e "${status_symbol}\t${tests_passed}\t${tests_failed}\t${tests_skipped}\t${tests_executed}\t${group}\t${duration}s" >> "${SUMMARY_FILE}"
    echo "==========================================="
    echo -e "\n\n"
done

# Align the summary table columns
column -t -s $'\t' "${SUMMARY_FILE}" > "${SUMMARY_FILE}.tmp" && mv "${SUMMARY_FILE}.tmp" "${SUMMARY_FILE}"
