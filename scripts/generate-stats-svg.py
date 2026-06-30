#!/usr/bin/env python3
"""Generate github-stats.svg: a big, readable stats card for the profile README.

Data source: GitHub GraphQL via the `gh` CLI (classic token in GH_TOKEN).
Lifetime commit/review totals are aggregated year-by-year because
`contributionsCollection` only spans one year per query.

Usage:
    GH_TOKEN=... python scripts/generate-stats-svg.py     # fetch live, write svg
    STATS_JSON=stats.json python scripts/generate-stats-svg.py  # render from file
    python scripts/generate-stats-svg.py --selftest       # render sample, assert valid

Output: github-stats.svg in the current working directory.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

USER = os.environ.get("STATS_USER", "CarlosDanielDev")

# ponytail: gh CLI does auth + transport. No requests dep, no token plumbing here.
def _gh_graphql(query):
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)["data"]["viewer"]


def fetch_stats():
    base_q = """
    {
      viewer {
        name login createdAt
        followers { totalCount }
        following { totalCount }
        starredRepositories { totalCount }
        pullRequests { totalCount }
        issues { totalCount }
        repositoriesContributedTo(
          contributionTypes: [COMMIT, PULL_REQUEST, ISSUE, PULL_REQUEST_REVIEW]
        ) { totalCount }
      }
    }"""
    v = _gh_graphql(base_q)
    start_year = int(v["createdAt"][:4])
    now = datetime.now(timezone.utc)

    commits = 0
    reviews = 0
    for year in range(start_year, now.year + 1):
        frm = f"{year}-01-01T00:00:00Z"
        to = f"{year}-12-31T23:59:59Z"
        yq = f"""
        {{
          viewer {{
            contributionsCollection(from: "{frm}", to: "{to}") {{
              totalCommitContributions
              restrictedContributionsCount
              totalPullRequestReviewContributions
            }}
          }}
        }}"""
        c = _gh_graphql(yq)["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]
        reviews += c["totalPullRequestReviewContributions"]

    years = now.year - start_year or 1

    return {
        "name": v["name"] or v["login"],
        "createdYear": start_year,
        "yearsCoding": years,
        "commits": commits,
        "prsOpened": v["pullRequests"]["totalCount"],
        "prsReviewed": reviews,
        "issuesOpened": v["issues"]["totalCount"],
        "reposContributed": v["repositoriesContributedTo"]["totalCount"],
        "followers": v["followers"]["totalCount"],
        "following": v["following"]["totalCount"],
        "starred": v["starredRepositories"]["totalCount"],
    }


# --- rendering ---------------------------------------------------------------

W = 760
PAD = 28
ACCENT = "#70A5FD"
MUTED = "#8b949e"
DIM = "#6e7681"
BG = "#0d1117"
BORDER = "#30363d"
FONT = ('font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", '
        "Helvetica, Arial, sans-serif;")


def _fmt(n):
    return f"{n:,}"


def render_svg(s):
    tiles = [
        ("Commits", _fmt(s["commits"])),
        ("Pull Requests", _fmt(s["prsOpened"])),
        ("PRs Reviewed", _fmt(s["prsReviewed"])),
        ("Issues Opened", _fmt(s["issuesOpened"])),
        ("Repos Contributed", _fmt(s["reposContributed"])),
        ("Years on GitHub", _fmt(s["yearsCoding"])),
        ("Followers", _fmt(s["followers"])),
        ("Following", _fmt(s["following"])),
        ("Repos Starred", _fmt(s["starred"])),
    ]

    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    head_h = 70
    tile_h = 78
    grid_w = W - PAD * 2
    col_w = grid_w / cols
    height = head_h + rows * tile_h + PAD

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="GitHub statistics">',
        "<defs>",
        '  <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">',
        '    <stop offset="0" stop-color="#70A5FD"/>',
        '    <stop offset="1" stop-color="#B388FF"/>',
        "  </linearGradient>",
        "</defs>",
        "<style>",
        f"  text {{ {FONT} }}",
        f"  .title {{ font-size: 20px; font-weight: 700; fill: {ACCENT}; }}",
        f"  .sub {{ font-size: 12px; fill: {DIM}; }}",
        "  .num { font-size: 32px; font-weight: 700; fill: #e6edf3; text-anchor: middle; }",
        f"  .lbl {{ font-size: 13px; fill: {MUTED}; text-anchor: middle; }}",
        "</style>",
        # card
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="14" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # gradient accent bar
        f'<rect x="{PAD}" y="{PAD}" width="64" height="5" rx="2.5" fill="url(#g)"/>',
        f'<text x="{PAD}" y="{PAD + 30}" class="title">GitHub Stats</text>',
        f'<text x="{PAD}" y="{PAD + 48}" class="sub">{_esc(s["name"])} '
        f'&#183; on GitHub since {s["createdYear"]}</text>',
    ]

    for i, (label, value) in enumerate(tiles):
        r, c = divmod(i, cols)
        cx = PAD + col_w * (c + 0.5)  # centered within each column
        cy = head_h + r * tile_h
        parts.append(f'<text x="{cx:.1f}" y="{cy + 34:.1f}" class="num">{value}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{cy + 54:.1f}" class="lbl">{label}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def _esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    if "--selftest" in sys.argv:
        return _selftest()

    src = os.environ.get("STATS_JSON")
    stats = json.load(open(src)) if src else fetch_stats()

    svg = render_svg(stats)
    with open("github-stats.svg", "w") as f:
        f.write(svg)
    print("wrote github-stats.svg")
    for k, v in stats.items():
        print(f"  {k}: {v}")


def _selftest():
    sample = {
        "name": "Carlos Daniel", "createdYear": 2017, "yearsCoding": 8,
        "commits": 4946, "prsOpened": 773, "prsReviewed": 173,
        "issuesOpened": 1101, "reposContributed": 40, "followers": 87,
        "following": 62, "starred": 157,
    }
    svg = render_svg(sample)
    import xml.dom.minidom as m
    m.parseString(svg)  # raises if invalid XML
    assert "4,946" in svg and "GitHub Stats" in svg
    assert svg.count('class="num"') == 9
    print("selftest OK")


if __name__ == "__main__":
    main()
