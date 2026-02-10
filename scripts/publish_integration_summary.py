#!/usr/bin/env python3
import argparse
import os
import sys


def format_status(result: str) -> str:
    status_map = {
        "success": "✅ **SUCCESS**",
        "failure": "❌ **FAILURE**",
        "cancelled": "⚪ **CANCELLED**",
        "skipped": "⚪ **SKIPPED**",
        "": "⚪ **UNKNOWN**",
    }
    return status_map.get(result, "⚪ **UNKNOWN**")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish integration test summary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 scripts/publish_integration_summary.py \\\n"
            "    --integration-result success \\\n"
            "    --docs-result failure \\\n"
            "    --logs-dir _logs/integration_test_logs\n"
            "  python3 scripts/publish_integration_summary.py \\\n"
            "    --integration-result success \\\n"
            "    --docs-result success"
        ),
    )
    parser.add_argument(
        "--integration-result",
        default="",
        choices=["success", "failure", "cancelled", "skipped"],
        help="Integration test result.",
    )
    parser.add_argument(
        "--docs-result",
        default="",
        choices=["success", "failure", "cancelled", "skipped"],
        help="Documentation result.",
    )
    parser.add_argument(
        "--logs-dir",
        default="_logs",
        help="Directory containing build_summary.md files.",
    )
    args = parser.parse_args()

    integration_result = args.integration_result
    docs_result = args.docs_result
    logs_dir = args.logs_dir

    out = sys.stdout

    out.write("## Overall Status\n\n")

    out.write(f"- Integration Test: {format_status(integration_result)}\n")
    out.write(f"- Documentation Generation: {format_status(docs_result)}\n")

    out.write("\n---\n\n")
    out.write("## Integration Test Summary\n\n")

    summaries = []
    if os.path.isdir(logs_dir):
        for root, _, files in os.walk(logs_dir):
            for name in files:
                if name.startswith("build_summary-") and name.endswith(".md"):
                    summaries.append(os.path.join(root, name))

    if not summaries:
        out.write(f"No build_summary-*.md files found in '{logs_dir}'.\n\n")
        return 0
    for summary_file in sorted(summaries):
        filename = os.path.basename(summary_file)
        config_name = filename[len("build_summary-") : -len(".md")]
        out.write(f"### Configuration: {config_name}\n\n")
        with open(summary_file, "r", encoding="utf-8", errors="replace") as handle:
            out.write(handle.read())
        out.write("\n\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
