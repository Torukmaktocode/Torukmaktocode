#!/usr/bin/env python3
"""
Convert a prepped photo into a self-typing monochrome ASCII art SVG.
Usage: python make_ascii_svg.py [source-prepped.png] [output.svg]
"""
import sys
import numpy as np
from PIL import Image

# ASCII density ramp: bright (sparse) -> dark (dense)
RAMP = " .`:-=+*cs#%@"
WIDTH = 100  # characters wide
CHAR_W = 9  # px per character
CHAR_H = 16  # px per character (monospace aspect)

def brightness_to_char(b):
    """Map 0-255 brightness to ASCII character."""
    idx = int((1 - b / 255) * (len(RAMP) - 1))
    return RAMP[max(0, min(idx, len(RAMP) - 1))]

def make_ascii_svg(input_path, output_path):
    # Load and resize
    img = Image.open(input_path).convert("L")
    aspect = img.height / img.width
    height = int(WIDTH * aspect * 0.55)  # compensate for character aspect
    img = img.resize((WIDTH, height), Image.LANCZOS)
    pixels = np.array(img)

    # Build character grid
    rows = []
    for y in range(pixels.shape[0]):
        row = ""
        for x in range(pixels.shape[1]):
            ch = brightness_to_char(pixels[y, x])
            row += ch
        rows.append(row)

    svg_w = WIDTH * CHAR_W
    svg_h = height * CHAR_H

    # Build SVG with staggered row animations
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">',
        f'<rect width="{svg_w}" height="{svg_h}" fill="#0d1117"/>',
        '<style>',
        '  text { font-family: "Courier New", monospace; font-size: 14px; fill: #8b949e; }',
        '  @keyframes typeRow {',
        '    from { clip-path: inset(0 100% 0 0); }',
        '    to { clip-path: inset(0 0% 0 0); }',
        '  }',
        '  .row { animation: typeRow 0.3s ease-out forwards; animation-fill-mode: both; }',
        '</style>',
    ]

    for i, row in enumerate(rows):
        delay = i * 0.05  # stagger
        svg_parts.append(
            f'<text class="row" x="0" y="{(i + 1) * CHAR_H}" '
            f'style="animation-delay: {delay:.2f}s">{escape_xml(row)}</text>'
        )

    svg_parts.append("</svg>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"[OK] ASCII SVG written to {output_path}")

def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "ascii-art.svg"
    make_ascii_svg(inp, out)
