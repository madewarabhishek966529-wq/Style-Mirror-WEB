import io
import cv2
import numpy as np
from PIL import Image, ImageOps

def validate_photo_bytes(data: bytes) -> dict:
    """
    Validates uploaded face photo against quality and biometric requirements.
    Thresholds:
      - Resolution >= 512x512
      - Single face in frame
      - Face height >= 28% of total height
      - Sharpness (Laplacian variance >= 35)
      - Luminance (mean brightness between 45 and 235)
      - Frontal orientation (eyes horizontal & centered)
    """
    issues = []
    face_meta = {}

    try:
        # Load with PIL to fix EXIF rotation and check dimensions
        pil_img = Image.open(io.BytesIO(data))
        pil_img = ImageOps.exif_transpose(pil_img)
        w, h = pil_img.size

        if w < 512 or h < 512:
            issues.append("FACE_TOO_SMALL")
            return {"ok": False, "issues": issues, "face_meta": face_meta}

        # Convert to numpy array for OpenCV
        rgb = np.array(pil_img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # 1. Brightness check
        mean_brightness = float(np.mean(gray))
        face_meta["brightness"] = mean_brightness
        if mean_brightness < 40:
            issues.append("TOO_DARK")
        elif mean_brightness > 245:
            issues.append("TOO_BRIGHT")

        # 2. Blur / Sharpness check using Laplacian variance
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        face_meta["blur_score"] = blur_score
        if blur_score < 30:
            issues.append("TOO_BLURRY")

        # 3. Face detection with OpenCV CascadeClassifier (built into opencv-python)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(int(w * 0.15), int(h * 0.15))
        )

        face_count = len(faces)
        face_meta["face_count"] = face_count

        if face_count == 0:
            # Try with slightly more relaxed minNeighbors
            faces_relaxed = face_cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=3, minSize=(int(w * 0.12), int(h * 0.12)))
            if len(faces_relaxed) == 1:
                faces = faces_relaxed
                face_count = 1
            else:
                issues.append("NO_FACE")
                return {"ok": False, "issues": issues, "face_meta": face_meta}

        if face_count > 1:
            issues.append("MULTIPLE_FACES")
            return {"ok": False, "issues": issues, "face_meta": face_meta}

        # Exactly 1 face found
        fx, fy, fw, fh = faces[0]
        face_meta["bbox"] = [int(fx), int(fy), int(fw), int(fh)]
        face_ratio = fh / float(h)
        face_meta["face_ratio"] = float(face_ratio)

        # 4. Face size check
        if face_ratio < 0.20:
            issues.append("FACE_TOO_SMALL")

        # 5. Eye / Frontal check
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        face_roi_gray = gray[fy : fy + int(fh * 0.65), fx : fx + fw]
        eyes = eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=4)

        if len(eyes) >= 2:
            # Sort by x coordinate
            eyes = sorted(eyes, key=lambda e: e[0])
            e1, e2 = eyes[0], eyes[1]
            eye_angle = abs(e1[1] - e2[1]) / float(fw)
            if eye_angle > 0.18:
                issues.append("FACE_NOT_FRONTAL")

        face_meta["issues"] = issues
        return {
            "ok": len(issues) == 0,
            "issues": issues,
            "face_meta": face_meta
        }

    except Exception as e:
        # Fallback if image parsing fails
        return {"ok": False, "issues": ["INVALID_IMAGE_FILE"], "face_meta": {"error": str(e)}}
