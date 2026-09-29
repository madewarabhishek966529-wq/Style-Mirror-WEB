# 02 — Architecture

## Tech Stack (no Docker, no frontend framework)
| Layer | Choice | Why |
|---|---|---|
| Frontend | **Plain HTML + CSS + JavaScript** (ES modules, `fetch`) | No build step, simple to host and edit |
| Backend | **Python 3.11+ with FastAPI + Uvicorn** | Best image/AI ecosystem, async |
| AI generation | **Hosted AI API (API key)** — Gemini image-editing model as primary, optional fallback providers | Changes hair/beard without a GPU |
| Face check | MediaPipe Face Landmarker (OpenCV as fallback) | Face count, pose, size |
| Images | Pillow + OpenCV | Resize, EXIF fix, watermark |
| Jobs | FastAPI `BackgroundTasks` / `asyncio` + a `generations` table (no Redis) | Generation takes 5–20 s |
| DB | **SQLite** for dev/MVP (SQLAlchemy); Supabase Postgres later if needed | Zero setup |
| File storage | Local `storage/` folder (MVP); Supabase/Firebase Storage later | Simple TTL cleanup |
| Rate limit | `slowapi` (in-memory) | No extra services |
| Hosting | Render / Railway / any VPS running `uvicorn` (no containers). Backend serves the static frontend too | One deployable |
| Monitoring | Sentry (Python + browser snippet), optional PostHog | Errors + funnel |

## API Keys — How Hair & Beard Changing Works
- The AI provider **API key lives only in the Python backend `.env`**. It is never written into HTML/JS (anyone could read it in the browser).
- Browser → `POST /v1/generations` → Python backend → AI provider using the key → result image → browser.
- Supports several keys for rotation/fallback: `GEMINI_API_KEYS=key1,key2` (backend picks round-robin and skips a key on 429/quota errors).
- Optional fallback provider key (e.g. `REPLICATE_API_TOKEN`) selected by `AI_PROVIDER` / `AI_FALLBACK_PROVIDER`.
- Add a per-user and global daily cap so a leaked page cannot burn your quota.

## System Diagram
```
Browser (HTML/CSS/JS) ──HTTPS──▶ FastAPI (Python) ──API key──▶ AI Provider (Gemini / fallback)
                                     │
                                     ├─▶ SQLite (styles, photos, generations)
                                     └─▶ storage/ (photos, outputs, auto-deleted)
```

## Request Lifecycle
1. Browser uploads the selfie: `POST /v1/photos` (multipart form).
2. Backend validates the face and returns `{photo_id, ok, issues[]}`.
3. Browser calls `POST /v1/generations` with `hair_style_id` and/or `beard_style_id` → `job_id`.
4. Background task: build prompt → call AI provider with API key → identity check → save output.
5. Browser polls `GET /v1/generations/{job_id}` every ~1.5 s until `done`, then shows the image.

## Project Structure
```
stylemirror/
├─ backend/
│  ├─ app/
│  │  ├─ main.py                 # FastAPI app, mounts /static frontend
│  │  ├─ config.py               # loads .env (pydantic-settings)
│  │  ├─ db.py  models.py  schemas.py
│  │  ├─ routers/{styles,photos,generations}.py
│  │  ├─ services/{face_check,storage,identity,keys,cleanup}.py
│  │  ├─ ai/{base,gemini,fallback}.py
│  │  ├─ prompts.py
│  │  └─ workers/generate.py
│  ├─ tests/
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ index.html                 # landing
│  ├─ try.html                   # upload → style → result
│  ├─ privacy.html  terms.html
│  ├─ css/{base.css,layout.css,components.css}
│  ├─ js/{main.js,api.js,state.js,uploader.js,styleGrid.js,slider.js,progress.js}
│  └─ assets/styles/{hair,beard}/   # cropped thumbnails
├─ scripts/{crop_sheet.py,seed_styles.py}
├─ .gitignore
└─ README.md
```

## Run Locally (no Docker)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # then paste your API key(s)
python ../scripts/seed_styles.py
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000
```

## `requirements.txt` (starting point)
```
fastapi
uvicorn[standard]
python-multipart
pydantic-settings
sqlalchemy
pillow
opencv-python-headless
mediapipe
numpy
httpx
google-genai
slowapi
python-dotenv
sentry-sdk
pytest
ruff
```

## Environment Variables (`backend/.env`)
```
AI_PROVIDER=gemini
GEMINI_API_KEYS=your_key_1,your_key_2
AI_FALLBACK_PROVIDER=
REPLICATE_API_TOKEN=
DATABASE_URL=sqlite:///./stylemirror.db
STORAGE_DIR=./storage
PHOTO_TTL_HOURS=24
RATE_LIMIT_ANON_PER_HOUR=10
DAILY_GENERATION_CAP=500
ALLOWED_ORIGIN=http://localhost:8000
SENTRY_DSN=
```
Commit only `.env.example`, never `.env`.
