#!/usr/bin/env python3
"""Generate github-activity.svg: a smooth area chart of monthly contributions
over the last 12 months. Self-hosted (no external render service).

Usage:
    GH_TOKEN=... python scripts/generate-activity-svg.py
    CONTRIB_JSON=days.json python scripts/generate-activity-svg.py
    python scripts/generate-activity-svg.py --selftest

Output: github-activity.svg in the current working directory.
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


def fetch_days():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)
    q = f"""
    {{
      viewer {{
        contributionsCollection(
          from: "{start.strftime('%Y-%m-%dT00:00:00Z')}",
          to: "{now.strftime('%Y-%m-%dT23:59:59Z')}"
        ) {{
          contributionCalendar {{
            weeks {{ contributionDays {{ date contributionCount }} }}
          }}
        }}
      }}
    }}"""
    cal = _gh_graphql(q)["contributionsCollection"]["contributionCalendar"]
    days = {}
    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            days[d["date"]] = d["contributionCount"]
    return days


def monthly(days):
    """Aggregate {date: count} into the trailing 12 months [(label, total)]."""
    now = datetime.now(timezone.utc)
    y, mo = now.year, now.month
    months = []
    for _ in range(12):
        months.append((y, mo))
        mo -= 1
        if mo == 0:
            mo, y = 12, y - 1
    months.reverse()

    sums = {ym: 0 for ym in months}
    for ds, cnt in days.items():
        dt = datetime.strptime(ds, "%Y-%m-%d")
        key = (dt.year, dt.month)
        if key in sums:
            sums[key] += cnt

    names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return [(names[m], sums[(yy, m)]) for (yy, m) in months]


# --- rendering ---------------------------------------------------------------

W, H = 760, 230
PAD_L, PAD_R, PAD_T, PAD_B = 44, 24, 64, 40
ACCENT = "#70A5FD"
MUTED = "#8b949e"
DIM = "#6e7681"
BG = "#0d1117"
BORDER = "#30363d"
FONT = ('font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", '
        "Helvetica, Arial, sans-serif;")


def _smooth_path(pts):
    """Catmull-Rom -> cubic bezier for a smooth line through points."""
    if len(pts) < 2:
        return ""
    d = [f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[0]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1x = p1[0] + (p2[0] - p0[0]) / 6
        c1y = p1[1] + (p2[1] - p0[1]) / 6
        c2x = p2[0] - (p3[0] - p1[0]) / 6
        c2y = p2[1] - (p3[1] - p1[1]) / 6
        d.append(f"C {c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} "
                 f"{p2[0]:.1f} {p2[1]:.1f}")
    return " ".join(d)


def render_svg(series, total):
    plot_w = W - PAD_L - PAD_R
    plot_h = H - PAD_T - PAD_B
    n = len(series)
    vmax = max((v for _, v in series), default=1) or 1

    pts = []
    for i, (_, v) in enumerate(series):
        x = PAD_L + (plot_w * i / (n - 1) if n > 1 else 0)
        yv = PAD_T + plot_h - (v / vmax) * plot_h
        pts.append((x, yv))

    line = _smooth_path(pts)
    baseline = PAD_T + plot_h
    area = f"{line} L {pts[-1][0]:.1f} {baseline:.1f} L {pts[0][0]:.1f} {baseline:.1f} Z"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Contribution activity">',
        "<defs>",
        '  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">',
        f'    <stop offset="0" stop-color="{ACCENT}" stop-opacity="0.45"/>',
        f'    <stop offset="1" stop-color="{ACCENT}" stop-opacity="0.02"/>',
        "  </linearGradient>",
        '  <linearGradient id="stroke" x1="0" y1="0" x2="1" y2="0">',
        '    <stop offset="0" stop-color="#70A5FD"/>',
        '    <stop offset="1" stop-color="#B388FF"/>',
        "  </linearGradient>",
        "</defs>",
        "<style>",
        f"  text {{ {FONT} }}",
        f"  .title {{ font-size: 16px; font-weight: 700; fill: {ACCENT}; }}",
        f"  .sub {{ font-size: 12px; fill: {DIM}; }}",
        f"  .ax {{ font-size: 10px; fill: {DIM}; text-anchor: middle; }}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="{PAD_L}" y="34" class="title">Contribution Activity</text>',
        f'<text x="{PAD_L}" y="50" class="sub">{total:,} contributions in the '
        f'last 12 months</text>',
    ]

    # subtle gridlines (3)
    for g in range(1, 4):
        gy = PAD_T + plot_h * g / 4
        parts.append(f'<line x1="{PAD_L}" y1="{gy:.0f}" x2="{W - PAD_R}" '
                     f'y2="{gy:.0f}" stroke="{BORDER}" stroke-opacity="0.5"/>')

    parts.append(f'<path d="{area}" fill="url(#area)"/>')
    parts.append(f'<path d="{line}" fill="none" stroke="url(#stroke)" '
                 f'stroke-width="2.5" stroke-linecap="round"/>')

    # dots on each month
    for (x, yv) in pts:
        parts.append(f'<circle cx="{x:.1f}" cy="{yv:.1f}" r="2.5" '
                     f'fill="#0d1117" stroke="{ACCENT}" stroke-width="1.5"/>')

    # month labels
    for i, (label, _) in enumerate(series):
        x = pts[i][0]
        parts.append(f'<text x="{x:.1f}" y="{H - 16}" class="ax">{label}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if "--selftest" in sys.argv:
        return _selftest()

    src = os.environ.get("CONTRIB_JSON")
    days = json.load(open(src)) if src else fetch_days()
    series = monthly(days)
    total = sum(v for _, v in series)

    with open("github-activity.svg", "w") as f:
        f.write(render_svg(series, total))
    print("wrote github-activity.svg")
    for label, v in series:
        print(f"  {label}: {v}")


def _selftest():
    series = [("Jul", 30), ("Aug", 45), ("Sep", 12), ("Oct", 60), ("Nov", 80),
              ("Dec", 20), ("Jan", 55), ("Feb", 90), ("Mar", 40), ("Apr", 70),
              ("May", 110), ("Jun", 65)]
    svg = render_svg(series, sum(v for _, v in series))
    import xml.dom.minidom as m
    m.parseString(svg)
    assert "Contribution Activity" in svg
    assert svg.count("<circle") == 12
    print("selftest OK")


if __name__ == "__main__":
    main()
