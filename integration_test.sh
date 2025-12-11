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

# Codeql

CODEQL_WORK_DIR="./codeql_analysis_results"
CODEQL_DATABASES_DIR="${CODEQL_WORK_DIR}/databases"
CODEQL_SARIF_DIR="${CODEQL_WORK_DIR}/sarif"
CODEQL_LANGUAGE="cpp"
CODEQL_QUERY_PACKS="codeql/cpp-queries,codeql/misra-cpp-coding-standards" # Add more packs as needed
CODEQL_CLI_VERSION="v2.23.6" # Use the latest stable version
CODEQL_PLATFORM="linux64" # e.g., linux64, macos, win64
CODEQL_BUNDLE="codeql-${CODEQL_PLATFORM}.zip"
CODEQL_URL="https://github.com/github/codeql-cli-binaries/releases/download/${CODEQL_CLI_VERSION}/${CODEQL_BUNDLE}"
#https://github.com/github/codeql-cli-binaries/releases/download/v2.23.6/codeql-linux64.zip

# maybe move this to known_good.json or a config file later
declare -A BUILD_TARGET_GROUPS=(
    [score_baselibs]="@score_baselibs//score/..."
    [score_communication]="@score_communication//score/mw/com:com"
    [score_persistency]="@score_persistency//src/cpp/src/... @score_persistency//src/rust/..."
    [score_logging]="@score_logging//src/..."
    [score_orchestrator]="@score_orchestrator//src/..."
    [score_test_scenarios]="@score_test_scenarios//..."
    [score_feo]="-- @score_feo//... -@score_feo//:docs -@score_feo//:ide_support -@score_feo//:needs_json"
)



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

# Track if any build group failed
any_failed=0
binary_path="${CODEQL_WORK_DIR}/codeql-cli/codeql/codeql"

if [ -x "${binary_path}" ]; then
    echo "Local CodeQL CLI found at ${binary_path}. Adding to PATH."
    export PATH="$(pwd)/${CODEQL_WORK_DIR}/codeql-cli/codeql:${PATH}"
else    
    echo "CodeQL CLI not found. Downloading..."
    mkdir -p "${CODEQL_WORK_DIR}/codeql-cli"
    curl -L "${CODEQL_URL}" -o "${CODEQL_WORK_DIR}/${CODEQL_BUNDLE}"
    unzip "${CODEQL_WORK_DIR}/${CODEQL_BUNDLE}" -d "${CODEQL_WORK_DIR}/codeql-cli"
    export PATH="$(pwd)/${CODEQL_WORK_DIR}/codeql-cli/codeql:${PATH}"
    echo "CodeQL CLI downloaded and added to PATH."
fi

# Verify CodeQL CLI is now available
if ! command -v codeql &> /dev/null; then
    echo "Error: CodeQL CLI could not be set up. Exiting."
    exit 1
else
    echo "codeql found in path"    
fi  


mkdir -p "${CODEQL_DATABASES_DIR}"
mkdir -p "${CODEQL_SARIF_DIR}"

for group in "${!BUILD_TARGET_GROUPS[@]}"; do
    targets="${BUILD_TARGET_GROUPS[$group]}"
    log_file="${LOG_DIR}/${group}.log"

    db_path="${CODEQL_DATABASES_DIR}/${group}_db"
    sarif_output="${CODEQL_SARIF_DIR}/${group}.sarif"
    current_bazel_output_base="/tmp/codeql_bazel_output_${group}_$(date +%s%N)" # Add timestamp for extra uniqueness


    # 1. Clean Bazel to ensure a fresh build for CodeQL tracing
    echo "Running 'bazel clean --expunge' and 'bazel shutdown'..."
    bazel --output_base="${current_bazel_output_base}" clean --expunge  || { echo "Bazel clean failed for ${group}"; exit 1; }
    bazel --output_base="${current_bazel_output_base}" shutdown  || { echo "Bazel shutdown failed for ${group}"; exit 1; }

    # Log build group banner only to stdout/stderr (not into summary table file)
    echo "--- Building group: ${group} ---"
    start_ts=$(date +%s)
    echo "bazel build --verbose_failures --config "${CONFIG}" ${targets}"
    # GitHub Actions log grouping start
    echo "::group::Bazel build (${group})"
    set +e
    bazel build --verbose_failures --config "${CONFIG}" ${targets} 2>&1 | tee "$log_file"
    build_status=${PIPESTATUS[0]}
    # Track if any build group failed
    if [[ ${build_status} -ne 0 ]]; then
        any_failed=1
    fi
    set -e
    echo "::endgroup::"  # End Bazel build group
    end_ts=$(date +%s)
    duration=$(( end_ts - start_ts ))
    w_count=$(warn_count "$log_file")
    d_count=$(depr_count "$log_file")
    overall_warn_total=$(( overall_warn_total + w_count ))
    overall_depr_total=$(( overall_depr_total + d_count ))

     # Shutdown Bazel again after the traced build
    echo "Running 'bazel shutdown' after CodeQL database creation..."
    bazel shutdown || { echo "Bazel shutdown failed after tracing for ${group}"; exit 1; }

    # 4. Analyze the created database
    echo "Analyzing CodeQL database for ${group}..."
    codeql database analyze "${DB_PATH}" \
      --format=sarifv2.1.0 \
      --output="${SARIF_OUTPUT}" \
      --sarif-category="${group}-${CODEQL_LANGUAGE}" \
      --packs "${CODEQL_QUERY_PACKS}" \
      || { echo "CodeQL analysis failed for ${group}"; exit 1; }

    echo "CodeQL analysis for ${group} complete. Results saved to: ${SARIF_OUTPUT}"
    echo ""


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
echo "| TOTAL |  |  | ${overall_warn_total} | ${overall_depr_total} |  |" >> "${SUMMARY_FILE}"
echo '::group::Build Summary'
echo '=== Build Summary (echo) ==='
cat "${SUMMARY_FILE}" || echo "(Could not read summary file ${SUMMARY_FILE})"
echo '::endgroup::'

# Report to GitHub Actions if any build group failed
if [[ ${any_failed} -eq 1 ]]; then
    echo "::error::One or more build groups failed. See summary above."
    exit 1
fi
