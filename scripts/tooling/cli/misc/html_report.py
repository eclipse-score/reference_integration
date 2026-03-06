import argparse
import os
import sys
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "assets"


def _find_repo_root() -> Path:
    candidate = Path(__file__).resolve()
    for parent in candidate.parents:
        if (parent / "known_good.json").exists():
            return parent
    return Path.cwd()


def _resolve_path_from_bazel(path: Path) -> Path:
    if not path.is_absolute():
        build_working_dir = os.environ.get("BUILD_WORKING_DIRECTORY")
        if build_working_dir:
            return (Path(build_working_dir) / path).resolve()
    return path.resolve()


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("html_report", help="Generate an HTML status report from known_good.json")
    parser.add_argument(
        "--known_good",
        metavar="PATH",
        default=str(_find_repo_root()),
        help="Directory containing known_good.json (default: repo root)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default="report.html",
        help="Output HTML file path (default: report.html)",
    )
    parser.set_defaults(func=_run)


def _run(args: argparse.Namespace) -> int:
    from scripts.tooling.lib.html_report import write_report
    from scripts.tooling.lib.known_good import load_known_good

    known_good_path = Path(args.known_good) / "known_good.json"
    try:
        known_good = load_known_good(known_good_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    token = os.environ.get("GITHUB_TOKEN")
    output = _resolve_path_from_bazel(Path(args.output))
    write_report(known_good, output, TEMPLATE_DIR, token=token)
    if token:
        print(f"Report written to {output} (current hashes fetched from GitHub)")
    else:
        print(f"Report written to {output} (set GITHUB_TOKEN to embed current hashes)")
    return 0
