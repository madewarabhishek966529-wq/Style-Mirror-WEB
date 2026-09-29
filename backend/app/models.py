import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Index
)
from sqlalchemy.orm import relationship
from app.db import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Style(Base):
    __tablename__ = "styles"

    id = Column(String, primary_key=True)  # 'H01', 'B01', etc.
    type = Column(String, nullable=False)   # 'hair' | 'beard'
    name = Column(String, nullable=False)
    prompt_hint = Column(String, nullable=False)
    thumb_url = Column(String, nullable=False)
    ref_front_url = Column(String, nullable=True)
    ref_side_url = Column(String, nullable=True)
    ref_back_url = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class Photo(Base):
    __tablename__ = "photos"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=True)  # None = anonymous
    session_id = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    sha256 = Column(String, nullable=False)
    face_meta = Column(JSON, nullable=True)  # {bbox, yaw, blur_score, etc.}
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=False)

    generations = relationship("Generation", back_populates="photo", cascade="all, delete-orphan")

class Generation(Base):
    __tablename__ = "generations"

    id = Column(String, primary_key=True, default=generate_uuid)
    photo_id = Column(String, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    hair_style_id = Column(String, ForeignKey("styles.id"), nullable=True)
    beard_style_id = Column(String, ForeignKey("styles.id"), nullable=True)
    view = Column(String, default="front")  # front, side, back
    status = Column(String, default="queued")  # queued, running, done, failed
    result_path = Column(String, nullable=True)
    identity_score = Column(Float, nullable=True)
    provider = Column(String, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    photo = relationship("Photo", back_populates="generations")
    hair_style = relationship("Style", foreign_keys=[hair_style_id])
    beard_style = relationship("Style", foreign_keys=[beard_style_id])

# Cache index to allow instant repeats for identical combinations
Index(
    "generations_cache_idx",
    Generation.photo_id,
    Generation.hair_style_id,
    Generation.beard_style_id,
    Generation.view
)
