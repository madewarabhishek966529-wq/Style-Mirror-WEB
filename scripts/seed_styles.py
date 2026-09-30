"""
Database seeder for StyleMirror style catalog.
Seeds 25 hairstyles and 25 beard styles into the SQLite database.
Reference: stylemirror-docs/03_STYLE_CATALOG.md, 06_DATABASE.md
"""
import os
import sys
from pathlib import Path

# Add backend directory to sys.path so we can import app modules if available
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

HAIRSTYLES = [
    ("H01", "Crew Cut", "very short tapered sides, slightly longer flat-ish top, neat classic military cut"),
    ("H02", "Buzz Cut", "uniformly clipped very short all over, scalp slightly visible"),
    ("H03", "French Crop", "short textured top with a short straight forward fringe, faded short sides"),
    ("H04", "Ivy League", "short side-parted classic cut, slightly longer top, tapered neat back"),
    ("H05", "Side Part", "neat defined side parting, combed volume on top, tapered sides"),
    ("H06", "Mid Fade", "textured medium-length top, skin fade starting mid-level on the sides"),
    ("H07", "High Fade", "textured top, sides faded high up toward temples, high contrast"),
    ("H08", "Low Fade", "textured top with fringe, fade starting low near ears and neckline"),
    ("H09", "Taper Fade", "gradual taper on sides and neckline, voluminous textured top"),
    ("H10", "Skin Fade", "sides faded down to bare skin, longer messy-textured top"),
    ("H11", "Undercut", "long swept-back top with sharply disconnected shaved sides"),
    ("H12", "Quiff", "raised voluminous front swept upward and back, short tapered sides"),
    ("H13", "Pompadour", "tall voluminous swept-back front with height, faded sides"),
    ("H14", "Slick Back", "hair combed straight back with gel shine, no parting"),
    ("H15", "Comb Over", "hair combed to one side with sharp parting, tapered sides"),
    ("H16", "Curtain Hair", "center-parted medium-length hair falling to both sides like curtains"),
    ("H17", "Bro Flow", "medium-long wavy hair flowing back, past the ears"),
    ("H18", "Textured Crop", "short messy textured top with fringe, short sides"),
    ("H19", "Messy Hair", "tousled, loose, choppy medium-length layers"),
    ("H20", "Spiky Hair", "short spiked-up top with faded sides"),
    ("H21", "Man Bun", "longer hair tied in a bun at the back of head, sides tight"),
    ("H22", "Top Knot", "hair tied into a knot at the crown, shaved/faded sides"),
    ("H23", "Long Hair", "long straight-to-wavy hair past the shoulders"),
    ("H24", "Mullet", "short top and sides, long tail at the back"),
    ("H25", "Curly Hair", "full natural curls on top, tapered sides"),
]

BEARDS = [
    ("B01", "Clean Shaven", "no facial hair, smooth skin"),
    ("B02", "Stubble", "very short 1–3 mm even facial hair"),
    ("B03", "Short Boxed Beard", "short, well-groomed, sharply lined full beard"),
    ("B04", "Medium Beard", "natural medium-length full beard, neat"),
    ("B05", "Full Beard", "thick, full, long facial hair covering cheeks and chin"),
    ("B06", "Goatee", "hair only on the chin, with or without mustache"),
    ("B07", "Extended Goatee", "goatee connected to mustache, extending slightly along the jaw"),
    ("B08", "Van Dyke", "pointed chin beard with a styled, disconnected mustache"),
    ("B09", "Circle Beard", "mustache connected to chin beard forming a circle"),
    ("B10", "Anchor Beard", "stylized chin beard shaped like an anchor, thin line along jaw"),
    ("B11", "Balbo Beard", "mustache plus chin beard, not connected, no sideburns"),
    ("B12", "Soul Patch", "tiny patch of hair under the lower lip"),
    ("B13", "Mutton Chops", "thick sideburns extending to the jaw, clean-shaven chin"),
    ("B14", "Friendly Mutton Chops", "mutton chops connected with a mustache, chin shaved"),
    ("B15", "Verdi Beard", "full rounded beard with styled mustache"),
    ("B16", "Garibaldi", "long, full, wide rounded natural beard"),
    ("B17", "Dutch Beard", "full beard with shaped bottom, no mustache"),
    ("B18", "Bandholz", "very long, thick, rugged beard"),
    ("B19", "Corporate Beard", "short, neat, professional trimmed beard"),
    ("B20", "Hollywoodian", "full beard with a styled, waxed mustache"),
    ("B21", "Designer Stubble", "stylish, well-defined sharp-edged stubble"),
    ("B22", "Chin Strap", "thin beard line following the jawline"),
    ("B23", "Neck Beard", "growth concentrated along the neck area"),
    ("B24", "Imperial", "long upturned mustache with a goatee"),
    ("B25", "Horseshoe", "mustache with vertical strips running down to the chin"),
]

