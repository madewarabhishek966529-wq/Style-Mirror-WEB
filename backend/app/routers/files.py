import os
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from app.services.storage import get_full_path, verify_token

router = APIRouter(prefix="/v1", tags=["files"])

@router.get("/files/{path:path}")
def serve_file(
    path: str,
    token: str = Query(...),
    expires: int = Query(...)
):
    """
    Serves private photos and outputs with short-lived HMAC token validation.
    """
    if not verify_token(path, expires, token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "TOKEN_INVALID", "message": "File access token is invalid or expired."}}
        )

    try:
        full_file_path = get_full_path(path)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_PATH", "message": "Access denied."}}
        )

    if not full_file_path.exists() or not full_file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_NOT_FOUND", "message": "Requested image file was not found."}}
        )

    return FileResponse(
        path=str(full_file_path),
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=3600"}
    )
