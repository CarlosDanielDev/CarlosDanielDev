#!/usr/bin/env python3
"""Generate github-streak-card.svg: total contributions + current & longest streak.

Self-hosted alternative to github-readme-streak-stats (no flaky heroku).
Walks the full daily contribution calendar (createdAt..today) via `gh` GraphQL.

Usage:
    GH_TOKEN=... python scripts/generate-streak-svg.py
    CONTRIB_JSON=days.json python scripts/generate-streak-svg.py   # render from file
    python scripts/generate-streak-svg.py --selftest

Output: github-streak-card.svg in the current working directory.
"""
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone

USER = os.environ.get("STATS_USER", "CarlosDanielDev")


def _gh_graphql(query):
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)["data"]["viewer"]


def fetch_days():
    """Return {iso_date: count} for every day since account creation."""
    created = _gh_graphql("{ viewer { createdAt } }")["createdAt"]
    start_year = int(created[:4])
    now = datetime.now(timezone.utc)
    days = {}
    for year in range(start_year, now.year + 1):
        frm = f"{year}-01-01T00:00:00Z"
        to = f"{year}-12-31T23:59:59Z"
        q = f"""
        {{
          viewer {{
            contributionsCollection(from: "{frm}", to: "{to}") {{
              contributionCalendar {{
                weeks {{ contributionDays {{ date contributionCount }} }}
              }}
            }}
          }}
        }}"""
        cal = _gh_graphql(q)["contributionsCollection"]["contributionCalendar"]
        for week in cal["weeks"]:
            for d in week["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return days


def compute(days):
    total = sum(days.values())
    if not days:
        return {"total": 0, "current": 0, "longest": 0,
                "currentRange": "", "longestRange": ""}

    sorted_dates = sorted(days.keys())
    d0 = datetime.strptime(sorted_dates[0], "%Y-%m-%d").date()
    today = datetime.now(timezone.utc).date()

    # longest streak across the whole history
    longest = cur = 0
    long_end = long_start = cur_start = None
    day = d0
    one = timedelta(days=1)
    while day <= today:
        if days.get(day.isoformat(), 0) > 0:
            if cur == 0:
                cur_start = day
            cur += 1
            if cur > longest:
                longest, long_start, long_end = cur, cur_start, day
        else:
            cur = 0
        day += one

    # current streak: walk back from today; today==0 doesn't break it yet
    cur_streak = 0
    cur_s = cur_e = None
    day = today
    if days.get(today.isoformat(), 0) == 0:
        day = today - one  # grace: today not over
    while day >= d0 and days.get(day.isoformat(), 0) > 0:
        if cur_e is None:
            cur_e = day
        cur_s = day
        cur_streak += 1
        day -= one

    def rng(a, b):
        if not a or not b:
            return ""
        f = "%b %d, %Y"
        return f"{a.strftime(f)} - {b.strftime(f)}"

    return {
        "total": total,
        "current": cur_streak,
        "longest": longest,
        "currentRange": rng(cur_s, cur_e) if cur_streak else "—",
        "longestRange": rng(long_start, long_end) if longest else "—",
    }


# --- rendering ---------------------------------------------------------------

W, H = 495, 195
ACCENT = "#70A5FD"
FIRE = "#FB8C00"
MUTED = "#8b949e"
DIM = "#6e7681"
BG = "#0d1117"
BORDER = "#30363d"
FONT = ('font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", '
        "Helvetica, Arial, sans-serif;")


def _fmt(n):
    return f"{n:,}"


def render_svg(s):
    col = W / 3
    cx_total, cx_cur, cx_long = col * 0.5, col * 1.5, col * 2.5
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Contribution streak">',
        "<defs>",
        '  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">',
        f'    <stop offset="0" stop-color="{FIRE}"/>',
        '    <stop offset="1" stop-color="#FFCA28"/>',
        "  </linearGradient>",
        "</defs>",
        "<style>",
        f"  text {{ {FONT} text-anchor: middle; }}",
        "  .big { font-size: 30px; font-weight: 700; fill: #e6edf3; }",
        f"  .lbl {{ font-size: 13px; fill: {ACCENT}; font-weight: 600; }}",
        f"  .rng {{ font-size: 10px; fill: {DIM}; }}",
        f"  .fire {{ font-size: 28px; font-weight: 700; fill: {FIRE}; }}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # dividers
        f'<line x1="{col:.0f}" y1="36" x2="{col:.0f}" y2="{H - 36}" '
        f'stroke="{BORDER}"/>',
        f'<line x1="{col * 2:.0f}" y1="36" x2="{col * 2:.0f}" y2="{H - 36}" '
        f'stroke="{BORDER}"/>',
        # total
        f'<text x="{cx_total:.0f}" y="78" class="big">{_fmt(s["total"])}</text>',
        f'<text x="{cx_total:.0f}" y="104" class="lbl">Total Contributions</text>',
        f'<text x="{cx_total:.0f}" y="124" class="rng">All time</text>',
        # current streak (flame ring)
        f'<circle cx="{cx_cur:.0f}" cy="74" r="34" fill="none" '
        f'stroke="url(#ring)" stroke-width="4"/>',
        f'<text x="{cx_cur:.0f}" y="84" class="fire">{s["current"]}</text>',
        f'<text x="{cx_cur:.0f}" y="134" class="lbl">Current Streak</text>',
        f'<text x="{cx_cur:.0f}" y="152" class="rng">{_esc(s["currentRange"])}</text>',
        # longest streak
        f'<text x="{cx_long:.0f}" y="78" class="big">{s["longest"]}</text>',
        f'<text x="{cx_long:.0f}" y="104" class="lbl">Longest Streak</text>',
        f'<text x="{cx_long:.0f}" y="124" class="rng">{_esc(s["longestRange"])}</text>',
        "</svg>",
    ]
    return "\n".join(parts)


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    if "--selftest" in sys.argv:
        return _selftest()

    src = os.environ.get("CONTRIB_JSON")
    days = json.load(open(src)) if src else fetch_days()
    stats = compute(days)

    with open("github-streak-card.svg", "w") as f:
        f.write(render_svg(stats))
    print("wrote github-streak-card.svg")
    for k, v in stats.items():
        print(f"  {k}: {v}")


def _selftest():
    # 5-day current streak ending today, a 10-day run earlier
    today = date(2026, 6, 30)
    days = {}
    for i in range(5):
        days[(today - timedelta(days=i)).isoformat()] = 3
    base = date(2026, 1, 1)
    for i in range(10):
        days[(base + timedelta(days=i)).isoformat()] = 2
    s = compute(days)
    assert s["current"] == 5, s
    assert s["longest"] == 10, s
    assert s["total"] == 5 * 3 + 10 * 2, s
    import xml.dom.minidom as m
    m.parseString(render_svg(s))
    print("selftest OK", s)


if __name__ == "__main__":
    main()
