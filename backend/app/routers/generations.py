from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Generation, Photo, Style
from app.config import settings
from app.schemas import GenerationCreateRequest, GenerationJobResponse
from app.services.storage import generate_signed_url
from app.workers.generate import process_generation_job
from app.limiter import limiter

router = APIRouter(prefix="/v1", tags=["generations"])

@router.post("/generations", response_model=GenerationJobResponse)
@limiter.limit(f"{settings.RATE_LIMIT_ANON_PER_HOUR * 3}/hour")
def create_generation(
    request: Request,
    req: GenerationCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submits a style try-on generation job.
    Returns immediately with job_id for polling. If identical combination
    was previously generated for this photo, returns cached result instantly.
    """
    if not req.hair_style_id and not req.beard_style_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "STYLE_REQUIRED", "message": "At least one hairstyle or beard style must be selected."}}
        )

    # Check daily generation cap per specification
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(Generation).filter(Generation.created_at >= today_start).count()
    if today_count >= settings.DAILY_GENERATION_CAP:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": {"code": "DAILY_CAP_REACHED", "message": "Daily generation quota reached. Please try again tomorrow."}}
        )

    # Validate photo existence and expiry
    photo = db.query(Photo).filter(Photo.id == req.photo_id).first()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PHOTO_NOT_FOUND", "message": "Photo not found or expired."}}
        )

    now = datetime.now(timezone.utc)
    photo_expires = photo.expires_at
    if photo_expires.tzinfo is None:
        photo_expires = photo_expires.replace(tzinfo=timezone.utc)
    if photo_expires < now:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={"error": {"code": "PHOTO_EXPIRED", "message": "This photo has expired. Please upload a fresh photo."}}
        )

    # Validate selected style IDs
    if req.hair_style_id:
        hair = db.query(Style).filter(Style.id == req.hair_style_id, Style.type == "hair").first()
        if not hair:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_HAIR_STYLE", "message": f"Hairstyle '{req.hair_style_id}' does not exist."}}
            )

    if req.beard_style_id:
        beard = db.query(Style).filter(Style.id == req.beard_style_id, Style.type == "beard").first()
        if not beard:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_BEARD_STYLE", "message": f"Beard style '{req.beard_style_id}' does not exist."}}
            )

    # Cache check
    cached = db.query(Generation).filter(
        Generation.photo_id == req.photo_id,
        Generation.hair_style_id == req.hair_style_id,
        Generation.beard_style_id == req.beard_style_id,
        Generation.view == req.view,
        Generation.status == "done"
    ).first()

    if cached and cached.result_path:
        return GenerationJobResponse(
            job_id=cached.id,
            status="done",
            result_url=generate_signed_url(cached.result_path),
            identity_score=cached.identity_score
        )

    # Create new generation record
    job = Generation(
        photo_id=req.photo_id,
        hair_style_id=req.hair_style_id,
        beard_style_id=req.beard_style_id,
        view=req.view,
        status="queued"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue background generation task
    background_tasks.add_task(process_generation_job, job.id)

    return GenerationJobResponse(
        job_id=job.id,
        status="queued"
    )

@router.get("/generations/{job_id}", response_model=GenerationJobResponse)
def get_generation_status(job_id: str, db: Session = Depends(get_db)):
    """
    Polls status of a generation job.
    Status can be: queued, running, done, failed.
    """
    job = db.query(Generation).filter(Generation.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "JOB_NOT_FOUND", "message": "Generation job not found."}}
        )

    result_url = None
    if job.status == "done" and job.result_path:
        result_url = generate_signed_url(job.result_path)

    return GenerationJobResponse(
        job_id=job.id,
        status=job.status,
        result_url=result_url,
        identity_score=job.identity_score,
        error=job.error
    )