def seed(db_path: str = None):
    try:
        from app.db import SessionLocal, engine, Base
        from app.models import Style
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        count = 0
        for idx, (code, name, hint) in enumerate(HAIRSTYLES, start=1):
            thumb = f"/assets/styles/hair/{code}.jpg"
            existing = db.query(Style).filter(Style.id == code).first()
            if existing:
                existing.name = name
                existing.prompt_hint = hint
                existing.thumb_url = thumb
                existing.sort_order = idx
            else:
                s = Style(
                    id=code,
                    type="hair",
                    name=name,
                    prompt_hint=hint,
                    thumb_url=thumb,
                    sort_order=idx,
                    is_active=True,
                )
                db.add(s)
            count += 1

        for idx, (code, name, hint) in enumerate(BEARDS, start=1):
            thumb = f"/assets/styles/beard/{code}.jpg"
            existing = db.query(Style).filter(Style.id == code).first()
            if existing:
                existing.name = name
                existing.prompt_hint = hint
                existing.thumb_url = thumb
                existing.sort_order = idx
            else:
                s = Style(
                    id=code,
                    type="beard",
                    name=name,
                    prompt_hint=hint,
                    thumb_url=thumb,
                    sort_order=idx,
                    is_active=True,
                )
                db.add(s)
            count += 1

        db.commit()
        db.close()
        print(f"Successfully seeded {count} styles into the database.")
    except ImportError:
        # Fallback to direct sqlite3 if app not yet importable
        import sqlite3
        if db_path is None:
            db_path = str(BACKEND_DIR / "stylemirror.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS styles (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                prompt_hint TEXT NOT NULL,
                thumb_url TEXT NOT NULL,
                ref_front_url TEXT,
                ref_side_url TEXT,
                ref_back_url TEXT,
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        for idx, (code, name, hint) in enumerate(HAIRSTYLES, start=1):
            thumb = f"/assets/styles/hair/{code}.jpg"
            cur.execute("""
                INSERT INTO styles (id, type, name, prompt_hint, thumb_url, sort_order, is_active)
                VALUES (?, 'hair', ?, ?, ?, ?, 1)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    prompt_hint=excluded.prompt_hint,
                    thumb_url=excluded.thumb_url,
                    sort_order=excluded.sort_order
            """, (code, name, hint, thumb, idx))

        for idx, (code, name, hint) in enumerate(BEARDS, start=1):
            thumb = f"/assets/styles/beard/{code}.jpg"
            cur.execute("""
                INSERT INTO styles (id, type, name, prompt_hint, thumb_url, sort_order, is_active)
                VALUES (?, 'beard', ?, ?, ?, ?, 1)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    prompt_hint=excluded.prompt_hint,
                    thumb_url=excluded.thumb_url,
                    sort_order=excluded.sort_order
            """, (code, name, hint, thumb, idx))

        conn.commit()
        conn.close()
        print(f"Direct SQLite seed finished. Seeded 50 styles into {db_path}.")

if __name__ == "__main__":
    seed()
