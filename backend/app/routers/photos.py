import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Photo
from app.config import settings
from app.schemas import PhotoUploadResponse
from app.services.storage import save_original_photo, delete_photo_storage
from app.services.face_check import validate_photo_bytes

router = APIRouter(prefix="/v1", tags=["photos"])

MAX_FILE_SIZE = 8 * 1024 * 1024  # 8 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}

@router.post("/photos", response_model=PhotoUploadResponse)
async def upload_photo(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a face photo, performs server-side quality and biometric checks,
    and returns a photo_id valid for 24 hours.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        return PhotoUploadResponse(
            ok=False,
            issues=["UNSUPPORTED_TYPE"],
            message="Only JPG, PNG and WEBP formats are supported."
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return PhotoUploadResponse(
            ok=False,
            issues=["FILE_TOO_LARGE"],
            message="Image size exceeds maximum limit of 8MB."
        )

    # Validate face quality & pose
    validation_result = validate_photo_bytes(content)
    if not validation_result["ok"]:
        return PhotoUploadResponse(
            ok=False,
            issues=validation_result["issues"],
            message="Photo did not meet face validation requirements."
        )

    photo_id = str(uuid.uuid4())
    session_id = request.cookies.get("session_id", photo_id)
    sha256_hash = hashlib.sha256(content).hexdigest()

    # Save to storage
    storage_path = save_original_photo(photo_id, content)

    # Save to database
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=settings.PHOTO_TTL_HOURS)

    photo_record = Photo(
        id=photo_id,
        session_id=session_id,
        storage_path=storage_path,
        sha256=sha256_hash,
        face_meta=validation_result.get("face_meta"),
        created_at=now,
        expires_at=expires_at
    )
    db.add(photo_record)
    db.commit()

    return PhotoUploadResponse(
        photo_id=photo_id,
        ok=True,
        issues=[],
        expires_in=settings.PHOTO_TTL_HOURS * 3600,
        message="Photo uploaded and validated successfully."
    )

@router.delete("/photos/{photo_id}")
def delete_photo(photo_id: str, db: Session = Depends(get_db)):
    """
    Instantly deletes a user photo and all generated styles from disk and database.
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PHOTO_NOT_FOUND", "message": "Photo not found or already deleted"}}
        )

    delete_photo_storage(photo_id)
    db.delete(photo)
    db.commit()

    return {"ok": True, "message": "Photo and all associated generations deleted immediately."}
