import argparse
import os
import sys
from pathlib import Path


def _resolve_path_from_bazel(path: Path) -> Path:
    """Resolve path relative to user's working directory when running via bazel run.

    Bazel sets BUILD_WORKING_DIRECTORY to the directory where bazel was invoked.
    """
    if not path.is_absolute():
        # When running via 'bazel run', resolve relative paths against the user's cwd
        build_working_dir = os.environ.get("BUILD_WORKING_DIRECTORY")
        if build_working_dir:
            return (Path(build_working_dir) / path).resolve()
    return path.resolve()


def _find_repo_root() -> Path:
    """Walk up from this file to find the repo root (contains known_good.json)."""
    candidate = Path(__file__).resolve()
    for parent in candidate.parents:
        if (parent / "known_good.json").exists():
            return parent
    return Path.cwd()


def _cmd_html_report(args: argparse.Namespace) -> int:
    from scripts.tooling.lib.html_report import write_report
    from scripts.tooling.lib.known_good import load_known_good

    known_good_path = Path(args.known_good) / "known_good.json"
    try:
        known_good = load_known_good(known_good_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = _resolve_path_from_bazel(Path(args.output))
    write_report(known_good, output)
    print(f"Report written to {output}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="tooling")
    subparsers = parser.add_subparsers(dest="group", metavar="GROUP")
    subparsers.required = True

    # --- misc group ---
    misc_parser = subparsers.add_parser("misc", help="Miscellaneous utilities")
    misc_sub = misc_parser.add_subparsers(dest="command", metavar="COMMAND")
    misc_sub.required = True

    html_parser = misc_sub.add_parser("html_report", help="Generate an HTML status report from known_good.json")
    html_parser.add_argument(
        "--known_good",
        metavar="PATH",
        default=str(_find_repo_root()),
        help="Directory containing known_good.json (default: repo root)",
    )
    html_parser.add_argument(
        "--output",
        metavar="FILE",
        default="report.html",
        help="Output HTML file path (default: report.html)",
    )

    args = parser.parse_args()

    if args.group == "misc" and args.command == "html_report":
        sys.exit(_cmd_html_report(args))


if __name__ == "__main__":
    main()
