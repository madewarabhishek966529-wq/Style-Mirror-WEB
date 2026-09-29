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
