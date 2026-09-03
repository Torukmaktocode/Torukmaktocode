#!/usr/bin/env python3
"""
Fetch GitHub contributions and render dark theme heatmap SVG.
Usage: python fetch_and_render.py [username]
"""
import requests
import json
from datetime import datetime, timedelta
import sys

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "Torukmaktocode"

# GitHub's dark palette (dark to bright green)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL_SIZE = 11
CELL_GAP = 3
WEEKS = 52

def fetch_contributions(username):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def render_svg(data, output_path):
    contributions = data.get("contributions", [])
    
    # Build lookup dict
    day_map = {}
    for c in contributions:
        day_map[c["date"]] = c["count"]
    
    # Calculate grid
    today = datetime.now().date()
    start = today - timedelta(weeks=WEEKS)
    start -= timedelta(days=start.weekday() + 1)  # align to Sunday
    
    svg_w = WEEKS * (CELL_SIZE + CELL_GAP) + 50
    svg_h = 7 * (CELL_SIZE + CELL_GAP) + 60
    
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">',
        f'<rect width="{svg_w}" height="{svg_h}" fill="#0d1117" rx="6"/>',
    ]
    
    # Month labels
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    last_month = -1
    for w in range(WEEKS):
        d = start + timedelta(weeks=w)
        m = d.month - 1
        if m != last_month:
            last_month = m
            x = 44 + w * (CELL_SIZE + CELL_GAP)
            parts.append(f'<text x="{x}" y="12" fill="#8b949e" font-family="sans-serif" font-size="10">{months[m]}</text>')
    
    # Day labels
    day_labels = ["", "Mon", "", "Wed", "", "Fri", ""]
    for i, label in enumerate(day_labels):
        if label:
            y = 22 + i * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 1
            parts.append(f'<text x="0" y="{y}" fill="#8b949e" font-family="sans-serif" font-size="10">{label}</text>')
    
    # Cells
    for w in range(WEEKS):
        for d in range(7):
            current = start + timedelta(weeks=w, days=d)
            if current > today:
                continue
            
            date_str = current.isoformat()
            count = day_map.get(date_str, 0)
            
            # Calculate level (0-4)
            if count == 0:
                level = 0
            elif count <= 3:
                level = 1
            elif count <= 6:
                level = 2
            elif count <= 9:
                level = 3
            else:
                level = 4
            
            x = 44 + w * (CELL_SIZE + CELL_GAP)
            y = 20 + d * (CELL_SIZE + CELL_GAP)
            color = PALETTE[min(level, len(PALETTE) - 1)]
            
            parts.append(f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" rx="2"><title>{count} contributions on {date_str}</title></rect>')
    
    # Legend
    legend_x = svg_w - 110
    legend_y = svg_h - 12
    parts.append(f'<text x="{legend_x - 28}" y="{legend_y + 1}" fill="#8b949e" font-family="sans-serif" font-size="10">Less</text>')
    for i, color in enumerate(PALETTE):
        x = legend_x + i * (CELL_SIZE + CELL_GAP)
        parts.append(f'<rect x="{x}" y="{legend_y - 10}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" rx="2"/>')
    parts.append(f'<text x="{legend_x + 6 * (CELL_SIZE + CELL_GAP) + 4}" y="{legend_y + 1}" fill="#8b949e" font-family="sans-serif" font-size="10">More</text>')
    
    parts.append("</svg>")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    
    total = sum(day_map.values())
    print(f"[OK] Heatmap saved to {output_path}")
    print(f"     {total} contributions in the last year")

if __name__ == "__main__":
    data = fetch_contributions(USERNAME)
    render_svg(data, "contributions.svg")
