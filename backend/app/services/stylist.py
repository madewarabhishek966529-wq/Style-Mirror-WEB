"""
StyleMirror Stylist Transformation Engine
High-fidelity hair and beard virtual try-on engine.
Preserves user facial identity, expression, skin tone, clothing, and background
while cleanly applying chosen hairstyles (H01-H25) and beard styles (B01-B25).
"""

import io
import os
import logging
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# Pre-tuned face coordinates for hair styles (H01-H25) in 360x360 catalog
HAIR_FACE_COORDS = {
    "H01": (82, 71, 197, 197),
    "H02": (87, 78, 188, 188),
    "H03": (87, 80, 190, 190),
    "H04": (82, 71, 197, 197),
    "H05": (92, 81, 185, 185),
    "H06": (88, 85, 186, 186),
    "H07": (90, 86, 182, 182),
    "H08": (91, 87, 185, 185),
    "H09": (91, 88, 188, 188),
    "H10": (89, 85, 192, 192),
    "H11": (86, 89, 187, 187),
    "H12": (92, 90, 180, 180),
    "H13": (92, 90, 181, 181),
    "H14": (97, 92, 175, 175),
    "H15": (92, 90, 186, 186),
    "H16": (90, 88, 184, 184),
    "H17": (89, 88, 183, 183),
    "H18": (91, 86, 184, 184),
    "H19": (93, 88, 181, 181),
    "H20": (89, 82, 193, 193),
    "H21": (85, 85, 186, 186),
    "H22": (86, 87, 183, 183),
    "H23": (85, 85, 185, 185),
    "H24": (95, 86, 179, 179),
    "H25": (87, 85, 186, 186),
}

# Pre-tuned face coordinates for beard styles (B01-B25) in 360x360 catalog
BEARD_FACE_COORDS = {
    "B01": (64, 91, 240, 240),
    "B02": (66, 94, 235, 235),
    "B03": (66, 94, 234, 234),
    "B04": (66, 95, 233, 233),
    "B05": (66, 94, 233, 233),
    "B06": (65, 89, 239, 239),
    "B07": (61, 88, 242, 242),
    "B08": (63, 86, 243, 243),
    "B09": (61, 88, 242, 242),
    "B10": (61, 87, 243, 243),
    "B11": (57, 68, 254, 254),
    "B12": (58, 69, 251, 251),
    "B13": (57, 68, 256, 256),
    "B14": (58, 70, 249, 249),
    "B15": (56, 68, 255, 255),
    "B16": (50, 33, 268, 268),
    "B17": (47, 31, 273, 273),
    "B18": (51, 35, 265, 265),
    "B19": (50, 33, 267, 267),
    "B20": (55, 36, 254, 254),
    "B21": (57, 23, 255, 255),
    "B22": (58, 23, 251, 251),
    "B23": (53, 22, 261, 261),
    "B24": (56, 22, 256, 256),
    "B25": (56, 22, 257, 257),
}

def _resolve_asset_dirs() -> Tuple[Path, Path]:
    """Finds hairstyles and beards directory across repository structures."""
    curr = Path(__file__).resolve()
    candidates = [
        curr.parents[3] / "frontend" / "assets" / "styles",
        curr.parents[2] / "frontend" / "assets" / "styles",
        Path.cwd() / "frontend" / "assets" / "styles",
        Path.cwd().parent / "frontend" / "assets" / "styles",
    ]
    for c in candidates:
        if (c / "hair").exists() and (c / "beard").exists():
            return c / "hair", c / "beard"
    # Fallback to standard relative path
    default_base = curr.parents[3] / "frontend" / "assets" / "styles"
    return default_base / "hair", default_base / "beard"

HAIR_DIR, BEARD_DIR = _resolve_asset_dirs()

def _get_cascade() -> cv2.CascadeClassifier:
    cascade_dir = getattr(cv2, "data", None) and getattr(cv2.data, "haarcascades", "")
    xml_path = os.path.join(cascade_dir, "haarcascade_frontalface_default.xml")
    if not os.path.exists(xml_path):
        xml_path = "haarcascade_frontalface_default.xml"
    return cv2.CascadeClassifier(xml_path)

