# 05 — API Spec (FastAPI, Python)

Base path `/v1`. JSON responses. Error shape:
```json
{ "error": { "code": "NO_FACE", "message": "No face detected. Face the camera in good light." } }
```
Interactive docs available at `/docs` (Swagger) while developing.

## Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/styles?type=hair\|beard` | List styles (id, name, thumb_url) |
| POST | `/photos` | Multipart upload (`file`) → validates face → `{photo_id, ok, issues[]}` |
| DELETE | `/photos/{photo_id}` | Delete photo + all outputs immediately |
| POST | `/generations` | `{photo_id, hair_style_id?, beard_style_id?, view?}` → `{job_id}` |
| GET | `/generations/{job_id}` | `{status, result_url?, error?}` |
| GET | `/files/{path}` | Serve stored output via short-lived signed token |
| POST | `/suggestions` | (P2) top-N styles for face shape |
| GET | `/me/looks` | (P2) saved looks |

## Details

### POST /photos
- Multipart form field `file` (JPG/PNG/WEBP, ≤ 8 MB, ≥ 512×512).
- Backend fixes EXIF rotation, strips metadata, runs face checks, stores file, returns:
  `{ "photo_id": "uuid", "ok": true, "issues": [], "expires_in": 86400 }`
  or `{ "ok": false, "issues": ["FACE_NOT_FRONTAL"] }` (nothing stored on failure).

### POST /generations
- At least one of `hair_style_id` / `beard_style_id` required.
- Returns cached result immediately (`status: "done"`) if the same combo exists.
- Uses the server-side API key(s) to call the AI provider (see `04_AI_PIPELINE.md`).
- `view`: `front` (default) | `side` | `back` (beta).

### GET /generations/{id}
`status`: `queued | running | done | failed`. Poll every 1.5 s.

## Error Codes
`NO_FACE`, `MULTIPLE_FACES`, `FACE_TOO_SMALL`, `TOO_BLURRY`, `TOO_DARK`, `FACE_NOT_FRONTAL`, `FILE_TOO_LARGE`, `UNSUPPORTED_TYPE`, `RATE_LIMITED`, `DAILY_CAP_REACHED`, `PHOTO_EXPIRED`, `GENERATION_FAILED`, `IDENTITY_MISMATCH`, `AI_KEY_INVALID`, `AI_QUOTA_EXCEEDED`.

## Cross-Cutting
- CORS: only `ALLOWED_ORIGIN`.
- Anonymous identity via signed `session_id` cookie (HttpOnly, SameSite=Lax).
- Rate limiting with `slowapi` per IP + session.
- Request IDs in logs; never log image bytes or API keys.
- Backend also mounts `frontend/` as static files at `/`.
