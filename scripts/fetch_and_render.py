#!/usr/bin/env python3
"""
Fetch GitHub contributions and render dark theme heatmap SVG.
Matches GitHub's native contribution graph layout exactly.
Usage: python fetch_and_render.py [username]
"""
import requests
from datetime import datetime, timedelta
import sys

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "Torukmaktocode"

# GitHub's exact dark palette
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b949e"
ROUND = 2

CELL = 10
GAP = 3
STEP = CELL + GAP
LEFT_PAD = 35
TOP_PAD = 22

def fetch(username):
    r = requests.get(f"https://github-contributions-api.jogruber.de/v4/{username}", timeout=30)
    r.raise_for_status()
    return r.json()

def render(data, out):
    days = {c["date"]: c["count"] for c in data.get("contributions", [])}
    total = sum(days.values())

    today = datetime.now().date()
    # Find the Sunday of the current week, then go back 52 weeks
    end = today
    # Go back to find the last Sunday
    start = end - timedelta(weeks=52)
    start -= timedelta(days=(start.weekday() + 1) % 7)

    # Count actual weeks
    weeks = (end - start).days // 7 + 1

    w = LEFT_PAD + weeks * STEP + 20
    h = TOP_PAD + 7 * STEP + 30

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
           f'<rect width="{w}" height="{h}" fill="{BG_COLOR}" rx="4"/>']

    # Month labels
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    shown = set()
    for wk in range(weeks):
        d = start + timedelta(weeks=wk)
        m = d.month
        if m not in shown:
            shown.add(m)
            x = LEFT_PAD + wk * STEP
            svg.append(f'<text x="{x}" y="13" fill="{TEXT_COLOR}" font-size="10" font-family="sans-serif">{months[m-1]}</text>')

    # Day labels (Mon, Wed, Fri)
    for i, label in enumerate(["Mon","","Wed","","Fri"]):
        if label:
            y = TOP_PAD + i * STEP + CELL - 1
            svg.append(f'<text x="0" y="{y}" fill="{TEXT_COLOR}" font-size="10" font-family="sans-serif">{label}</text>')

    # Cells
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

            x = LEFT_PAD + wk * STEP
            y = TOP_PAD + d * STEP
            color = PALETTE[lvl]
            svg.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{color}" rx="{ROUND}"><title>{count} contributions on {key}</title></rect>')

    # Legend
    lx = w - 100
    ly = h - 10
    svg.append(f'<text x="{lx - 24}" y="{ly + 1}" fill="{TEXT_COLOR}" font-size="10" font-family="sans-serif">Less</text>')
    for i, c in enumerate(PALETTE):
        svg.append(f'<rect x="{lx + i * (CELL + GAP)}" y="{ly - 9}" width="{CELL}" height="{CELL}" fill="{c}" rx="{ROUND}"/>')
    svg.append(f'<text x="{lx + 5 * (CELL + GAP) + 5}" y="{ly + 1}" fill="{TEXT_COLOR}" font-size="10" font-family="sans-serif">More</text>')

    svg.append("</svg>")

    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    print(f"[OK] Heatmap saved: {out}")
    print(f"     {total} contributions in the last year")

if __name__ == "__main__":
    data = fetch(USERNAME)
    render(data, "contributions.svg")