FACE_CASCADE = _get_cascade()

def get_primary_face_box(bgr_img: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """Detects primary frontal human face box (x, y, w, h)."""
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(80, 80))
    if len(faces) == 0:
        # Slightly more relaxed second pass
        faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.06, minNeighbors=3, minSize=(60, 60))
    if len(faces) == 0:
        return None
    # Pick largest face
    fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    return int(fx), int(fy), int(fw), int(fh)

def apply_hairstyle_overlay(
    canvas: np.ndarray,
    u_face: Tuple[int, int, int, int],
    hair_style_id: str
) -> np.ndarray:
    """Extracts and composites hairstyle onto canvas with zero rectangular backdrop artifacts."""
    clean_id = (hair_style_id or "").upper().strip()
    if not clean_id or clean_id in ("H00", "NONE"):
        return canvas

    hair_file = HAIR_DIR / f"{clean_id}.jpg"
    if not hair_file.exists():
        logger.warning(f"Hairstyle file not found: {hair_file}")
        return canvas

    h_img = cv2.imread(str(hair_file))
    if h_img is None:
        return canvas

    hh, hw = h_img.shape[:2]
    u_h, u_w = canvas.shape[:2]
    ufx, ufy, ufw, ufh = u_face

    # Get style face coordinates
    h_face = HAIR_FACE_COORDS.get(clean_id)
    if not h_face:
        h_face = get_primary_face_box(h_img)
    if not h_face:
        h_face = (int(hw * 0.25), int(hh * 0.25), int(hw * 0.5), int(hh * 0.5))
    hfx, hfy, hfw, hfh = h_face

    # Build anatomical hair dome ellipse (eliminates background boxes)
    center = (int(hfx + hfw * 0.5), int(hfy - 0.04 * hfh))
    axes = (int(hfw * 0.52), int(hfh * 0.40))
    ellipse_mask = np.zeros((hh, hw), dtype=np.uint8)
    cv2.ellipse(ellipse_mask, center, axes, 0, 0, 360, 255, -1)
    forehead_y = int(hfy + 0.28 * hfh)
    ellipse_mask[forehead_y:, :] = 0
    ellipse_mask[:12, :] = 0

    # GrabCut mask initialization
    gc_mask = np.zeros((hh, hw), dtype=np.uint8)
    gc_mask[:] = cv2.GC_BGD
    gc_mask[ellipse_mask == 255] = cv2.GC_PR_FGD

    # Hair core: definite foreground
    core = np.zeros((hh, hw), dtype=np.uint8)
    cv2.ellipse(core, (center[0], int(hfy - 0.08 * hfh)), (int(hfw * 0.32), int(hfh * 0.22)), 0, 0, 360, 255, -1)
    gc_mask[core == 255] = cv2.GC_FGD

    # Studio backdrop detection: flat texture + corner backdrop color
    bg_sample = np.concatenate([h_img[12:28, 12:28], h_img[12:28, -28:-12]], axis=0)
    bg_mean = np.mean(bg_sample, axis=(0, 1))
    color_dist = np.linalg.norm(h_img.astype(float) - bg_mean, axis=2)

    h_gray = cv2.cvtColor(h_img, cv2.COLOR_BGR2GRAY)
    gx = cv2.Sobel(h_gray, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(h_gray, cv2.CV_32F, 0, 1)
    grad = cv2.magnitude(gx, gy)
    flat_bg = (grad < 7.0) & (color_dist < 20.0)
    gc_mask[flat_bg & (gc_mask != cv2.GC_FGD)] = cv2.GC_BGD

    try:
        bgd = np.zeros((1, 65), np.float64)
        fgd = np.zeros((1, 65), np.float64)
        cv2.grabCut(h_img, gc_mask, None, bgd, fgd, 4, cv2.GC_INIT_WITH_MASK)
        h_alpha = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 1.0, 0.0).astype(np.float32)
    except Exception:
        h_alpha = (ellipse_mask.astype(np.float32) / 255.0)

    # Smooth feathering into forehead boundary
    fade_len = 16
    for i in range(fade_len):
        y = forehead_y - fade_len + i
        if 0 <= y < hh:
            h_alpha[y, :] *= (1.0 - (i / float(fade_len)))
    h_alpha = cv2.GaussianBlur(h_alpha, (5, 5), 0)

    # Target placement on user photo
    scale_h = ufw / float(hfw)
    act_y, act_x = np.where(h_alpha > 0.02)
    if len(act_y) == 0 or len(act_x) == 0:
        return canvas

    y1, y2 = act_y.min(), act_y.max() + 1
    x1, x2 = act_x.min(), act_x.max() + 1

    patch = h_img[y1:y2, x1:x2]
    alpha_p = h_alpha[y1:y2, x1:x2]

    sw = max(1, int((x2 - x1) * scale_h))
    sh = max(1, int((y2 - y1) * scale_h))
    patch_res = cv2.resize(patch, (sw, sh), interpolation=cv2.INTER_LANCZOS4)
    alpha_res = cv2.resize(alpha_p, (sw, sh), interpolation=cv2.INTER_LINEAR)[:, :, np.newaxis]

    tx = int(ufx + (x1 - hfx) * scale_h)
    ty = int(ufy + (y1 - hfy) * scale_h)

    dx1, dy1 = max(0, tx), max(0, ty)
    dx2, dy2 = min(u_w, tx + sw), min(u_h, ty + sh)
    sx1, sy1 = max(0, -tx), max(0, -ty)
    sx2, sy2 = sx1 + (dx2 - dx1), sy1 + (dy2 - dy1)

    if dx2 > dx1 and dy2 > dy1:
        rp = patch_res[sy1:sy2, sx1:sx2].astype(np.float32)
        ra = alpha_res[sy1:sy2, sx1:sx2]
        r_roi = canvas[dy1:dy2, dx1:dx2].astype(np.float32)
        canvas[dy1:dy2, dx1:dx2] = np.clip(r_roi * (1.0 - ra) + rp * ra, 0, 255).astype(np.uint8)

    return canvas

