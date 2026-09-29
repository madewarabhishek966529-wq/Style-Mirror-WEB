"""
Script to crop 5x5 collage sheets into individual style thumbnails.
Reference: stylemirror-docs/03_STYLE_CATALOG.md
"""
import os
import sys
from PIL import Image

def crop_grid(path: str, cols: int, rows: int, top_offset: int, cell_w: int, cell_h: int, out_prefix: str, names: list[str]):
    if not os.path.exists(path):
        print(f"Source sheet not found: {path}")
        return
    im = Image.open(path)
    i = 0
    os.makedirs(os.path.dirname(out_prefix), exist_ok=True)
    for r in range(rows):
        for c in range(cols):
            if i >= len(names):
                break
            box = (c * cell_w, top_offset + r * cell_h, (c + 1) * cell_w, top_offset + (r + 1) * cell_h)
            cropped = im.crop(box)
            out_file = f"{out_prefix}{names[i]}.jpg"
            cropped.save(out_file, quality=92)
            print(f"Saved: {out_file}")
            i += 1

if __name__ == "__main__":
    print("Crop sheet utility ready. Provide collage sheet path and dimensions to crop.")
