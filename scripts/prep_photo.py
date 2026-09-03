#!/usr/bin/env python3
"""
Prepare a photo for ASCII art conversion.
- Removes background with rembg
- Boosts contrast with CLAHE
- Composites onto white background
Usage: python prep_photo.py source-photo.jpg
"""
import sys
import numpy as np
from PIL import Image

def prep_photo(input_path, output_path="source-prepped.png"):
    try:
        import cv2
        from rembg import remove
    except ImportError:
        print("❌ Missing dependencies. Install with:")
        print("   pip install opencv-python rembg pillow numpy")
        sys.exit(1)
    
    print(f"📸 Processing {input_path}...")
    
    # Step 1: Remove background
    print("  🔄 Removing background...")
    with open(input_path, "rb") as f:
        input_data = f.read()
    output_data = remove(input_data)
    
    # Save temporary
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(output_data)
        tmp_path = tmp.name
    
    # Step 2: Load and convert to grayscale
    img = cv2.imread(tmp_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Step 3: Apply CLAHE for local contrast enhancement
    print("  🎨 Enhancing contrast...")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Step 4: Composite onto white background
    # Load alpha channel from rembg output
    rgba = cv2.imread(tmp_path, cv2.IMREAD_UNCHANGED)
    alpha = rgba[:, :, 3] / 255.0
    
    # Create white background
    white = np.ones_like(enhanced) * 255
    
    # Composite: alpha * enhanced + (1-alpha) * white
    result = (alpha * enhanced + (1 - alpha) * white).astype(np.uint8)
    
    # Save
    cv2.imwrite(output_path, result)
    
    # Cleanup
    import os
    os.unlink(tmp_path)
    
    print(f"✅ Prepped photo saved to {output_path}")
    print("   Now run: python make_ascii_svg.py")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <source-photo.jpg>")
        print("Example: python prep_photo.py my-photo.jpg")
        sys.exit(1)
    prep_photo(sys.argv[1])