def apply_beard_overlay(
    canvas: np.ndarray,
    u_face: Tuple[int, int, int, int],
    beard_style_id: str
) -> np.ndarray:
    """Extracts and composites beard style onto canvas with zero rectangular backdrop artifacts."""
    clean_id = (beard_style_id or "").upper().strip()
    if not clean_id or clean_id in ("B00", "NONE"):
        return canvas

    u_h, u_w = canvas.shape[:2]
    ufx, ufy, ufw, ufh = u_face

    # B01: Clean Shaven -> bilateral filter smoothing on jawline
    if clean_id == "B01":
        jy1 = min(u_h, int(ufy + 0.58 * ufh))
        jy2 = min(u_h, int(ufy + 1.15 * ufh))
        jx1 = max(0, int(ufx + 0.12 * ufw))
        jx2 = min(u_w, int(ufx + 0.88 * ufw))
        jaw_roi = canvas[jy1:jy2, jx1:jx2]
        if jaw_roi.size > 0:
            smoothed = cv2.bilateralFilter(jaw_roi, d=9, sigmaColor=75, sigmaSpace=75)
            mask_jaw = np.zeros((jy2 - jy1, jx2 - jx1), dtype=np.float32)
            cv2.ellipse(
                mask_jaw,
                ((jx2 - jx1) // 2, (jy2 - jy1) // 2),
                ((jx2 - jx1) // 2 - 12, (jy2 - jy1) // 2 - 12),
                0, 0, 360, 1.0, -1
            )
            mask_jaw = cv2.GaussianBlur(mask_jaw, (17, 17), 0)[:, :, np.newaxis]
            canvas[jy1:jy2, jx1:jx2] = (jaw_roi * (1.0 - mask_jaw) + smoothed * mask_jaw).astype(np.uint8)
        return canvas

    beard_file = BEARD_DIR / f"{clean_id}.jpg"
    b01_file = BEARD_DIR / "B01.jpg"
    if not beard_file.exists() or not b01_file.exists():
        logger.warning(f"Beard asset file not found: {beard_file}")
        return canvas

    b_img = cv2.imread(str(beard_file))
    b01 = cv2.imread(str(b01_file))
    if b_img is None or b01 is None:
        return canvas

    bh, bw = b_img.shape[:2]
    bfx, bfy, bfw, bfh = BEARD_FACE_COORDS.get(clean_id, (64, 91, 240, 240))

    # Align clean template B01 if row was shifted in grid
    shift_y = bfy - 91
    if abs(shift_y) > 5:
        M = np.float32([[1, 0, 0], [0, 1, shift_y]])
        b01_ref = cv2.warpAffine(b01, M, (bw, bh), borderMode=cv2.BORDER_REFLECT)
    else:
        b01_ref = b01

    # Differential facial hair extraction
    diff = np.max(np.abs(b_img.astype(float) - b01_ref.astype(float)), axis=2)
    # Mask out upper face (eyes/forehead) and borders
    diff[:int(bfy + 0.58 * bfh), :] = 0
    diff[:, :14] = 0
    diff[:, -14:] = 0
    diff[325:, 320:] = 0  # number watermark
    diff[350:, :] = 0

    mask = np.clip((diff - 10.0) / 28.0, 0.0, 1.0)
    for y in range(320, min(bh, 350)):
        mask[y, :] *= (1.0 - ((y - 320) / 30.0))
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    scale_b = ufw / float(bfw)
    act_y, act_x = np.where(mask > 0.02)
    if len(act_y) == 0 or len(act_x) == 0:
        return canvas

    y1, y2 = act_y.min(), act_y.max() + 1
    x1, x2 = act_x.min(), act_x.max() + 1

    patch = b_img[y1:y2, x1:x2]
    alpha_p = mask[y1:y2, x1:x2]

    sw = max(1, int((x2 - x1) * scale_b))
    sh = max(1, int((y2 - y1) * scale_b))
    patch_res = cv2.resize(patch, (sw, sh), interpolation=cv2.INTER_LANCZOS4)
    alpha_res = cv2.resize(alpha_p, (sw, sh), interpolation=cv2.INTER_LINEAR)[:, :, np.newaxis]

    tx = int(ufx + (x1 - bfx) * scale_b)
    ty = int(ufy + (y1 - bfy) * scale_b)

    dx1, dy1 = max(0, tx), max(0, ty)
    dx2, dy2 = min(u_w, tx + sw), min(u_h, ty + sh)
    sx1, sy1 = max(0, -tx), max(0, -ty)
    sx2, sy2 = sx1 + (dx2 - dx1), sy1 + (dy2 - dy1)

    if dx2 > dx1 and dy2 > dy1:
        rp = patch_res[sy1:sy2, sx1:sx2].astype(np.float32)
        ra = alpha_res[sy1:sy2, sx1:sx2]
        r_roi = canvas[dy1:dy2, dx1:dx2].astype(np.float32)
        canvas[dy1:dy2, dx1:dx2] = np.clip(r_roi * (1.0 - ra) + rp * ra, 0, 255).astype(np.uint8)

    return canvas

def transform_portrait(
    image_bytes: bytes,
    hair_style_id: Optional[str] = None,
    beard_style_id: Optional[str] = None
) -> bytes:
    """
    Main entry point: Transforms portrait bytes with selected hairstyle and beard style.
    Preserves user face, identity, background, and lighting.
    Returns high-quality JPEG bytes.
    """
    # 1. Parse image bytes with EXIF rotation
    pil_img = Image.open(io.BytesIO(image_bytes))
    pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
    bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 2. Detect face ONCE on original clean portrait
    u_face = get_primary_face_box(bgr)
    if u_face is None:
        logger.warning("No face detected in portrait, returning enhanced original.")
        out_buf = io.BytesIO()
        pil_img.save(out_buf, format="JPEG", quality=92)
        return out_buf.getvalue()

    result = bgr.copy()

    # 3. Apply beard first (so hairline/fringe can cleanly drape over forehead)
    if beard_style_id:
        result = apply_beard_overlay(result, u_face, beard_style_id)

    # 4. Apply hairstyle
    if hair_style_id:
        result = apply_hairstyle_overlay(result, u_face, hair_style_id)

    # 5. Output to high-quality JPEG
    rgb_out = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    out_pil = Image.fromarray(rgb_out)
    buf = io.BytesIO()
    out_pil.save(buf, format="JPEG", quality=95)
    return buf.getvalue()
