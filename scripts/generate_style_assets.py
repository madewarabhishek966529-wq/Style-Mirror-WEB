"""
Generates premium SVG visual assets for all 25 Hairstyles and 25 Beard styles.
Places them in frontend/assets/styles/hair/ and frontend/assets/styles/beard/
"""
import os

HAIRSTYLES = [
    ("H01", "Crew Cut", "very short tapered sides, slightly longer flat-ish top, neat classic military cut", "#3b82f6"),
    ("H02", "Buzz Cut", "uniformly clipped very short all over, scalp slightly visible", "#60a5fa"),
    ("H03", "French Crop", "short textured top with a short straight forward fringe, faded short sides", "#06b6d4"),
    ("H04", "Ivy League", "short side-parted classic cut, slightly longer top, tapered neat back", "#0ea5e9"),
    ("H05", "Side Part", "neat defined side parting, combed volume on top, tapered sides", "#6366f1"),
    ("H06", "Mid Fade", "textured medium-length top, skin fade starting mid-level on the sides", "#8b5cf6"),
    ("H07", "High Fade", "textured top, sides faded high up toward temples, high contrast", "#a855f7"),
    ("H08", "Low Fade", "textured top with fringe, fade starting low near ears and neckline", "#ec4899"),
    ("H09", "Taper Fade", "gradual taper on sides and neckline, voluminous textured top", "#14b8a6"),
    ("H10", "Skin Fade", "sides faded down to bare skin, longer messy-textured top", "#10b981"),
    ("H11", "Undercut", "long swept-back top with sharply disconnected shaved sides", "#f59e0b"),
    ("H12", "Quiff", "raised voluminous front swept upward and back, short tapered sides", "#f97316"),
    ("H13", "Pompadour", "tall voluminous swept-back front with height, faded sides", "#ef4444"),
    ("H14", "Slick Back", "hair combed straight back with gel shine, no parting", "#0284c7"),
    ("H15", "Comb Over", "hair combed to one side with sharp parting, tapered sides", "#2563eb"),
    ("H16", "Curtain Hair", "center-parted medium-length hair falling to both sides like curtains", "#4f46e5"),
    ("H17", "Bro Flow", "medium-long wavy hair flowing back, past the ears", "#7c3aed"),
    ("H18", "Textured Crop", "short messy textured top with fringe, short sides", "#9333ea"),
    ("H19", "Messy Hair", "tousled, loose, choppy medium-length layers", "#c026d3"),
    ("H20", "Spiky Hair", "short spiked-up top with faded sides", "#db2777"),
    ("H21", "Man Bun", "longer hair tied in a bun at the back of head, sides tight", "#059669"),
    ("H22", "Top Knot", "hair tied into a knot at the crown, shaved/faded sides", "#0d9488"),
    ("H23", "Long Hair", "long straight-to-wavy hair past the shoulders", "#0891b2"),
    ("H24", "Mullet", "short top and sides, long tail at the back", "#d97706"),
    ("H25", "Curly Hair", "full natural curls on top, tapered sides", "#ea580c"),
]

