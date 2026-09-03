#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG.
Usage: python make_info_card.py [output.svg]
"""
import sys
import os

# === CUSTOMIZE YOUR INFO HERE ===
INFO = {
    "user": "Toruk_Makto_Code",
    "role": "Full Stack Developer",
    "stack": "Python | JavaScript | React | Node.js",
    "focus": "AI & Automation",
    "status": "Open to opportunities",
    "location": "Earth 🌎",
}

SVG_W = 490
SVG_H = 280
PADDING = 24

def make_info_card(output_path, static=False):
    lines = [
        ("$ whoami", "#58a6ff", False),
        (f"  {INFO['user']}", "#f0f6fc", True),
        ("", None, False),
        ("$ cat role.txt", "#58a6ff", False),
        (f"  {INFO['role']}", "#7ee787", True),
        ("", None, False),
        ("$ echo $STACK", "#58a6ff", False),
        (f"  {INFO['stack']}", "#d2a8ff", True),
        ("", None, False),
        ("$ cat focus.md", "#58a6ff", False),
        (f"  {INFO['focus']}", "#ff7b72", True),
        ("", None, False),
        ("$ echo $STATUS", "#58a6ff", False),
        (f"  {INFO['status']}", "#ffa657", True),
        ("", None, False),
        ("$ pwd", "#58a6ff", False),
        (f"  {INFO['location']}", "#79c0ff", True),
    ]

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}" height="{SVG_H}">',
        f'<rect width="{SVG_W}" height="{SVG_H}" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1"/>',
        # Title bar
        f'<rect width="{SVG_W}" height="32" rx="12" fill="#21262d"/>',
        f'<rect y="16" width="{SVG_W}" height="16" fill="#21262d"/>',
        '<circle cx="16" cy="16" r="6" fill="#ff5f56"/>',
        '<circle cx="36" cy="16" r="6" fill="#ffbd2e"/>',
        '<circle cx="56" cy="16" r="6" fill="#27c93f"/>',
        f'<text x="{SVG_W // 2}" y="21" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="12">info@terminal ~ $</text>',
        '<style>',
        '  .line { font-family: "Courier New", monospace; font-size: 13px; }',
        '  .prompt { fill: #58a6ff; }',
        '  .value { fill: #f0f6fc; }',
        '  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }',
        '  .reveal { animation: fadeIn 0.4s ease-out forwards; animation-fill-mode: both; opacity: 0; }',
        '</style>',
    ]

    y = 52
    for i, (text, color, is_value) in enumerate(lines):
        if not text:
            y += 6
            continue
        delay = i * 0.12
        cls = "prompt" if not is_value else "value"
        svg_parts.append(
            f'<text class="line reveal {cls}" x="{PADDING}" y="{y}" '
            f'style="animation-delay: {delay:.2f}s" fill="{color}">{escape_xml(text)}</text>'
        )
        y += 18

    svg_parts.append("</svg>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"[OK] Info card SVG written to {output_path}")

def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    static = os.environ.get("STATIC", "0") == "1"
    make_info_card(out, static)
