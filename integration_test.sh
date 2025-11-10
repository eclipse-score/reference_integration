#!/usr/bin/env bash
set -euox pipefail

# Integration build script.
# Captures warning counts for regression tracking.

CONFIG=${CONFIG:-bl-x86_64-linux}
LOG_DIR=${LOG_DIR:-_logs/logs}
SUMMARY_FILE=${SUMMARY_FILE:-_logs/build_summary.md}
mkdir -p "${LOG_DIR}" || true

declare -A BUILD_TARGET_GROUPS=(
    [baselibs]="@score_baselibs//score/..."
    [score_communication]="@score_communication//score/mw/com:com"
    [persistency]="@score_persistency//src/cpp/src/... @score_persistency//src/rust/..."
    #[score_logging]="@score_logging//src/..."
    [score_orchestrator]="@score_orchestrator//src/..."
    [score_test_scenarios]="@score_test_scenarios//..."
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
echo "" >> "${SUMMARY_FILE}"
echo "## Build Groups Summary" >> "${SUMMARY_FILE}"
echo "" >> "${SUMMARY_FILE}"
# Markdown table header
{
    echo "| Group | Status | Duration (s) | Warnings | Deprecated refs |";
    echo "|-------|--------|--------------|----------|-----------------|";
} >> "${SUMMARY_FILE}"

overall_warn_total=0
overall_depr_total=0

for group in "${!BUILD_TARGET_GROUPS[@]}"; do
    targets="${BUILD_TARGET_GROUPS[$group]}"
    log_file="${LOG_DIR}/${group}.log"
    # Log build group banner only to stdout/stderr (not into summary table file)
    echo "--- Building group: ${group} ---"
    # GitHub Actions log grouping start
    echo "::group::Bazel build (${group})"
    start_ts=$(date +%s)
    set +e
    bazel build --config "${CONFIG}" ${targets} --verbose_failures 2>&1 | tee "$log_file"
    build_status=${PIPESTATUS[0]}
    set -e
    echo "::endgroup::"  # End Bazel build group
    end_ts=$(date +%s)
    duration=$(( end_ts - start_ts ))
    w_count=$(warn_count "$log_file")
    d_count=$(depr_count "$log_file")
    overall_warn_total=$(( overall_warn_total + w_count ))
    overall_depr_total=$(( overall_depr_total + d_count ))
    # Append as a markdown table row (duration without trailing 's')
    if [[ ${build_status} -eq 0 ]]; then
        status_symbol="✅"
    else
        status_symbol="❌(${build_status})"
    fi
    echo "| ${group} | ${status_symbol} | ${duration} | ${w_count} | ${d_count} |" | tee -a "${SUMMARY_FILE}"
done

# Append aggregate totals row to summary table
echo "| TOTAL |  |  | ${overall_warn_total} | ${overall_depr_total} |" >> "${SUMMARY_FILE}"

# Display the full build summary explicitly at the end
echo '::group::Build Summary'
echo '=== Build Summary (echo) ==='
cat "${SUMMARY_FILE}" || echo "(Could not read summary file ${SUMMARY_FILE})"
echo '::endgroup::'

exit 0