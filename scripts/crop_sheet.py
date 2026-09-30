"""
Script to crop 5x5 collage sheets into individual style thumbnails.
Reference: stylemirror-docs/03_STYLE_CATALOG.md
"""
import os
import sys
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
HAIR_DIR = os.path.join(FRONTEND_DIR, "assets", "styles", "hair")
BEARD_DIR = os.path.join(FRONTEND_DIR, "assets", "styles", "beard")
DEMO_DIR = os.path.join(FRONTEND_DIR, "assets", "demos")

HAIR_NAMES = [f"H{i:02d}" for i in range(1, 26)]
BEARD_NAMES = [f"B{i:02d}" for i in range(1, 26)]

def crop_grid(path: str, cols: int, rows: int, out_dir: str, names: list[str], target_size=(360, 360)):
    if not os.path.exists(path):
        print(f"Source sheet not found: {path}")
        return
    im = Image.open(path).convert("RGB")
    w, h = im.size
    cell_w = w / cols
    cell_h = h / rows
    os.makedirs(out_dir, exist_ok=True)

    i = 0
    for r in range(rows):
        for c in range(cols):
            if i >= len(names):
                break
            # Calculate coordinates, trimming subtle border edges
            x0 = int(c * cell_w)
            y0 = int(r * cell_h)
            x1 = int((c + 1) * cell_w)
            y1 = int((r + 1) * cell_h)

            cropped = im.crop((x0, y0, x1, y1))
            resized = cropped.resize(target_size, Image.Resampling.LANCZOS)
            out_file = os.path.join(out_dir, f"{names[i]}.jpg")
            resized.save(out_file, "JPEG", quality=92)
            print(f"Saved: {out_file}")
            i += 1

def run_crop(hair_sheet_path: str, beard_sheet_path: str):
    print("Cropping Hairstyles (25 styles on single base face)...")
    crop_grid(hair_sheet_path, 5, 5, HAIR_DIR, HAIR_NAMES)

    print("Cropping Beard Styles (25 styles on single base face)...")
    crop_grid(beard_sheet_path, 5, 5, BEARD_DIR, BEARD_NAMES)

    # Set Demo Model 1 to the clean-shaven version of this exact same model
    b01_path = os.path.join(BEARD_DIR, "B01.jpg")
    if os.path.exists(b01_path):
        demo1_path = os.path.join(DEMO_DIR, "demo1.jpg")
        os.makedirs(DEMO_DIR, exist_ok=True)
        im = Image.open(b01_path)
        im.resize((640, 640), Image.Resampling.LANCZOS).save(demo1_path, "JPEG", quality=95)
        print(f"Updated Demo Model 1 portrait with base model: {demo1_path}")

if __name__ == "__main__":
    hair_sheet = sys.argv[1] if len(sys.argv) > 1 else ""
    beard_sheet = sys.argv[2] if len(sys.argv) > 2 else ""
    if hair_sheet and beard_sheet:
        run_crop(hair_sheet, beard_sheet)
    else:
        print("Usage: python scripts/crop_sheet.py <hair_sheet.jpg> <beard_sheet.jpg>")

