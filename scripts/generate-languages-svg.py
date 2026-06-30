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
    W = 760
    PAD = 28
    inner = W - PAD * 2
    head_h = 78
    row_h = 30
    rows = (len(sorted_langs) + 1) // 2
    height = head_h + rows * row_h + PAD
    col_w = inner / 2
    font = ('font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", '
            "Helvetica, Arial, sans-serif;")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="Most used languages">',
        "<defs>",
        '  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">',
        '    <stop offset="0" stop-color="#70A5FD"/>',
        '    <stop offset="1" stop-color="#B388FF"/>',
        "  </linearGradient>",
        "</defs>",
        "<style>",
        f"  text {{ {font} fill: #8b949e; }}",
        "  .t { font-size: 20px; fill: #70A5FD; font-weight: 700; }",
        "  .sub { font-size: 12px; fill: #6e7681; }",
        "  .l { font-size: 14px; }",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="14" '
        'fill="#0d1117" stroke="#30363d"/>',
        f'<rect x="{PAD}" y="{PAD}" width="64" height="5" rx="2.5" fill="url(#g)"/>',
        f'<text x="{PAD}" y="{PAD + 30}" class="t">Most Used Languages</text>',
        f'<text x="{PAD}" y="{PAD + 48}" class="sub">across all repos '
        '(public + private, excl. forks)</text>',
        f'<g transform="translate({PAD}, {head_h - 14})">',
    ]

    x = 0
    last_name = sorted_langs[-1][0] if sorted_langs else None
    for name, size in sorted_langs:
        width = max((size / total) * inner, 4)
        color = COLORS.get(name, "#8b8b8b")
        if x == 0:
            radius = "7 0 0 7"
        elif name == last_name:
            radius = "0 7 7 0"
        else:
            radius = "0"
        parts.append(
            f'  <rect x="{x:.1f}" y="0" width="{width:.1f}" height="14" '
            f'rx="{radius}" fill="{color}"/>'
        )
        x += width

    col, row = 0, 0
    for name, size in sorted_langs:
        pct = (size / total) * 100
        color = COLORS.get(name, "#8b8b8b")
        lx, ly = col * col_w, 40 + row * row_h
        parts.append(f'  <circle cx="{lx + 6}" cy="{ly}" r="6" fill="{color}"/>')
        parts.append(
            f'  <text x="{lx + 20}" y="{ly + 5}" class="l">{name} '
            f'<tspan fill="#6e7681">{pct:.1f}%</tspan></text>'
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
