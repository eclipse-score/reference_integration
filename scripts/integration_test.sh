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
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up one level to get the repository root since this script is in scripts/ directory
repo_root="$(cd "${script_dir}/.." && pwd)"

# Set default known_good.json if it exists
if [[ -z "${KNOWN_GOOD_FILE}" ]] && [[ -f "known_good.json" ]]; then
    KNOWN_GOOD_FILE="known_good.json"
fi

# maybe move this to known_good.json or a config file later
declare -A BUILD_TARGET_GROUPS=(
    [score_baselibs]="@score_baselibs//score/..."
    [score_communication]="@score_communication//score/mw/com:com"
    [score_persistency]="@score_persistency//src/cpp/src/... @score_persistency//src/rust/..."
    [score_kyron]="@score_kyron//src/..."
    [score_orchestrator]="@score_orchestrator//src/..."
    [score_test_scenarios]="@score_test_scenarios//test_scenarios_rust:test_scenarios_rust @score_test_scenarios//test_scenarios_cpp:test_scenarios_cpp"
    [score_feo]="-- @score_feo//... -@score_feo//:docs -@score_feo//:ide_support -@score_feo//:needs_json"
    [score_logging]="@score_logging//score/...  \
        --@score_baselibs//score/memory/shared/flags:use_typedshmd=False \
        --@score_baselibs//score/json:base_library=nlohmann \
        --@score_logging//score/datarouter/build_configuration_flags:persistent_logging=False \
        --@score_logging//score/datarouter/build_configuration_flags:persistent_config_feature_enabled=False \
        --@score_logging//score/datarouter/build_configuration_flags:enable_nonverbose_dlt=False \
        --@score_logging//score/datarouter/build_configuration_flags:enable_dynamic_configuration_in_datarouter=False \
        --@score_logging//score/datarouter/build_configuration_flags:dlt_file_transfer_feature=False \
        --@score_logging//score/datarouter/build_configuration_flags:use_local_vlan=True "
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
    
    # Use the Python script to extract module info
    local result
    result=$(python3 "${repo_root}/tools/get_module_info.py" "${known_good_file}" "${module_name}" "hash" 2>&1)
    if [[ $? -eq 0 ]] && [[ -n "${result}" ]] && [[ "${result}" != "N/A" ]]; then
        echo "${result}"
    else
        echo "N/A"
    fi
}

# Function to extract repo URL from known_good.json
get_module_repo() {
    local module_name=$1
    local known_good_file=$2
    
    if [[ -z "${known_good_file}" ]] || [[ ! -f "${known_good_file}" ]]; then
        echo "N/A"
        return
    fi
    
    # Use the Python script to extract module repo
    local result
    result=$(python3 "${repo_root}/tools/get_module_info.py" "${known_good_file}" "${module_name}" "repo" 2>&1)
    if [[ $? -eq 0 ]] && [[ -n "${result}" ]] && [[ "${result}" != "N/A" ]]; then
        echo "${result}"
    else
        echo "N/A"
    fi
}

# Function to extract version from known_good.json
get_module_version() {
    local module_name=$1
    local known_good_file=$2
    
    if [[ -z "${known_good_file}" ]] || [[ ! -f "${known_good_file}" ]]; then
        echo "N/A"
        return
    fi
    
    # Use the Python script to extract module version
    local result
    result=$(python3 "${repo_root}/tools/get_module_info.py" "${known_good_file}" "${module_name}" "version" 2>&1)
    if [[ $? -eq 0 ]] && [[ -n "${result}" ]] && [[ "${result}" != "N/A" ]]; then
        echo "${result}"
    else
        echo "N/A"
    fi
}

get_module_version_gh() {
    local module_name=$1
    local known_good_file=$2
    local repo_url=$3
    local commit_hash=$4
    
    if [[ -z "${known_good_file}" ]] || [[ ! -f "${known_good_file}" ]]; then
        echo "::warning::get_module_version_gh: known_good_file not found or empty" >&2
        echo "N/A"
        return
    fi
    
    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        echo "::warning::gh CLI not found. Install it to resolve commit hashes to tags." >&2
        echo "N/A"
        return
    fi
    
    echo "::debug::get_module_version_gh: module=${module_name}, repo=${repo_url}, hash=${commit_hash}" >&2
    
    # Extract owner/repo from GitHub URL
    if [[ "${repo_url}" =~ github\.com[/:]([^/]+)/([^/.]+)(\.git)?$ ]]; then
        local owner="${BASH_REMATCH[1]}"
        local repo="${BASH_REMATCH[2]}"
        
        echo "::debug::Querying GitHub API: repos/${owner}/${repo}/tags for commit ${commit_hash}" >&2
        
        # Query GitHub API for tags and find matching commit
        local tag_name
        tag_name=$(gh api "repos/${owner}/${repo}/tags" --jq ".[] | select(.commit.sha == \"${commit_hash}\") | .name" 2>/dev/null | head -n1)
        
        if [[ -n "${tag_name}" ]]; then
            echo "::debug::Found tag: ${tag_name}" >&2
            echo "${tag_name}"
        else
            echo "::debug::No tag found for commit ${commit_hash}" >&2
            echo "N/A"
        fi
    else
        echo "::warning::Invalid repo URL format: ${repo_url}" >&2
        echo "N/A"
    fi
}