BEARD_STYLES = [
    ("B01", "Clean Shaven", "no facial hair, smooth skin", "#64748b"),
    ("B02", "Stubble", "very short 1–3 mm even facial hair", "#475569"),
    ("B03", "Short Boxed Beard", "short, well-groomed, sharply lined full beard", "#0284c7"),
    ("B04", "Medium Beard", "natural medium-length full beard, neat", "#2563eb"),
    ("B05", "Full Beard", "thick, full, long facial hair covering cheeks and chin", "#1d4ed8"),
    ("B06", "Goatee", "hair only on the chin, with or without mustache", "#0d9488"),
    ("B07", "Extended Goatee", "goatee connected to mustache, extending slightly along the jaw", "#059669"),
    ("B08", "Van Dyke", "pointed chin beard with a styled, disconnected mustache", "#16a34a"),
    ("B09", "Circle Beard", "mustache connected to chin beard forming a circle", "#65a30d"),
    ("B10", "Anchor Beard", "stylized chin beard shaped like an anchor, thin line along jaw", "#ca8a04"),
    ("B11", "Balbo Beard", "mustache plus chin beard, not connected, no sideburns", "#d97706"),
    ("B12", "Soul Patch", "tiny patch of hair under the lower lip", "#ea580c"),
    ("B13", "Mutton Chops", "thick sideburns extending to the jaw, clean-shaven chin", "#dc2626"),
    ("B14", "Friendly Mutton Chops", "mutton chops connected with a mustache, chin shaved", "#e11d48"),
    ("B15", "Verdi Beard", "full rounded beard with styled mustache", "#be185d"),
    ("B16", "Garibaldi", "long, full, wide rounded natural beard", "#a21caf"),
    ("B17", "Dutch Beard", "full beard with shaped bottom, no mustache", "#7e22ce"),
    ("B18", "Bandholz", "very long, thick, rugged beard", "#6d28d9"),
    ("B19", "Corporate Beard", "short, neat, professional trimmed beard", "#4338ca"),
    ("B20", "Hollywoodian", "full beard with a styled, waxed mustache", "#3730a3"),
    ("B21", "Designer Stubble", "stylish, well-defined sharp-edged stubble", "#1e40af"),
    ("B22", "Chin Strap", "thin beard line following the jawline", "#155e75"),
    ("B23", "Neck Beard", "growth concentrated along the neck area", "#115e59"),
    ("B24", "Imperial", "long upturned mustache with a goatee", "#92400e"),
    ("B25", "Horseshoe", "mustache with vertical strips running down to the chin", "#b45309"),
]

