import os
import shutil
import time
import hmac
import hashlib
from pathlib import Path
from typing import Optional
from app.config import settings

STORAGE_DIR = Path(settings.STORAGE_DIR)

def get_full_path(relative_path: str) -> Path:
    # Normalize and guard against directory traversal
    clean_rel = os.path.normpath(relative_path).lstrip("/\\")
    full_path = (STORAGE_DIR / clean_rel).resolve()
    if not str(full_path).startswith(str(STORAGE_DIR.resolve())):
        raise ValueError("Invalid path access outside storage directory")
    return full_path

def save_original_photo(photo_id: str, data: bytes) -> str:
    target_dir = STORAGE_DIR / "photos" / photo_id
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / "original.jpg"
    with open(file_path, "wb") as f:
        f.write(data)
    return f"photos/{photo_id}/original.jpg"

def save_generation_result(photo_id: str, gen_id: str, data: bytes) -> str:
    target_dir = STORAGE_DIR / "photos" / photo_id / "out"
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"{gen_id}.jpg"
    with open(file_path, "wb") as f:
        f.write(data)
    return f"photos/{photo_id}/out/{gen_id}.jpg"

def delete_photo_storage(photo_id: str):
    target_dir = STORAGE_DIR / "photos" / photo_id
    if target_dir.exists():
        shutil.rmtree(target_dir, ignore_errors=True)

def generate_signed_url(relative_path: str, expires_in_seconds: int = 3600) -> str:
    expires_at = int(time.time()) + expires_in_seconds
    clean_path = relative_path.replace("\\", "/").lstrip("/")
    message = f"{clean_path}:{expires_at}".encode("utf-8")
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"/v1/files/{clean_path}?expires={expires_at}&token={sig}"

def verify_token(relative_path: str, expires_at: int, token: str) -> bool:
    if time.time() > expires_at:
        return False
    clean_path = relative_path.replace("\\", "/").lstrip("/")
    message = f"{clean_path}:{expires_at}".encode("utf-8")
    expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, token)
