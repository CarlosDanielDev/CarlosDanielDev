#!/usr/bin/env python3
"""Generate github-featured.svg: a curated "Featured Projects" card grid.

Curated repo list (hand-ranked), live stars/description/language fetched via
the `gh` CLI. Self-hosted, themed to match the other profile cards (760px).

Usage:
    GH_TOKEN=... python scripts/generate-featured-svg.py
    FEATURED_JSON=repos.json python scripts/generate-featured-svg.py
    python scripts/generate-featured-svg.py --selftest

Output: github-featured.svg in the current working directory.
"""
import json
import os
import subprocess
import sys

OWNER = os.environ.get("STATS_USER", "CarlosDanielDev")

# hand-ranked, curated. order = display order.
FEATURED = [
    "maestro",
    "copyrfid",
    "saopaulo-night",
    "discipline.nvim",
    "lucid-engine",
    "tsumiki",
]

LANG_COLORS = {
    "Swift": "#F05138", "TypeScript": "#3178C6", "JavaScript": "#F1E05A",
    "C++": "#F34B7D", "PHP": "#4F5D95", "Java": "#B07219", "Rust": "#DEA584",
    "Python": "#3572A5", "Go": "#00ADD8", "Lua": "#000080", "C": "#555555",
    "Ruby": "#701516", "Shell": "#89E051", "Objective-C": "#438EFF",
}


def fetch():
    repos = []
    for name in FEATURED:
        out = subprocess.run(
            ["gh", "api", f"repos/{OWNER}/{name}",
             "--jq", "{name:.name, desc:.description, "
                     "lang:.language, stars:.stargazers_count, "
                     "forks:.forks_count, url:.html_url}"],
            capture_output=True, text=True, check=True,
        )
        repos.append(json.loads(out.stdout))
    return repos


# --- rendering ---------------------------------------------------------------

W = 760
PAD = 28
ACCENT = "#70A5FD"
MUTED = "#8b949e"
DIM = "#6e7681"
BG = "#0d1117"
TILE_BG = "#161b22"
BORDER = "#30363d"
FONT = ('font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", '
        "Helvetica, Arial, sans-serif;")


def _esc(t):
    return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _wrap(text, width, max_lines=2):
    words = (text or "").split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and (len(" ".join(lines)) < len(text or "")):
        lines[-1] = lines[-1][:width - 1].rstrip() + "…"
    return lines[:max_lines]


def render_svg(repos):
    cols = 2
    gap = 16
    inner = W - PAD * 2
    col_w = (inner - gap) / cols
    tile_h = 96
    rows = (len(repos) + cols - 1) // cols
    head_h = 58
    height = head_h + rows * tile_h + (rows - 1) * gap + PAD

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="Featured projects">',
        "<defs>",
        '  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">',
        '    <stop offset="0" stop-color="#70A5FD"/>',
        '    <stop offset="1" stop-color="#B388FF"/>',
        "  </linearGradient>",
        "</defs>",
        "<style>",
        f"  text {{ {FONT} }}",
        f"  .t {{ font-size: 20px; fill: {ACCENT}; font-weight: 700; }}",
        f"  .sub {{ font-size: 12px; fill: {DIM}; }}",
        f"  .repo {{ font-size: 15px; fill: {ACCENT}; font-weight: 700; }}",
        f"  .desc {{ font-size: 12px; fill: {MUTED}; }}",
        f"  .meta {{ font-size: 12px; fill: {DIM}; }}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="14" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<rect x="{PAD}" y="{PAD}" width="64" height="5" rx="2.5" fill="url(#g)"/>',
        f'<text x="{PAD}" y="{PAD + 28}" class="t">Featured Projects</text>',
        f'<text x="{W - PAD}" y="{PAD + 28}" class="sub" text-anchor="end">'
        f'what I’m building on GitHub</text>',
    ]

    for i, r in enumerate(repos):
        c = i % cols
        row = i // cols
        x = PAD + c * (col_w + gap)
        y = head_h + row * (tile_h + gap)
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{col_w:.1f}" height="{tile_h}" '
            f'rx="10" fill="{TILE_BG}" stroke="{BORDER}"/>'
        )
        tx = x + 16
        parts.append(f'<text x="{tx:.1f}" y="{y + 26:.1f}" class="repo">'
                     f'{_esc(r["name"])}</text>')
        # description, up to 2 wrapped lines
        char_w = int((col_w - 32) / 6.2)
        for li, line in enumerate(_wrap(r.get("desc") or "", char_w, 2)):
            parts.append(f'<text x="{tx:.1f}" y="{y + 46 + li * 16:.1f}" '
                         f'class="desc">{_esc(line)}</text>')
        # meta row: lang dot + name + stars
        my = y + tile_h - 14
        lang = r.get("lang")
        cx = tx
        if lang:
            color = LANG_COLORS.get(lang, "#8b8b8b")
            parts.append(f'<circle cx="{cx + 5:.1f}" cy="{my - 4:.1f}" r="5" '
                         f'fill="{color}"/>')
            parts.append(f'<text x="{cx + 16:.1f}" y="{my:.1f}" class="meta">'
                         f'{_esc(lang)}</text>')
            cx += 16 + len(lang) * 7 + 16
        parts.append(f'<text x="{cx:.1f}" y="{my:.1f}" class="meta">'
                     f'★ {r.get("stars", 0)}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if "--selftest" in sys.argv:
        return _selftest()
    src = os.environ.get("FEATURED_JSON")
    repos = json.load(open(src)) if src else fetch()
    with open("github-featured.svg", "w") as f:
        f.write(render_svg(repos))
    print(f"wrote github-featured.svg ({len(repos)} repos)")
    for r in repos:
        print(f"  {r['name']}: ★{r.get('stars', 0)} {r.get('lang')}")


def _selftest():
    sample = [
        {"name": "maestro", "desc": "Spawns and monitors multiple AI providers "
         "in parallel from one CLI", "lang": "Rust", "stars": 29},
        {"name": "copyrfid", "desc": "RFID/NFC card reader for the M5StickC Plus",
         "lang": "C++", "stars": 9},
        {"name": "saopaulo-night", "desc": "Muted cyberpunk Sao Paulo night theme",
         "lang": "TypeScript", "stars": 2},
        {"name": "discipline.nvim", "desc": "Neovim plugin that warns you when you "
         "use bad habits", "lang": "Lua", "stars": 1},
        {"name": "lucid-engine", "desc": "Stockfish-powered chess engine for iOS/macOS",
         "lang": "C++", "stars": 1},
        {"name": "tsumiki", "desc": "A SwiftUI component library", "lang": "Swift",
         "stars": 0},
    ]
    svg = render_svg(sample)
    import xml.dom.minidom as m
    m.parseString(svg)
    assert "Featured Projects" in svg and "maestro" in svg
    assert svg.count('class="repo"') == 6
    print("selftest OK")


if __name__ == "__main__":
    main()
