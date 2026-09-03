#!/usr/bin/env python3
"""Convert SVG files to PNG using Playwright - navigate directly to SVG file."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import base64

def svg_to_png(svg_file, png_file, scale=2):
    svg_path = Path(svg_file).resolve()
    png_path = Path(png_file).resolve()
    
    # Read SVG content
    svg_content = svg_path.read_text(encoding='utf-8')
    
    # Create a data URI
    svg_b64 = base64.b64encode(svg_content.encode('utf-8')).decode('ascii')
    data_uri = f"data:image/svg+xml;base64,{svg_b64}"
    
    # HTML that displays the SVG at full size
    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0d1117;">
<img src="{data_uri}" style="display:block;">
</body>
</html>'''
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=scale)
        page.set_content(html, wait_until="networkidle")
        page.wait_for_timeout(2000)
        
        # Get actual rendered size
        size = page.evaluate("() => { const img = document.querySelector('img'); return {w: img.naturalWidth, h: img.naturalHeight} }")
        print(f"[INFO] Image size: {size['w']}x{size['h']}")
        
        page.set_viewport_size({"width": size['w'], "height": size['h']})
        page.wait_for_timeout(500)
        
        page.locator("img").screenshot(path=str(png_path))
        browser.close()
    
    size_kb = os.path.getsize(png_path) / 1024
    print(f"[OK] {png_file} ({size_kb:.0f} KB)")

if __name__ == "__main__":
    svg_to_png("dark_mode.svg", "dark_mode.png", scale=2)
    svg_to_png("contributions.svg", "contributions.png", scale=2)
    print("[DONE] Both PNGs generated")
