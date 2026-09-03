#!/usr/bin/env python3
"""
Render contribution heatmap SVG from JSON data.
Usage: python render_heatmap_svg.py [input.json] [output.svg]
"""
import sys
import json
from datetime import datetime, timedelta

# GitHub's green palette
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL_SIZE = 12
CELL_GAP = 3
CELL_R = 2
WEEKS = 53
DAYS = 7

SVG_W = WEEKS * (CELL_SIZE + CELL_GAP) + 60
SVG_H = DAYS * (CELL_SIZE + CELL_GAP) + 80

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def render_heatmap(data_path, output_path):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    days = data.get("days", [])
    stats = data.get("stats", {})
    
    # Index days by date
    day_map = {d["date"]: d for d in days}
    
    # Build 53-week x 7-day grid starting from the earliest Sunday
    today = datetime.now().date()
    end_date = today
    
    # Find the start: 52 weeks ago, aligned to Sunday
    start_date = today - timedelta(weeks=52)
    start_date -= timedelta(days=start_date.weekday() + 1)  # align to Sunday
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}">',
        f'<rect width="{SVG_W}" height="{SVG_H}" fill="#0d1117"/>',
        '<style>',
        '  .cell { rx: 2; ry: 2; }',
        '  @keyframes slideIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }',
        '  .reveal { animation: slideIn 0.2s ease-out forwards; animation-fill-mode: both; opacity: 0; }',
        '  text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }',
        '</style>',
    ]
    
    # Month labels
    current_month = -1
    for week in range(WEEKS):
        week_start = start_date + timedelta(weeks=week)
        month = week_start.month - 1
        if month != current_month:
            current_month = month
            x = 48 + week * (CELL_SIZE + CELL_GAP)
            svg_parts.append(
                f'<text x="{x}" y="12" fill="#8b949e" font-size="10">{MONTHS[month]}</text>'
            )
    
    # Day labels
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for day_idx in range(0, 7, 2):  # Only Mon, Wed, Fri
        y = 28 + day_idx * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 2
        svg_parts.append(
            f'<text x="0" y="{y}" fill="#8b949e" font-size="10">{day_labels[day_idx]}</text>'
        )
    
    # Cells
    cell_idx = 0
    for week in range(WEEKS):
        for day_idx in range(7):
            current_date = start_date + timedelta(weeks=week, days=day_idx)
            if current_date > end_date:
                continue
            
            date_str = current_date.strftime("%Y-%m-%d")
            day_data = day_map.get(date_str, {"level": 0, "count": 0})
            level = day_data["level"]
            count = day_data["count"]
            
            x = 48 + week * (CELL_SIZE + CELL_GAP)
            y = 20 + day_idx * (CELL_SIZE + CELL_GAP)
            color = PALETTE[min(level, len(PALETTE) - 1)]
            
            delay = (week * 7 + day_idx) * 0.003  # diagonal reveal
            
            svg_parts.append(
                f'<rect class="cell reveal" x="{x}" y="{y}" '
                f'width="{CELL_SIZE}" height="{CELL_SIZE}" '
                f'fill="{color}" '
                f'style="animation-delay: {delay:.3f}s">'
                f'<title>{count} contributions on {date_str}</title></rect>'
            )
            cell_idx += 1
    
    # Legend
    legend_x = SVG_W - 120
    legend_y = SVG_H - 20
    svg_parts.append(f'<text x="{legend_x - 30}" y="{legend_y + 1}" fill="#8b949e" font-size="10">Less</text>')
    for i, color in enumerate(PALETTE):
        x = legend_x + i * (CELL_SIZE + CELL_GAP)
        svg_parts.append(
            f'<rect x="{x}" y="{legend_y - 10}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'fill="{color}" rx="2"/>'
        )
    svg_parts.append(f'<text x="{legend_x + len(PALETTE) * (CELL_SIZE + CELL_GAP) + 6}" y="{legend_y + 1}" fill="#8b949e" font-size="10">More</text>')
    
    # Stats footer
    total = stats.get("total_contributions", 0)
    svg_parts.append(
        f'<text x="{SVG_W // 2}" y="{SVG_H - 2}" text-anchor="middle" fill="#8b949e" font-size="11">'
        f'{total:,} contributions in the last year</text>'
    )
    
    svg_parts.append("</svg>")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"✅ Heatmap SVG written to {output_path}")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"
    render_heatmap(inp, out)
