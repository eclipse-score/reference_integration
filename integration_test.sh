#!/usr/bin/env bash
set -euo pipefail

# Integration build script.
# Captures warning counts for regression tracking.
#
# Usage: ./integration_test.sh [--known-good <path>]
#   --known-good: Optional path to known_good.json file

CONFIG=${CONFIG:-bl-x86_64-linux}
LOG_DIR=${LOG_DIR:-_logs/logs}
SUMMARY_FILE=${SUMMARY_FILE:-_logs/build_summary.md}
KNOWN_GOOD_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --known-good)
            KNOWN_GOOD_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--known-good <path>]"
            exit 1
            ;;
    esac
done

mkdir -p "${LOG_DIR}" || true

# Function to extract commit hash from known_good.json
get_commit_hash() {
    local module_name=$1
    local known_good_file=$2
    
    if [[ -z "${known_good_file}" ]] || [[ ! -f "${known_good_file}" ]]; then
        echo "N/A"
        return
    fi
    
    # Get the script directory
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Use the Python script to extract module info
    python3 "${script_dir}/tools/get_module_info.py" "${known_good_file}" "${module_name}" "hash" 2>/dev/null || echo "N/A"
}

# Function to extract repo URL from known_good.json
get_module_repo() {
    local module_name=$1
    local known_good_file=$2
    
    if [[ -z "${known_good_file}" ]] || [[ ! -f "${known_good_file}" ]]; then
        echo "N/A"
        return
    fi
    
    # Get the script directory
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Use the Python script to extract module repo
    python3 "${script_dir}/tools/get_module_info.py" "${known_good_file}" "${module_name}" "repo" 2>/dev/null || echo "N/A"
}

declare -A BUILD_TARGET_GROUPS=(
    [score_baselibs]="@score_baselibs//score/..."
    [communication]="@communication//score/mw/com:com"
    [score_persistency]="@score_persistency//src/cpp/src/... @score_persistency//src/rust/..."
    #[score_logging]="@score_logging//src/..."
    [score_orchestrator]="@score_orchestrator//src/..."
    [score_test_scenarios]="@score_test_scenarios//..."
    [score_feo]="@score_feo//..."
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
if [[ -n "${KNOWN_GOOD_FILE}" ]]; then
    echo "Known Good File: ${KNOWN_GOOD_FILE}" | tee -a "${SUMMARY_FILE}"
fi
echo "" >> "${SUMMARY_FILE}"
echo "## Build Groups Summary" >> "${SUMMARY_FILE}"
echo "" >> "${SUMMARY_FILE}"
# Markdown table header
{
    echo "| Group | Status | Duration (s) | Warnings | Deprecated refs | Commit/Version |";
    echo "|-------|--------|--------------|----------|-----------------|----------------|";
} >> "${SUMMARY_FILE}"

overall_warn_total=0
overall_depr_total=0

for group in "${!BUILD_TARGET_GROUPS[@]}"; do
    targets="${BUILD_TARGET_GROUPS[$group]}"
    log_file="${LOG_DIR}/${group}.log"
    
    # Log build group banner only to stdout/stderr (not into summary table file)
    echo "--- Building group: ${group} ---"
    start_ts=$(date +%s)
    echo "bazel build --config "${CONFIG}" ${targets} --verbose_failures"
    # GitHub Actions log grouping start
    echo "::group::Bazel build (${group})"
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
    
    # Get commit hash/version for this group (group name is the module name)
    commit_hash=$(get_commit_hash "${group}" "${KNOWN_GOOD_FILE}")
    repo=$(get_module_repo "${group}" "${KNOWN_GOOD_FILE}")
    
    # Truncate commit hash for display (first 8 chars)
    if [[ "${commit_hash}" != "N/A" ]] && [[ ${#commit_hash} -gt 8 ]]; then
        commit_hash_display="${commit_hash:0:8}"
    else
        commit_hash_display="${commit_hash}"
    fi
    
    # Only add link if KNOWN_GOOD_FILE is set
    if [[ -n "${KNOWN_GOOD_FILE}" ]]; then
        commit_version_cell="[${commit_hash_display}](${repo}/tree/${commit_hash})"
    else
        commit_version_cell="${commit_hash_display}"
    fi
    
    echo "| ${group} | ${status_symbol} | ${duration} | ${w_count} | ${d_count} | ${commit_version_cell} |" | tee -a "${SUMMARY_FILE}"
done

# Append aggregate totals row to summary table
echo "| TOTAL |  |  | ${overall_warn_total} | ${overall_depr_total} |  |" >> "${SUMMARY_FILE}"# Display the full build summary explicitly at the end
echo '::group::Build Summary'
echo '=== Build Summary (echo) ==='
cat "${SUMMARY_FILE}" || echo "(Could not read summary file ${SUMMARY_FILE})"
echo '::endgroup::'