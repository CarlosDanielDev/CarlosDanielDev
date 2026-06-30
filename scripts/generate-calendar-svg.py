#!/usr/bin/env python3
"""Generate github-calendar.svg: a GitHub-style contribution heatmap for the
last ~12 months. Self-hosted (no external render service), themed blue to match
the rest of the profile cards.

Usage:
    GH_TOKEN=... python scripts/generate-calendar-svg.py
    WEEKS_JSON=weeks.json python scripts/generate-calendar-svg.py
    python scripts/generate-calendar-svg.py --selftest

Output: github-calendar.svg in the current working directory.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

USER = os.environ.get("STATS_USER", "CarlosDanielDev")


def _gh_graphql(query):
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)["data"]["viewer"]


def fetch_weeks():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=371)
    q = f"""
    {{
      viewer {{
        contributionsCollection(
          from: "{start.strftime('%Y-%m-%dT00:00:00Z')}",
          to: "{now.strftime('%Y-%m-%dT23:59:59Z')}"
        ) {{
          contributionCalendar {{
            weeks {{ contributionDays {{ date contributionCount weekday }} }}
          }}
        }}
      }}
    }}"""
    return _gh_graphql(q)["contributionsCollection"]["contributionCalendar"]["weeks"]


# --- rendering ---------------------------------------------------------------

PAD = 28
TOP = 64           # title + month labels
CELL = 10
GAP = 3
STEP = CELL + GAP
LEVELS = ["#161b22", "#1b3a6b", "#2b5cab", "#4d86e0", "#70A5FD"]
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FONT = ('font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", '
        "Helvetica, Arial, sans-serif;")


def _level(count):
    if count <= 0:
        return 0
    if count <= 3:
        return 1
    if count <= 7:
        return 2
    if count <= 12:
        return 3
    return 4


def render_svg(weeks):
    n_weeks = len(weeks)
    grid_w = n_weeks * STEP - GAP
    W = max(760, grid_w + PAD * 2)
    # center the grid inside the card
    x0 = (W - grid_w) / 2
    H = TOP + 7 * STEP - GAP + PAD

    total = sum(d["contributionCount"] for wk in weeks for d in wk["contributionDays"])

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Contribution calendar">',
        "<style>",
        f"  text {{ {FONT} fill: #8b949e; }}",
        "  .t { font-size: 20px; fill: #70A5FD; font-weight: 700; }",
        "  .sub { font-size: 12px; fill: #6e7681; }",
        "  .m { font-size: 10px; fill: #6e7681; }",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" '
        'fill="#0d1117" stroke="#30363d"/>',
        f'<text x="{PAD}" y="{PAD + 14}" class="t">Contribution Calendar</text>',
        f'<text x="{W - PAD}" y="{PAD + 14}" class="sub" '
        f'text-anchor="end">{total:,} contributions</text>',
    ]

    # month labels: print a month when its first week starts
    last_month = None
    for wi, wk in enumerate(weeks):
        first = wk["contributionDays"][0]["date"]
        m = int(first[5:7])
        if m != last_month:
            lx = x0 + wi * STEP
            parts.append(f'<text x="{lx:.1f}" y="{TOP - 8}" class="m">'
                         f'{MONTHS[m]}</text>')
            last_month = m

    # cells
    for wi, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            wd = d["weekday"]
            lvl = _level(d["contributionCount"])
            x = x0 + wi * STEP
            y = TOP + wd * STEP
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{LEVELS[lvl]}"/>'
            )

    # legend
    ly = H - PAD + 4
    lx = W - PAD - (len(LEVELS) * (CELL + 4)) - 60
    parts.append(f'<text x="{lx - 8:.1f}" y="{ly + 9:.1f}" class="m" '
                 f'text-anchor="end">Less</text>')
    for i, c in enumerate(LEVELS):
        parts.append(f'<rect x="{lx + i * (CELL + 4):.1f}" y="{ly:.1f}" '
                     f'width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    parts.append(f'<text x="{lx + len(LEVELS) * (CELL + 4) + 4:.1f}" '
                 f'y="{ly + 9:.1f}" class="m">More</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if "--selftest" in sys.argv:
        return _selftest()

    src = os.environ.get("WEEKS_JSON")
    weeks = json.load(open(src)) if src else fetch_weeks()

    with open("github-calendar.svg", "w") as f:
        f.write(render_svg(weeks))
    total = sum(d["contributionCount"] for wk in weeks for d in wk["contributionDays"])
    print(f"wrote github-calendar.svg ({len(weeks)} weeks, {total} contributions)")


def _selftest():
    # build 53 fake weeks
    weeks = []
    start = datetime(2025, 6, 1)
    day = start
    for w in range(53):
        days = []
        for wd in range(7):
            days.append({"date": day.strftime("%Y-%m-%d"),
                         "contributionCount": (w + wd) % 15, "weekday": wd})
            day += timedelta(days=1)
        weeks.append({"contributionDays": days})
    svg = render_svg(weeks)
    import xml.dom.minidom as m
    m.parseString(svg)
    assert "Contribution Calendar" in svg
    assert svg.count("<rect") >= 53 * 7
    print("selftest OK")


if __name__ == "__main__":
    main()
