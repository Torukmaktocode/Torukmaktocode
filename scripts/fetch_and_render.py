#!/usr/bin/env python3
"""
Fetch GitHub contributions and render premium dark heatmap SVG.
"""
import requests
from datetime import datetime, timedelta
import sys

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "Torukmaktocode"

# Premium dark palette with gradient
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
TEXT = "#8b949e"
BORDER = "#30363d"

CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT = 38
TOP = 28

def fetch(username):
    r = requests.get(f"https://github-contributions-api.jogruber.de/v4/{username}", timeout=30)
    r.raise_for_status()
    return r.json()

def render(data, out):
    days = {c["date"]: c["count"] for c in data.get("contributions", [])}
    total = sum(days.values())

    today = datetime.now().date()
    start = today - timedelta(weeks=52)
    start -= timedelta(days=(start.weekday() + 1) % 7)

    weeks = (today - start).days // 7 + 1

    w = LEFT + weeks * STEP + 30
    h = TOP + 7 * STEP + 40

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'<defs>',
        f'  <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        f'    <stop offset="0%" stop-color="#39d353"/>',
        f'    <stop offset="100%" stop-color="#26a641"/>',
        f'  </linearGradient>',
        f'  <filter id="glow">',
        f'    <feGaussianBlur stdDeviation="1" result="blur"/>',
        f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>',
        f'  </filter>',
        f'</defs>',
        f'<rect width="{w}" height="{h}" fill="{BG}" rx="6"/>',
        f'<rect x="0" y="0" width="{w}" height="4" fill="url(#headerGrad)" rx="6"/>',
    ]

    # Header
    svg.append(f'<text x="12" y="22" fill="#ffffff" font-size="13" font-weight="600" font-family="sans-serif">{total} contributions in the last year</text>')

    # Month labels
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    shown = set()
    for wk in range(weeks):
        d = start + timedelta(weeks=wk)
        m = d.month
        if m not in shown:
            shown.add(m)
            x = LEFT + wk * STEP
            svg.append(f'<text x="{x}" y="{TOP - 6}" fill="{TEXT}" font-size="10" font-family="sans-serif">{months[m-1]}</text>')

    # Day labels
    for i, label in enumerate(["Mon","","Wed","","Fri"]):
        if label:
            y = TOP + i * STEP + CELL - 1
            svg.append(f'<text x="0" y="{y}" fill="{TEXT}" font-size="10" font-family="sans-serif">{label}</text>')

    # Cells with hover effect
    for wk in range(weeks):
        for d in range(7):
            dt = start + timedelta(weeks=wk, days=d)
            if dt > today:
                continue
            key = dt.isoformat()
            count = days.get(key, 0)

            if count == 0:
                lvl = 0
            elif count <= 2:
                lvl = 1
            elif count <= 5:
                lvl = 2
            elif count <= 9:
                lvl = 3
            else:
                lvl = 4

            x = LEFT + wk * STEP
            y = TOP + d * STEP
            color = PALETTE[lvl]
            
            # Add subtle shadow for active cells
            if lvl > 0:
                svg.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{color}" rx="2" opacity="0.3" filter="url(#glow)"/>')
            
            svg.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{color}" rx="2"><title>{count} contributions on {key}</title></rect>')

    # Legend
    lx = w - 110
    ly = h - 14
    svg.append(f'<text x="{lx - 28}" y="{ly + 1}" fill="{TEXT}" font-size="10" font-family="sans-serif">Less</text>')
    for i, c in enumerate(PALETTE):
        svg.append(f'<rect x="{lx + i * (CELL + GAP)}" y="{ly - 9}" width="{CELL}" height="{CELL}" fill="{c}" rx="2"/>')
    svg.append(f'<text x="{lx + 6 * (CELL + GAP) + 5}" y="{ly + 1}" fill="{TEXT}" font-size="10" font-family="sans-serif">More</text>')

    svg.append("</svg>")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    print(f"[OK] Heatmap saved: {out}")
    print(f"     {total} contributions")

if __name__ == "__main__":
    data = fetch(USERNAME)
    render(data, "contributions.svg")
