#!/usr/bin/env python3
# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
"""Render the Overall Status progress charts from ``overall_status_data.json``.

Every release is a stacked bar whose colour slots map to the contributing
modules, so the per-module split is comparable across releases. Colours come
from the shared ``module_colors`` map, which makes a module recognisable by the
same colour in every chart. Within a bar the slots are ordered by size,
largest at the bottom.
"""

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "docs" / "s_core_v_1" / "roadmap" / "overall_status_data.json"
ASSET_DIR = REPO_ROOT / "docs" / "_assets"

WIDTH = 880
PLOT_LEFT = 90
PLOT_RIGHT = 850
PLOT_TOP = 56
PLOT_BOTTOM = 300
BAR_WIDTH = 82
LABEL_Y = 322
LEGEND_TOP = 348
LEGEND_ROW_H = 20
LEGEND_COLS = 3
# segments thinner than this get no inline label, it would not fit
MIN_LABEL_PX = 12


def fmt(value: int) -> str:
    return f"{value:,}"


def bar_x(index: int, count: int) -> float:
    span = (PLOT_RIGHT - PLOT_LEFT) / count
    return PLOT_LEFT + span * index + (span - BAR_WIDTH) / 2


def text(x: float, y: float, content: str, **attrs: str) -> str:
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'  <text x="{x}" y="{y}" text-anchor="middle"{extra}>{content}</text>'


def render(chart: dict, module_colors: dict) -> str:
    releases = chart["releases"]
    axis_max = int(chart["axis_max"])
    axis_step = int(chart["axis_step"])
    scale = (PLOT_BOTTOM - PLOT_TOP) / axis_max
    title = escape(chart["title"])

    contributing = [m for m in module_colors if any(r["modules"].get(m, 0) > 0 for r in releases)]
    legend_rows = -(-len(contributing) // LEGEND_COLS)
    height = LEGEND_TOP + legend_rows * LEGEND_ROW_H + 10

    o = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}"'
            ' font-family="Arial, sans-serif" font-size="13" role="img">'
        ),
        f"  <title>{title}</title>",
        text(WIDTH // 2, 26, title, font_size="15", font_weight="bold"),
        f'  <line x1="{PLOT_LEFT}" y1="{PLOT_TOP}" x2="{PLOT_LEFT}" y2="{PLOT_BOTTOM}" stroke="#333"/>',
        f'  <line x1="{PLOT_LEFT}" y1="{PLOT_BOTTOM}" x2="{PLOT_RIGHT}" y2="{PLOT_BOTTOM}" stroke="#333"/>',
        '  <g stroke="#ddd">',
    ]
    for tick in range(axis_step, axis_max + 1, axis_step):
        y = round(PLOT_BOTTOM - tick * scale, 1)
        o.append(f'    <line x1="{PLOT_LEFT}" y1="{y}" x2="{PLOT_RIGHT}" y2="{y}"/>')
    o.append("  </g>")

    o.append('  <g fill="#555" text-anchor="end" font-size="11">')
    for tick in range(0, axis_max + 1, axis_step):
        y = round(PLOT_BOTTOM - tick * scale + 4, 1)
        o.append(f'    <text x="{PLOT_LEFT - 8}" y="{y}">{fmt(tick)}</text>')
    o.append("  </g>")

    for i, release in enumerate(releases):
        mods = release["modules"]
        total = sum(mods.values())
        x = round(bar_x(i, len(releases)), 1)
        cx = round(x + BAR_WIDTH / 2, 1)
        o.append(f"  <!-- {release['name']}: total {total} -->")
        cursor = float(PLOT_BOTTOM)
        # largest slot at the bottom; colour stays tied to the module either way
        order = sorted(
            (m for m in contributing if mods.get(m, 0) > 0),
            key=lambda m: (-mods[m], contributing.index(m)),
        )
        for module in order:
            value = mods[module]
            h = value * scale
            y = cursor - h
            o.append(
                f'  <rect x="{x}" y="{round(y, 1)}" width="{BAR_WIDTH}"'
                f' height="{round(h, 1)}" fill="{module_colors[module]}"'
                ' stroke="#fff" stroke-width="0.5">'
                f"<title>{escape(module)}: {fmt(value)}</title></rect>"
            )
            if h >= MIN_LABEL_PX:
                o.append(
                    text(
                        cx,
                        round(y + h / 2 + 3.5, 1),
                        fmt(value),
                        font_size="9",
                        fill="#fff",
                        font_weight="bold",
                    )
                )
            cursor = y
        o.append(text(cx, round(cursor - 6, 1), fmt(total), font_size="11", font_weight="bold"))
        o.append(text(cx, LABEL_Y, escape(release["name"]), font_weight="bold", font_size="12"))

    col_w = (PLOT_RIGHT - PLOT_LEFT) / LEGEND_COLS
    o.append('  <g font-size="12">')
    for i, module in enumerate(contributing):
        lx = round(PLOT_LEFT + (i % LEGEND_COLS) * col_w, 1)
        ly = LEGEND_TOP + (i // LEGEND_COLS) * LEGEND_ROW_H
        o.append(f'    <rect x="{lx}" y="{ly}" width="13" height="13" fill="{module_colors[module]}"/>')
        o.append(f'    <text x="{lx + 19}" y="{ly + 11}">{escape(module)}</text>')
    o.append("  </g>")
    o.append("</svg>")
    return "\n".join(o) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_FILE)
    parser.add_argument("--out-dir", type=Path, default=ASSET_DIR)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when a chart is out of date",
    )
    args = parser.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    stale = []
    for chart in data["charts"].values():
        svg = render(chart, data["module_colors"])
        target = args.out_dir / chart["file"]
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != svg:
                stale.append(target)
            continue
        target.write_text(svg, encoding="utf-8")
        print(f"wrote {target.relative_to(REPO_ROOT)}")

    if stale:
        names = ", ".join(str(p.relative_to(REPO_ROOT)) for p in stale)
        raise SystemExit(f"out of date: {names}\nrun scripts/overall_status/generate_progress_charts.py")


if __name__ == "__main__":
    main()
