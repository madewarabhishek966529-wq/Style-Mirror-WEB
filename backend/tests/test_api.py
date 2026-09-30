import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine
from app.prompts import build_prompt
from app.services.storage import generate_signed_url, verify_token
from scripts.seed_styles import seed

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    seed()
    with TestClient(app) as c:
        yield c

def test_prompt_builder_hair_only():
    prompt = build_prompt(hair_name="Crew Cut", hair_hint="military cut", beard_name=None, beard_hint=None)
    assert "Crew Cut" in prompt
    assert "military cut" in prompt
    assert "Change ONLY the person's hairstyle" in prompt

def test_prompt_builder_combo():
    prompt = build_prompt(hair_name="Quiff", hair_hint="voluminous front", beard_name="Full Beard", beard_hint="thick beard")
    assert "Quiff" in prompt
    assert "Full Beard" in prompt
    assert "Change ONLY the hairstyle" in prompt

def test_signed_token_roundtrip():
    path = "photos/test-id/out/gen-123.jpg"
    url = generate_signed_url(path, expires_in_seconds=60)
    assert "?expires=" in url and "&token=" in url
    parts = url.split("?")
    params = dict(p.split("=") for p in parts[1].split("&"))
    expires = int(params["expires"])
    token = params["token"]
    assert verify_token(path, expires, token) is True
    # Test invalid token
    assert verify_token(path, expires, "wrongtoken") is False

def test_get_styles_endpoint(client):
    response = client.get("/v1/styles")
    assert response.status_code == 200
    styles = response.json()
    assert isinstance(styles, list)
    assert len(styles) == 50

def test_get_styles_by_type(client):
    res_hair = client.get("/v1/styles?type=hair")
    assert res_hair.status_code == 200
    hairs = res_hair.json()
    assert len(hairs) == 25
    assert all(s["type"] == "hair" for s in hairs)

    res_beard = client.get("/v1/styles?type=beard")
    assert res_beard.status_code == 200
    beards = res_beard.json()
    assert len(beards) == 25
    assert all(s["type"] == "beard" for s in beards)

def test_generation_without_styles_fails(client):
    res = client.post("/v1/generations", json={"photo_id": "dummy-uuid"})
    assert res.status_code == 400
    body = res.json()
    assert "error" in body
    assert body["error"]["code"] == "STYLE_REQUIRED"

def test_nonexistent_photo_generation_fails(client):
    res = client.post("/v1/generations", json={"photo_id": "nonexistent-id", "hair_style_id": "H01"})
    assert res.status_code == 404
    body = res.json()
    assert body["error"]["code"] == "PHOTO_NOT_FOUND"

def test_photo_upload_small_resolution_fails(client):
    img = Image.new("RGB", (256, 256), color=(200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = client.post("/v1/photos", files={"file": ("small.jpg", buf.getvalue(), "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is False
    assert "IMAGE_TOO_SMALL" in data["issues"]

def test_photo_upload_no_face_fails(client):
    img = Image.new("RGB", (600, 600), color=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    res = client.post("/v1/photos", files={"file": ("noface.jpg", buf.getvalue(), "image/jpeg")})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is False
    assert "NO_FACE" in data["issues"]

def test_generation_with_valid_photo_succeeds(client):
    from app.models import Photo
    from app.db import SessionLocal
    from datetime import datetime, timezone, timedelta
    db = SessionLocal()
    pid = "test-gen-photo-valid"
    photo = Photo(
        id=pid,
        session_id="test-session",
        storage_path="photos/test/original.jpg",
        sha256="dummyhash",
        face_meta={},
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    db.merge(photo)
    db.commit()
    db.close()

    res = client.post("/v1/generations", json={"photo_id": pid, "hair_style_id": "H01"})
    assert res.status_code == 200
    data = res.json()
    assert "job_id" in data
    assert data["status"] in ("queued", "running", "done")


