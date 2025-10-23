#!/usr/bin/env bash
set -euo pipefail

# Integration build script.
# Captures warning counts for regression tracking.

CONFIG=${CONFIG:-bl-x86_64-linux}
LOG_DIR=${LOG_DIR:-_logs/logs}
SUMMARY_FILE=${SUMMARY_FILE:-_logs/build_summary.txt}
mkdir -p "${LOG_DIR}" || true

declare -A BUILD_TARGET_GROUPS=(
    [baselibs]="@score-baselibs//..."
    [communication]="@communication//score/..."
    [persistency]="@score_persistency//src/... @score_persistency//tests/cpp_test_scenarios/... @score_persistency//tests/rust_test_scenarios/..."
)

warn_count() {
    # Grep typical compiler and Bazel warnings; adjust patterns as needed.
    local file=$1
    # Count lines with 'warning:' excluding ones from system headers optionally later.
    grep -i 'warning:' "$file" | wc -l || true
}

depr_count() {
    local file=$1
    grep -i 'deprecated' "$file" | wc -l || true
}

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

echo "=== Integration Build Started $(timestamp) ===" | tee "${SUMMARY_FILE}"
echo "Config: ${CONFIG}" | tee -a "${SUMMARY_FILE}"

overall_warn_total=0
overall_depr_total=0

for group in baselibs communication persistency; do
    targets="${BUILD_TARGET_GROUPS[$group]}"
    log_file="${LOG_DIR}/${group}.log"
    echo "--- Building group: ${group} ---" | tee -a "${SUMMARY_FILE}"
    # GitHub Actions log grouping start
    echo "::group::Bazel build (${group})"
    start_ts=$(date +%s)
    if [[ "$group" == "persistency" ]]; then
        # Extra flags only for persistency group.
        set +e
        bazel build --config "${CONFIG}" \
            ${targets} \
            --extra_toolchains=@llvm_toolchain//:cc-toolchain-x86_64-linux \
            --copt=-Wno-deprecated-declarations \
            --verbose_failures 2>&1 | tee "$log_file"
        build_status=${PIPESTATUS[0]}
        set -e
    else
        set +e
        bazel build --config "${CONFIG}" ${targets} --verbose_failures 2>&1 | tee "$log_file"
        build_status=${PIPESTATUS[0]}
        set -e
    fi
    echo "::endgroup::"  # End Bazel build group
    end_ts=$(date +%s)
    duration=$(( end_ts - start_ts ))
    w_count=$(warn_count "$log_file")
    d_count=$(depr_count "$log_file")
    overall_warn_total=$(( overall_warn_total + w_count ))
    overall_depr_total=$(( overall_depr_total + d_count ))
        echo "Group: ${group} | Status: ${build_status} | Duration: ${duration}s | Warnings: ${w_count} | Deprecated refs: ${d_count}" | tee -a "${SUMMARY_FILE}"
done

# Display the full build summary explicitly at the end
echo '::group::Build Summary'
echo '=== Build Summary (echo) ==='
cat "${SUMMARY_FILE}" || echo "(Could not read summary file ${SUMMARY_FILE})"
echo '::endgroup::'

exit 0