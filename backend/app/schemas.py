from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail

class StyleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    name: str
    prompt_hint: str
    thumb_url: str
    ref_front_url: Optional[str] = None
    ref_side_url: Optional[str] = None
    ref_back_url: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True

class PhotoUploadResponse(BaseModel):
    photo_id: Optional[str] = None
    ok: bool
    issues: List[str] = Field(default_factory=list)
    expires_in: Optional[int] = None
    message: Optional[str] = None

class GenerationCreateRequest(BaseModel):
    photo_id: str
    hair_style_id: Optional[str] = None
    beard_style_id: Optional[str] = None
    view: str = Field(default="front")

class GenerationJobResponse(BaseModel):
    job_id: str
    status: str  # queued, running, done, failed
    result_url: Optional[str] = None
    identity_score: Optional[float] = None
    error: Optional[str] = None
