#!/usr/bin/env python3
"""Generate github-languages.svg from one or two GitHub GraphQL paginated JSON dumps.

Inputs (env vars):
    PAGE1_JSON  Path to first page JSON (default: /tmp/p1.json) -- required to exist.
    PAGE2_JSON  Path to second page JSON (default: /tmp/p2.json) -- optional; skipped if missing.

Output:
    github-languages.svg in the current working directory.
"""
import json
import os
import sys

EXCLUDE = {
    "HTML", "CSS", "SCSS", "Shell", "Makefile", "Roff", "VCL", "Smarty",
    "Starlark", "FreeMarker", "Gherkin", "PowerShell", "Dockerfile",
    "AppleScript", "Hack", "Objective-C++",
}

COLORS = {
    "Swift": "#F05138", "TypeScript": "#3178C6", "JavaScript": "#F1E05A",
    "C++": "#F34B7D", "PHP": "#4F5D95", "Java": "#B07219",
    "Objective-C": "#438EFF", "Elixir": "#6E4A7E", "Ruby": "#701516",
    "Lua": "#000080", "Rust": "#DEA584", "Python": "#3572A5",
    "Go": "#00ADD8", "Kotlin": "#A97BFF", "C": "#555555",
    "Vue": "#41B883",
}

DEFAULT_PAGE1 = "/tmp/p1.json"
DEFAULT_PAGE2 = "/tmp/p2.json"


def collect_languages(paths):
    langs = {}
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for node in data["data"]["viewer"]["repositories"]["nodes"]:
            for edge in node["languages"]["edges"]:
                name = edge["node"]["name"]
                if name in EXCLUDE:
                    continue
                langs[name] = langs.get(name, 0) + edge["size"]
    return langs


def render_svg(sorted_langs, total):
    bar_w = 400
    row_h = 22
    rows = (len(sorted_langs) + 1) // 2
    height = 48 + 16 + rows * row_h + 8

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{height}">',
        "<style>",
        '  text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; fill: #8b949e; }',
        "  .t { font-size: 14px; fill: #58a6ff; font-weight: 600; }",
        "  .l { font-size: 12px; }",
        "</style>",
        '<text x="20" y="28" class="t">Most Used Languages</text>',
        '<text x="20" y="42" style="font-size:10px;fill:#666">across all repos (public + private, excl. forks)</text>',
        '<g transform="translate(40, 50)">',
    ]

    x = 0
    last_name = sorted_langs[-1][0] if sorted_langs else None
    for name, size in sorted_langs:
        width = max((size / total) * bar_w, 3)
        color = COLORS.get(name, "#8b8b8b")
        if x == 0:
            radius = "4 0 0 4"
        elif name == last_name:
            radius = "0 4 4 0"
        else:
            radius = "0"
        parts.append(
            f'  <rect x="{x:.1f}" y="0" width="{width:.1f}" height="8" rx="{radius}" fill="{color}"/>'
        )
        x += width

    col, row = 0, 0
    for name, size in sorted_langs:
        pct = (size / total) * 100
        color = COLORS.get(name, "#8b8b8b")
        lx, ly = col * 200, 22 + row * row_h
        parts.append(f'  <circle cx="{lx}" cy="{ly}" r="5" fill="{color}"/>')
        parts.append(
            f'  <text x="{lx + 12}" y="{ly + 4}" class="l">{name} <tspan fill="#666">{pct:.1f}%</tspan></text>'
        )
        col += 1
        if col >= 2:
            col, row = 0, row + 1

    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    page1 = os.environ.get("PAGE1_JSON", DEFAULT_PAGE1)
    page2 = os.environ.get("PAGE2_JSON", DEFAULT_PAGE2)

    if not os.path.exists(page1):
        print(f"error: PAGE1_JSON not found: {page1}", file=sys.stderr)
        sys.exit(1)

    langs = collect_languages([page1, page2])
    total = sum(langs.values()) or 1
    sorted_langs = sorted(langs.items(), key=lambda x: -x[1])[:8]

    svg = render_svg(sorted_langs, total)
    with open("github-languages.svg", "w") as f:
        f.write(svg)

    for name, size in sorted_langs:
        print(f"  {name}: {(size / total) * 100:.1f}%")


if __name__ == "__main__":
    main()
