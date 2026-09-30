import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.db import engine, Base
from app.routers import styles, photos, generations, files
from app.services.cleanup import cleanup_expired_photos_loop

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

import sys
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure DB tables exist
    Base.metadata.create_all(bind=engine)

    # 2. Seed styles catalog if empty
    try:
        from scripts.seed_styles import seed
        seed()
    except Exception as e:
        print(f"Auto-seed notification: {e}")

    # 3. Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_expired_photos_loop(interval_seconds=900))

    yield

    # Clean shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="StyleMirror API",
    description="Identity-Preserving Hair & Beard AI Try-On System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
origins = [
    settings.ALLOWED_ORIGIN,
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "null",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^(https?://(localhost|127\.0\.0\.1)(:\d+)?|null)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized Error Handling
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail)}}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0].get("msg") if errors else "Invalid request data"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": {"code": "VALIDATION_ERROR", "message": msg}}
    )

# Include Routers
app.include_router(styles.router)
app.include_router(photos.router)
app.include_router(generations.router)
app.include_router(files.router)

# Mount Frontend Assets and Pages
if FRONTEND_DIR.exists():
    # Mount assets, css, js explicitly
    if (FRONTEND_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
    if (FRONTEND_DIR / "css").exists():
        app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    if (FRONTEND_DIR / "js").exists():
        app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    # Direct routes for pages
    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "StyleMirror API is running"}

    @app.get("/try", include_in_schema=False)
    @app.get("/try.html", include_in_schema=False)
    async def serve_try():
        try_file = FRONTEND_DIR / "try.html"
        if try_file.exists():
            return FileResponse(try_file)
        return {"message": "try.html not found"}

    @app.get("/privacy", include_in_schema=False)
    @app.get("/privacy.html", include_in_schema=False)
    async def serve_privacy():
        p_file = FRONTEND_DIR / "privacy.html"
        if p_file.exists():
            return FileResponse(p_file)
        return {"message": "privacy.html not found"}

    @app.get("/terms", include_in_schema=False)
    @app.get("/terms.html", include_in_schema=False)
    async def serve_terms():
        t_file = FRONTEND_DIR / "terms.html"
        if t_file.exists():
            return FileResponse(t_file)
        return {"message": "terms.html not found"}
