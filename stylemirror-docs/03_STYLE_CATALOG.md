# 03 — Style Catalog

Seed these into the `styles` table (`scripts/seed_styles.py`). `prompt_hint` is injected into AI prompts.

## Hairstyles (25)
| ID | Name | prompt_hint |
|---|---|---|
| H01 | Crew Cut | very short tapered sides, slightly longer flat-ish top, neat classic military cut |
| H02 | Buzz Cut | uniformly clipped very short all over, scalp slightly visible |
| H03 | French Crop | short textured top with a short straight forward fringe, faded short sides |
| H04 | Ivy League | short side-parted classic cut, slightly longer top, tapered neat back |
| H05 | Side Part | neat defined side parting, combed volume on top, tapered sides |
| H06 | Mid Fade | textured medium-length top, skin fade starting mid-level on the sides |
| H07 | High Fade | textured top, sides faded high up toward temples, high contrast |
| H08 | Low Fade | textured top with fringe, fade starting low near ears and neckline |
| H09 | Taper Fade | gradual taper on sides and neckline, voluminous textured top |
| H10 | Skin Fade | sides faded down to bare skin, longer messy-textured top |
| H11 | Undercut | long swept-back top with sharply disconnected shaved sides |
| H12 | Quiff | raised voluminous front swept upward and back, short tapered sides |
| H13 | Pompadour | tall voluminous swept-back front with height, faded sides |
| H14 | Slick Back | hair combed straight back with gel shine, no parting |
| H15 | Comb Over | hair combed to one side with sharp parting, tapered sides |
| H16 | Curtain Hair | center-parted medium-length hair falling to both sides like curtains |
| H17 | Bro Flow | medium-long wavy hair flowing back, past the ears |
| H18 | Textured Crop | short messy textured top with fringe, short sides |
| H19 | Messy Hair | tousled, loose, choppy medium-length layers |
| H20 | Spiky Hair | short spiked-up top with faded sides |
| H21 | Man Bun | longer hair tied in a bun at the back of head, sides tight |
| H22 | Top Knot | hair tied into a knot at the crown, shaved/faded sides |
| H23 | Long Hair | long straight-to-wavy hair past the shoulders |
| H24 | Mullet | short top and sides, long tail at the back |
| H25 | Curly Hair | full natural curls on top, tapered sides |

## Beards (25)
| ID | Name | prompt_hint |
|---|---|---|
| B01 | Clean Shaven | no facial hair, smooth skin |
| B02 | Stubble | very short 1–3 mm even facial hair |
| B03 | Short Boxed Beard | short, well-groomed, sharply lined full beard |
| B04 | Medium Beard | natural medium-length full beard, neat |
| B05 | Full Beard | thick, full, long facial hair covering cheeks and chin |
| B06 | Goatee | hair only on the chin, with or without mustache |
| B07 | Extended Goatee | goatee connected to mustache, extending slightly along the jaw |
| B08 | Van Dyke | pointed chin beard with a styled, disconnected mustache |
| B09 | Circle Beard | mustache connected to chin beard forming a circle |
| B10 | Anchor Beard | stylized chin beard shaped like an anchor, thin line along jaw |
| B11 | Balbo Beard | mustache plus chin beard, not connected, no sideburns |
| B12 | Soul Patch | tiny patch of hair under the lower lip |
| B13 | Mutton Chops | thick sideburns extending to the jaw, clean-shaven chin |
| B14 | Friendly Mutton Chops | mutton chops connected with a mustache, chin shaved |
| B15 | Verdi Beard | full rounded beard with styled mustache |
| B16 | Garibaldi | long, full, wide rounded natural beard |
| B17 | Dutch Beard | full beard with shaped bottom, no mustache |
| B18 | Bandholz | very long, thick, rugged beard |
| B19 | Corporate Beard | short, neat, professional trimmed beard |
| B20 | Hollywoodian | full beard with a styled, waxed mustache |
| B21 | Designer Stubble | stylish, well-defined sharp-edged stubble |
| B22 | Chin Strap | thin beard line following the jawline |
| B23 | Neck Beard | growth concentrated along the neck area |
| B24 | Imperial | long upturned mustache with a goatee |
| B25 | Horseshoe | mustache with vertical strips running down to the chin |

## Preparing Reference Images
The two uploaded sheets are collages. Crop each cell:

- Hair sheet: 5 cols × 5 rows; each cell = front / side / back thirds.
- Beard sheet: 5 cols × 5 rows; each cell = front / side halves.
- Output: `assets/styles/hair/H01_front.jpg`, `H01_side.jpg`, `H01_back.jpg`, `assets/styles/beard/B01_front.jpg`, `B01_side.jpg`.

```python
# scripts/crop_sheet.py
from PIL import Image

def crop_grid(path, cols, rows, top_offset, cell_w, cell_h, out_prefix, names):
    im = Image.open(path)
    i = 0
    for r in range(rows):
        for c in range(cols):
            box = (c*cell_w, top_offset + r*cell_h, (c+1)*cell_w, top_offset + (r+1)*cell_h)
            im.crop(box).save(f"{out_prefix}{names[i]}.jpg", quality=92)
            i += 1
```
Tune offsets manually per sheet, then split each cell into its front/side/back parts.

## Usage
1. **UI thumbnails** — use the front crop.
2. **AI reference (optional)** — prefer text `prompt_hint`; reference-only prompts tend to copy the reference person's face.
3. Sheets are AI-generated: check the generating tool's license before commercial use, or regenerate your own catalog.
