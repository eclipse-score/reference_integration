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
"""Architecture diagram (SVG) of the reference integration for the platform release note.

Rendered by generate_release_note.py together with the skeleton; never edited by hand.
Modules and images come from known_good.json and the repository, components from the
Sphinx-Needs ``comp``/``mod`` needs of a needs.json.
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

import generate_release_note as grn

W = 1280
M = 40
NAVY = "#0b1f3a"
INK = "#1d2b3f"
MUTED = "#5b6b80"
FAINT = "#9aa8bb"
RELEASED = "#0f9d8a"
UNRELEASED = "#e39a2d"
NEW = "#6d4aff"
# Header bar of the S-CORE docs theme (--pst-color-secondary in docs-as-code score.css)
HEADER = "#2d1942"
HEADER_TEXT = "#d8cce6"
HEADER_FAINT = "#a996bf"
FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Menlo, Consolas, monospace"

# images/<dir> -> (operating system, architecture)
IMAGE_LABELS = {
    "linux_x86_64": ("Linux", "x86_64"),
    "qnx_x86_64": ("QNX 8.0", "x86_64"),
    "qnx_aarch64": ("QNX 8.0", "aarch64"),
    "autosd": ("Red Hat AutoSD", "x86_64"),
    "ebclfsa_aarch64": ("EB corbos Linux", "aarch64"),
}


def text_width(s: str, size: float, weight: int = 400) -> float:
    return len(s) * size * (0.64 if weight >= 600 else 0.56)


def fit(s: str, size: float, weight: int, available: float, min_size: float = 11) -> tuple[str, float]:
    while size > min_size and text_width(s, size, weight) > available:
        size -= 0.5
    while len(s) > 4 and text_width(s, size, weight) > available:
        s = s[:-2] + "\u2026"
    return s, size


def wrap(s: str, size: float, weight: int, available: float) -> tuple[list[str], float]:
    """Split a too-long name into two balanced lines instead of shrinking it."""
    if text_width(s, size, weight) <= available or " " not in s:
        label, size = fit(s, size, weight, available)
        return [label], size
    words = s.split()
    cut = min(range(1, len(words)), key=lambda i: max(len(" ".join(words[:i])), len(" ".join(words[i:]))))
    lines = [" ".join(words[:cut]), " ".join(words[cut:])]
    size = min(fit(line, size, weight, available)[1] for line in lines)
    return [fit(line, size, weight, available)[0] for line in lines], size


def text(x, y, s, size=14, weight=400, fill=INK, anchor="start", family=FONT, extra=""):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>'
    )


def pill(x_right, y, label, color, h=18):
    w = 12 + 7 * len(label)
    return f'<rect x="{x_right - w:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="{h / 2}" fill="{color}"/>' + text(
        x_right - w / 2, y + h / 2 + 4, label, 10, 700, "#fff", "middle", extra='letter-spacing="0.8"'
    )


def card_base(x, y, w, h, accent):
    return [
        f'<rect x="{x + 2:.1f}" y="{y + 4:.1f}" width="{w:.1f}" height="{h:.1f}" rx="12" '
        f'fill="{NAVY}" opacity="0.07"/>',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="12" fill="#ffffff" stroke="#d9e1ec"/>',
        f'<rect x="{x:.1f}" y="{y:.1f}" width="6" height="{h:.1f}" rx="3" fill="{accent}"/>',
    ]


def tile(x, y, w, h, entry: grn.Entry, is_new: bool, note: str):
    accent = RELEASED if entry.tag else UNRELEASED
    out = card_base(x, y, w, h, accent)
    lines, size = wrap(entry.name, 16, 700, w - 34 - (52 if is_new else 0))
    for i, line in enumerate(lines):
        out.append(text(x + 20, y + 30 + i * (size + 5), line, size, 700, NAVY))
    version = entry.tag or entry.pin[:7]
    out.append(text(x + 20, y + h - 56, version, 18, 700, INK if entry.tag else accent, family=MONO))
    if note:
        out.append(text(x + 20, y + h - 38, note, 10, 400, FAINT, family=MONO))
    out.append(
        f'<line x1="{x + 20:.1f}" y1="{y + h - 28:.1f}" x2="{x + w - 14:.1f}" y2="{y + h - 28:.1f}" stroke="#e3e9f2"/>'
    )
    repo = entry.repo_url.rstrip("/").rsplit("/", 1)[-1]
    out.append(text(x + 20, y + h - 11, fit(repo, 10, 400, w - 34)[0], 10, 400, FAINT, family=MONO))
    if is_new:
        out.append(pill(x + w - 10, y + 10, "NEW", NEW))
    return "\n".join(out)


def row_card(x, y, w, h, entry: grn.Entry, is_new: bool):
    accent = RELEASED if entry.tag else UNRELEASED
    out = card_base(x, y, w, h, accent)
    version = entry.tag or entry.pin[:7]
    name = re.sub(r"\s*\(.*\)$", "", entry.name)
    label, size = fit(name, 13, 600, w - 40 - text_width(version, 11) - (42 if is_new else 0))
    out.append(text(x + 18, y + h / 2 + 5, label, size, 600))
    if is_new:
        out.append(pill(x + 18 + text_width(label, size, 600) + 41, y + (h - 18) / 2, "NEW", NEW))
    out.append(text(x + w - 12, y + h / 2 + 4, version, 11, 400, MUTED, "end", family=MONO))
    return "\n".join(out)


def section(x, y, w, h, title_lines, subtitle="", stacked=False):
    """stacked: subtitle goes below the title (narrow columns) instead of right-aligned."""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="18" fill="#f4f7fb" stroke="#e3e9f2"/>']
    for i, line in enumerate(title_lines):
        out.append(text(x + 24, y + 30 + i * 18, line.upper(), 12, 700, MUTED, extra='letter-spacing="1.8"'))
    if subtitle and stacked:
        out.append(text(x + 24, y + 30 + len(title_lines) * 18 + 4, subtitle, 12, 400, MUTED))
    elif subtitle:
        out.append(text(x + w - 24, y + 30, subtitle, 12, 400, MUTED, "end"))
    return "".join(out)


CHIP_H, CHIP_GAP = 22, 6


def load_components(source: str, entries: list[grn.Entry]) -> dict[str, list[str]]:
    """Module key -> component titles, from the Sphinx-Needs `comp` and `mod` needs of a needs.json."""
    if source.startswith("http"):
        with urllib.request.urlopen(source, timeout=60) as response:
            data = json.load(response)
    else:
        data = json.loads(Path(source).read_text())
    versions = data["versions"]
    needs = versions.get(data.get("current_version", ""), next(iter(versions.values())))["needs"]
    found: dict[str, dict[str, str]] = {e.key: {} for e in entries}

    def owner(need: dict) -> grn.Entry | None:
        docname = need.get("docname") or ""
        return next((e for e in entries if docname.startswith(f"modules/{e.key}/")), None)

    for need in needs.values():
        if need["type"] == "comp" and (e := owner(need)):
            found[e.key][need["id"]] = need["title"]
        elif need["type"] == "mod":
            # module descriptions can also live in score_platform, so fall back to the title
            e = owner(need) or next((e for e in entries if e.name == need["title"]), None)
            for ref in need.get("includes", []) if e else []:
                if comp := needs.get(ref.split("[")[0]):
                    found[e.key][comp["id"]] = comp["title"]
    return {key: sorted(comps.values(), key=lambda t: (t.lower(), t)) for key, comps in found.items()}


def chip_lines(labels: list[str], available: float) -> list[list[tuple[str, float]]]:
    lines: list[list[tuple[str, float]]] = []
    line: list[tuple[str, float]] = []
    used = 0.0
    for label in labels:
        label = fit(label, 11, 500, available - 16)[0]
        width = text_width(label, 11, 500) + 16
        if line and used + CHIP_GAP + width > available:
            lines.append(line)
            line, used = [], 0.0
        used += (CHIP_GAP if line else 0) + width
        line.append((label, width))
    return lines + [line] if line else lines


def component_layout(entry: grn.Entry, w: float, is_new: bool, note: str, comps: list[str]):
    """Name lines, name size, y offset of the chips and the minimum tile height."""
    lines, size = wrap(entry.name, 16, 700, w - 34 - (52 if is_new else 0))
    chips_y = 30 + (len(lines) - 1) * (size + 5) + 22 + (14 if note else 0) + 14
    n = len(chip_lines(comps, w - 34))
    block = n * CHIP_H + (n - 1) * CHIP_GAP if n else 20
    return lines, size, chips_y, chips_y + block + 16 + 28


def component_tile(x, y, w, h, entry: grn.Entry, is_new: bool, note: str, comps: list[str]):
    accent = RELEASED if entry.tag else UNRELEASED
    out = card_base(x, y, w, h, accent)
    lines, size, chips_y, _ = component_layout(entry, w, is_new, note, comps)
    for i, line in enumerate(lines):
        out.append(text(x + 20, y + 30 + i * (size + 5), line, size, 700, NAVY))
    vy = y + 30 + (len(lines) - 1) * (size + 5) + 22
    out.append(text(x + 20, vy, entry.tag or entry.pin[:7], 13, 700, INK if entry.tag else accent, family=MONO))
    if note:
        out.append(text(x + 20, vy + 14, note, 10, 400, FAINT, family=MONO))
    cy = y + chips_y
    for line in chip_lines(comps, w - 34):
        cx = x + 20
        for label, cw in line:
            out.append(
                f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="{CHIP_H}" rx="{CHIP_H / 2}" '
                f'fill="#eef3fa" stroke="#d6e0ee"/>'
            )
            out.append(text(cx + cw / 2, cy + 15, label, 11, 500, INK, "middle"))
            cx += cw + CHIP_GAP
        cy += CHIP_H + CHIP_GAP
    if not comps:
        out.append(text(x + 20, cy + 14, "no components documented", 11, 400, FAINT, extra='font-style="italic"'))
    out.append(
        f'<line x1="{x + 20:.1f}" y1="{y + h - 28:.1f}" x2="{x + w - 14:.1f}" y2="{y + h - 28:.1f}" stroke="#e3e9f2"/>'
    )
    repo = entry.repo_url.rstrip("/").rsplit("/", 1)[-1]
    out.append(text(x + 20, y + h - 11, fit(repo, 10, 400, w - 34)[0], 10, 400, FAINT, family=MONO))
    if is_new:
        out.append(pill(x + w - 10, y + 10, "NEW", NEW))
    return "\n".join(out)


def component_rows(sw: list[grn.Entry], components: dict[str, list[str]], inner_w: float, gap: float, history, origin):
    """Justified rows of up to 4 column units; modules with many components span 2 or 4 units."""
    rows: list[list[tuple[grn.Entry, int]]] = [[]]
    for e in sw:
        n = len(components.get(e.key, []))
        units = 4 if n > 8 else 2 if n > 3 else 1
        if sum(u for _, u in rows[-1]) + units > 4:
            rows.append([])
        rows[-1].append((e, units))
    layout = []
    for row in rows:
        total = sum(u for _, u in row)
        unit_w = (inner_w - gap * (len(row) - 1)) / total
        tiles, height = [], 0.0
        for e, units in row:
            is_new, previous = history(e)
            note = f"was {previous}" if previous else ("" if is_new else f"unchanged since {origin}")
            w = unit_w * units
            comps = components.get(e.key, [])
            height = max(height, component_layout(e, w, is_new, note, comps)[3])
            tiles.append((e, w, is_new, note, comps))
        layout.append((tiles, height))
    return layout


def render(
    release: str,
    origin: str,
    date: str,
    final: bool,
    groups: dict[str, list[grn.Entry]],
    origin_groups: dict[str, list[grn.Entry]],
    ref: str | None,
    ref_label: str,
    components: dict[str, list[str]] | None,
) -> str:
    old = {grn.KEY_ALIASES.get(e.key, e.key): e for es in origin_groups.values() for e in es}

    def history(e: grn.Entry) -> tuple[bool, str | None]:
        o = old.get(grn.KEY_ALIASES.get(e.key, e.key))
        if o is None:
            return True, None
        return False, (o.tag or o.pin[:7]) if o.pin != e.pin else None

    sw = [e for e in groups["target_sw"] if e.key != grn.PLATFORM_MODULE]
    infra = [e for e in groups["target_sw"] if e.key == grn.PLATFORM_MODULE] + groups["tooling"]

    images = [
        (IMAGE_LABELS.get(directory, (name, directory)), "(Experimental)" in name)
        for name, directory, _, _ in grn.IMAGES
        if grn._exists(ref, f"images/{directory}")
    ]
    new_count = sum(history(e)[0] for e in sw + infra)

    parts: list[str] = []

    # Header with key figures
    short = ".".join(release.removeprefix("v").split(".")[:2])
    parts.append(f'<rect x="0" y="0" width="{W}" height="132" fill="{HEADER}"/>')
    title = f"S-CORE Platform v{short}"
    parts.append(text(M, 54, title, 32, 800, "#ffffff"))
    parts.append(text(M, 86, "Reference integration architecture", 16, 400, HEADER_TEXT))
    state, color = ("FINAL", RELEASED) if final else ("DRAFT", UNRELEASED)
    parts.append(pill(M + text_width(title, 32, 800) + 20 + 12 + 7 * len(state), 30, state, color, 24))
    figures = [
        (str(len(sw)), "software modules"),
        (str(len(infra)), "infrastructure modules"),
        (str(len(images)), "target images"),
    ]
    if components is not None:
        figures.insert(1, (str(sum(map(len, components.values()))), "components"))
    x = W - M
    for value, label in reversed(figures):
        w = max(text_width(label, 11) + 8, 70)
        parts.append(text(x, 62, value, 28, 800, "#ffffff", "end"))
        parts.append(text(x, 82, label, 11, 400, HEADER_TEXT, "end"))
        x -= w + 26
    when = f"released {date}" if final else f"planned {date}"
    parts.append(text(M, 114, f"{release}  \u00b7  {when}  \u00b7  compared to {origin}", 12, 400, HEADER_FAINT))
    top = 156.0
    side_x, side_w = float(M), 300.0
    right_x = side_x + side_w + 20
    right_w = W - M - right_x

    # Body height: the taller of the infrastructure sidebar and the right column (with minimum tile height)
    row_h, row_gap, rows_top = 38, 8, 92
    side_h = rows_top + len(infra) * row_h + (len(infra) - 1) * row_gap + 24
    cols, gap, min_tile_h = 4, 16, 120
    rows = (len(sw) + cols - 1) // cols
    images_h = 128
    right_min = 56 + rows * min_tile_h + (rows - 1) * gap + 24 + 20 + images_h
    if components is not None:
        comp_rows = component_rows(sw, components, right_w - 48, gap, history, origin)
        right_min = 56 + sum(h for _, h in comp_rows) + (len(comp_rows) - 1) * gap + 24 + 20 + images_h
    body_h = max(side_h, right_min)

    # Left sidebar along the full body: platform, infrastructure & tooling
    parts.append(
        section(side_x, top, side_w, body_h, ["Platform, infrastructure", "& tooling"], f"{len(infra)} modules", True)
    )
    for i, e in enumerate(infra):
        y = top + rows_top + i * (row_h + row_gap)
        parts.append(row_card(side_x + 20, y, side_w - 40, row_h, e, history(e)[0]))

    # Integrated software modules, flat grid
    modules_h = body_h - 20 - images_h
    parts.append(section(right_x, top, right_w, modules_h, ["Integrated software modules"], f"{len(sw)} modules"))
    tile_w = (right_w - 48 - gap * (cols - 1)) / cols
    tile_h = (modules_h - 56 - 24 - gap * (rows - 1)) / rows
    if components is not None:
        extra = (body_h - right_min) / len(comp_rows)
        y = top + 56
        for tiles, h in comp_rows:
            x = right_x + 24
            for e, w, is_new, note, comps in tiles:
                parts.append(component_tile(x, y, w, h + extra, e, is_new, note, comps))
                x += w + gap
            y += h + extra + gap
        sw = []
    for i, e in enumerate(sw):
        is_new, previous = history(e)
        note = f"was {previous}" if previous else ("" if is_new else f"unchanged since {origin}")
        x = right_x + 24 + (i % cols) * (tile_w + gap)
        y = top + 56 + (i // cols) * (tile_h + gap)
        parts.append(tile(x, y, tile_w, tile_h, e, is_new, note))

    # Target images below the modules
    y = top + body_h - images_h
    parts.append(section(right_x, y, right_w, images_h, ["Target images"], "dashed: experimental"))
    iw = (right_w - 48 - 14 * (len(images) - 1)) / max(len(images), 1)
    for i, ((os_name, arch), experimental) in enumerate(images):
        x = right_x + 24 + i * (iw + 14)
        dash = ' stroke-dasharray="5 4"' if experimental else ""
        parts.append(
            f'<rect x="{x:.1f}" y="{y + 50:.1f}" width="{iw:.1f}" height="54" rx="10" fill="#ffffff" '
            f'stroke="#9fb1c9"{dash}/>'
        )
        label, size = fit(os_name, 14, 700, iw - 16)
        parts.append(text(x + iw / 2, y + 73, label, size, 700, NAVY, "middle"))
        parts.append(text(x + iw / 2, y + 92, arch, 11, 400, MUTED, "middle", family=MONO))
    y = top + body_h + 20

    # Legend
    x = float(M)
    for color, label in ((RELEASED, "released (tag)"), (UNRELEASED, "unreleased (commit pin)")):
        parts.append(f'<rect x="{x:.1f}" y="{y + 2:.1f}" width="14" height="14" rx="3" fill="{color}"/>')
        parts.append(text(x + 22, y + 14, label, 12, 400, MUTED))
        x += 40 + text_width(label, 12)
    parts.append(pill(x + 40, y, "NEW", NEW))
    parts.append(text(x + 48, y + 14, f"new since {origin}  ({new_count})", 12, 400, MUTED))
    x += 48 + text_width(f"new since {origin}  ({new_count})", 12) + 24
    parts.append(text(x, y + 14, f"was \u2026 = version in {origin}", 12, 400, MUTED, family=FONT))
    parts.append(
        text(W - M, y + 14, f"generated from known_good.json @ {ref_label}", 11, 400, FAINT, "end", family=MONO)
    )
    y += 36

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {y:.0f}" width="{W}" height="{y:.0f}" '
        f'role="img" aria-label="S-CORE v{short} reference integration architecture">'
        f'<rect width="{W}" height="{y:.0f}" fill="#ffffff"/>' + "\n".join(parts) + "</svg>"
    )