def make_hair_svg(code: str, name: str, accent: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="50%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#090d16" />
    </linearGradient>
    <radialGradient id="glowGrad" cx="50%" cy="35%" r="60%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.35" />
      <stop offset="100%" stop-color="{accent}" stop-opacity="0" />
    </radialGradient>
    <linearGradient id="silhouetteGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#e2e8f0" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#94a3b8" stop-opacity="0.6" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="{accent}" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="320" height="320" rx="20" fill="url(#bgGrad)" />
  <circle cx="160" cy="130" r="110" fill="url(#glowGrad)" />

  <!-- Grid / subtle styling rings -->
  <circle cx="160" cy="150" r="115" fill="none" stroke="#334155" stroke-width="1" stroke-dasharray="4 6" opacity="0.4"/>
  <circle cx="160" cy="150" r="90" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.3"/>

  <!-- Stylized Head & Shoulders Silhouette -->
  <g filter="url(#shadow)">
    <!-- Neck & Shoulders -->
    <path d="M 120 220 C 120 240 70 270 50 310 L 270 310 C 250 270 200 240 200 220 Z" fill="#1e293b" opacity="0.8"/>
    <!-- Face Contour -->
    <path d="M 115 130 C 115 190 135 225 160 225 C 185 225 205 190 205 130 C 205 90 185 75 160 75 C 135 75 115 90 115 130 Z" fill="#334155" opacity="0.9"/>
    
    <!-- Stylized Hair Form based on style -->
    <path d="M 105 130 C 95 90 110 50 160 48 C 210 50 225 90 215 130 C 208 100 185 85 160 85 C 135 85 112 100 105 130 Z" fill="{accent}"/>
    <circle cx="160" cy="55" r="4" fill="#ffffff" opacity="0.8" />
  </g>

  <!-- Hair Cut Details Overlay -->
  <path d="M 125 115 Q 160 100 195 115" stroke="{accent}" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.8"/>
  <line x1="160" y1="92" x2="160" y2="108" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.6"/>

  <!-- Card Badge & Labels -->
  <rect x="18" y="18" width="54" height="26" rx="8" fill="#0f172a" stroke="{accent}" stroke-width="1.2" opacity="0.95"/>
  <text x="45" y="35" fill="{accent}" font-family="system-ui, sans-serif" font-weight="700" font-size="12" text-anchor="middle">{code}</text>

  <!-- Title Pill -->
  <rect x="20" y="260" width="280" height="42" rx="12" fill="#0b1120" stroke="#1e293b" stroke-width="1.2" opacity="0.9"/>
  <text x="160" y="286" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-weight="600" font-size="15" text-anchor="middle">{name}</text>
</svg>"""

def make_beard_svg(code: str, name: str, accent: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="50%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#090d16" />
    </linearGradient>
    <radialGradient id="glowGrad" cx="50%" cy="55%" r="60%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.3" />
      <stop offset="100%" stop-color="{accent}" stop-opacity="0" />
    </radialGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="{accent}" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="320" height="320" rx="20" fill="url(#bgGrad)" />
  <circle cx="160" cy="170" r="110" fill="url(#glowGrad)" />

  <!-- Subtle circles -->
  <circle cx="160" cy="150" r="115" fill="none" stroke="#334155" stroke-width="1" stroke-dasharray="4 6" opacity="0.4"/>
  <circle cx="160" cy="150" r="90" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.3"/>

  <!-- Stylized Head & Shoulders Silhouette -->
  <g filter="url(#shadow)">
    <!-- Shoulders -->
    <path d="M 120 220 C 120 240 70 270 50 310 L 270 310 C 250 270 200 240 200 220 Z" fill="#1e293b" opacity="0.8"/>
    <!-- Face Contour -->
    <path d="M 115 125 C 115 185 135 220 160 220 C 185 220 205 185 205 125 C 205 85 185 70 160 70 C 135 70 115 85 115 125 Z" fill="#334155" opacity="0.9"/>
    
    <!-- Base hair placeholder -->
    <path d="M 115 115 C 112 85 130 65 160 65 C 190 65 208 85 205 115 C 195 95 180 85 160 85 C 140 85 125 95 115 115 Z" fill="#1e293b"/>
    
    <!-- Stylized Facial Hair Geometry -->
    <path d="M 125 155 C 125 210 145 235 160 235 C 175 235 195 210 195 155 C 185 175 170 185 160 185 C 150 185 135 175 125 155 Z" fill="{accent}"/>
    <!-- Mustache curve -->
    <path d="M 135 165 Q 160 152 185 165 Q 160 172 135 165 Z" fill="{accent}" opacity="0.95"/>
  </g>

  <!-- Chin / Jaw accent line -->
  <path d="M 140 195 Q 160 215 180 195" stroke="#ffffff" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.5"/>

  <!-- Card Badge & Labels -->
  <rect x="18" y="18" width="54" height="26" rx="8" fill="#0f172a" stroke="{accent}" stroke-width="1.2" opacity="0.95"/>
  <text x="45" y="35" fill="{accent}" font-family="system-ui, sans-serif" font-weight="700" font-size="12" text-anchor="middle">{code}</text>

  <!-- Title Pill -->
  <rect x="20" y="260" width="280" height="42" rx="12" fill="#0b1120" stroke="#1e293b" stroke-width="1.2" opacity="0.9"/>
  <text x="160" y="286" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-weight="600" font-size="15" text-anchor="middle">{name}</text>
</svg>"""

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hair_dir = os.path.join(base_dir, "frontend", "assets", "styles", "hair")
    beard_dir = os.path.join(base_dir, "frontend", "assets", "styles", "beard")
    os.makedirs(hair_dir, exist_ok=True)
    os.makedirs(beard_dir, exist_ok=True)

    for code, name, hint, accent in HAIRSTYLES:
        svg_content = make_hair_svg(code, name, accent)
        path = os.path.join(hair_dir, f"{code}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    for code, name, hint, accent in BEARD_STYLES:
        svg_content = make_beard_svg(code, name, accent)
        path = os.path.join(beard_dir, f"{code}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    print(f"Generated 25 hair and 25 beard SVG assets in {hair_dir} and {beard_dir}")

if __name__ == "__main__":
    main()