# Helper function to truncate hash
truncate_hash() {
    local hash=$1
    if [[ ${#hash} -gt 8 ]]; then
        echo "${hash:0:8}"
    else
        echo "${hash}"
    fi
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

for group in "${!BUILD_TARGET_GROUPS[@]}"; do
    targets="${BUILD_TARGET_GROUPS[$group]}"
    log_file="${LOG_DIR}/${group}.log"

    # Log build group banner only to stdout/stderr (not into summary table file)
    echo "--- Building group: ${group} ---"
    start_ts=$(date +%s)
    echo "bazel build --verbose_failures --config "${CONFIG}" ${targets}"
    # GitHub Actions log grouping start
    echo "::group::Bazel build (${group})"
    set +e
    # bazel build --verbose_failures --config "${CONFIG}" ${targets} 2>&1 | tee "$log_file" # ToDo: enable this line before PR
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
    # Append as a markdown table row (duration without trailing 's')
    if [[ ${build_status} -eq 0 ]]; then
        status_symbol="✅"
    else
        status_symbol="❌(${build_status})"
    fi
    
    # Get commit hash/version for this group (group name is the module name)
    commit_hash=$(get_commit_hash "${group}" "${KNOWN_GOOD_FILE}")
    commit_hash_old=$(get_commit_hash "${group}" "known_good.json")
    version=$(get_module_version "${group}" "${KNOWN_GOOD_FILE}")
    repo=$(get_module_repo "${group}" "${KNOWN_GOOD_FILE}")
    
    # Debug output
    echo "::debug::Module=${group}, version=${version}, hash=${commit_hash}, hash_old=${commit_hash_old}, repo=${repo}" >&2
    
    # Determine what to display and link to
    # Step 1: Determine old version/hash identifier
    old_identifier="N/A"
    old_link=""
    if [[ "${commit_hash_old}" != "N/A" ]]; then
        echo "::debug::Step 1: Getting old version for ${group}" >&2
        version_old=$(get_module_version "${group}" "known_good.json")
        echo "::debug::version_old from JSON: ${version_old}" >&2
        if [[ "${version_old}" == "N/A" ]]; then
            # Try to get version from GitHub API
            echo "::debug::Trying to resolve version_old from GitHub for ${group}" >&2
            version_old=$(get_module_version_gh "${group}" "known_good.json" "${repo}" "${commit_hash_old}")
            echo "::debug::version_old from GitHub: ${version_old}" >&2
        fi
        
        # Prefer version over hash
        if [[ "${version_old}" != "N/A" ]]; then
            old_identifier="${version_old}"
            if [[ "${repo}" != "N/A" ]]; then
                old_link="${repo}/releases/tag/${version_old}"
            fi
        else
            old_identifier=$(truncate_hash "${commit_hash_old}")
            if [[ "${repo}" != "N/A" ]]; then
                old_link="${repo}/tree/${commit_hash_old}"
            fi
        fi
        echo "::debug::old_identifier=${old_identifier}" >&2
    fi
    
    # Step 2: Determine if hash changed
    hash_changed=0
    if [[ "${commit_hash_old}" != "N/A" ]] && [[ "${commit_hash}" != "N/A" ]] && [[ "${commit_hash}" != "${commit_hash_old}" ]]; then
        hash_changed=1
    fi
    echo "::debug::hash_changed=${hash_changed}" >&2
    
    # Step 3: Determine new version/hash identifier (only if hash changed)
    new_identifier="N/A"
    new_link=""
    if [[ ${hash_changed} -eq 1 ]] && [[ "${commit_hash}" != "N/A" ]]; then
        echo "::debug::Step 3: Hash changed, getting new version for ${group}" >&2
        # Try to get version from known_good file first, then GitHub API
        if [[ "${version}" == "N/A" ]]; then
            echo "::debug::Trying to resolve new version from GitHub for ${group}" >&2
            version=$(get_module_version_gh "${group}" "${KNOWN_GOOD_FILE}" "${repo}" "${commit_hash}")
            echo "::debug::new version from GitHub: ${version}" >&2
        fi
        
        # Prefer version over hash
        if [[ "${version}" != "N/A" ]]; then
            new_identifier="${version}"
            if [[ "${repo}" != "N/A" ]]; then
                new_link="${repo}/releases/tag/${version}"
            fi
        else
            new_identifier=$(truncate_hash "${commit_hash}")
            if [[ "${repo}" != "N/A" ]]; then
                new_link="${repo}/tree/${commit_hash}"
            fi
        fi
        echo "::debug::new_identifier=${new_identifier}" >&2
    fi
    
    # Step 4: Format output based on whether hash changed
    echo "::debug::Formatting output: hash_changed=${hash_changed}, old=${old_identifier}, new=${new_identifier}" >&2
    if [[ ${hash_changed} -eq 1 ]]; then
        # Hash changed - show old -> new
        if [[ "${repo}" != "N/A" ]] && [[ -n "${old_link}" ]] && [[ -n "${new_link}" ]]; then
            commit_version_cell="[${old_identifier}](${old_link}) → [${new_identifier}](${new_link}) ([diff](${repo}/compare/${commit_hash_old}...${commit_hash}))"
        else
            commit_version_cell="${old_identifier} → ${new_identifier}"
        fi
    elif [[ "${old_identifier}" != "N/A" ]]; then
        # Hash not changed - show only old
        if [[ "${repo}" != "N/A" ]] && [[ -n "${old_link}" ]]; then
            commit_version_cell="[${old_identifier}](${old_link})"
        else
            commit_version_cell="${old_identifier}"
        fi
    elif [[ "${new_identifier}" != "N/A" ]]; then
        # No old available - show new
        if [[ "${repo}" != "N/A" ]] && [[ -n "${new_link}" ]]; then
            commit_version_cell="[${new_identifier}](${new_link})"
        else
            commit_version_cell="${new_identifier}"
        fi
    else
        # Nothing available
        commit_version_cell="N/A"
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
