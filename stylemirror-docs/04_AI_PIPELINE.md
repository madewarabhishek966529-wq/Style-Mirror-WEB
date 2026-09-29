# 04 — AI Pipeline

## Provider Interface
```python
# app/ai/base.py
from abc import ABC, abstractmethod

class ImageProvider(ABC):
    @abstractmethod
    async def edit(self, user_image: bytes, prompt: str,
                   reference_images: list[bytes] | None = None) -> bytes: ...
```
Implementations: `GeminiProvider` (MVP), `ReplicateProvider` (fallback), self-hosted SDXL (later). Selected via `AI_PROVIDER` / `AI_FALLBACK_PROVIDER` env vars.

## API Keys (server-side only)
```python
# app/services/keys.py
import itertools, os

class KeyPool:
    def __init__(self, env_name="GEMINI_API_KEYS"):
        keys = [k.strip() for k in os.getenv(env_name, "").split(",") if k.strip()]
        if not keys:
            raise RuntimeError(f"{env_name} is empty")
        self._cycle = itertools.cycle(keys)
        self._size = len(keys)

    def next(self) -> str:
        return next(self._cycle)

    @property
    def size(self): return self._size
```
- Call `pool.next()` per request; on HTTP 429 / quota error, retry with the next key (max `pool.size` attempts), then fall back to `AI_FALLBACK_PROVIDER`, then return `AI_QUOTA_EXCEEDED`.
- Invalid key → log `AI_KEY_INVALID` (without printing the key) and skip it.
- Keys come from `backend/.env` only. Never in frontend files, git, logs, or error messages.
- Add `DAILY_GENERATION_CAP` and per-IP limits so quota can't be drained.
- Call the AI API with `httpx`/official Python SDK using `pool.next()`; check the provider's current model name and pricing in its docs when you implement.

## Worker Steps
1. Load photo → fix EXIF rotation → resize longest side to 1024 px.
2. Re-run face check.
3. Build prompt from templates below.
4. Call provider with user photo (+ optional style reference).
5. **Identity check:** face-embedding cosine similarity (InsightFace/ArcFace) between input and output. If < ~0.6 → retry once with stricter prompt.
6. Optional "AI Preview" watermark (free tier / shared images).
7. Save output, update job row, return signed URL (expires in 1 h).

## Prompt Templates (`app/prompts.py`)

**Hair only**
```
Edit this photo. Change ONLY the person's hairstyle to: {hair.name} — {hair.prompt_hint}.
Keep the exact same face, identity, skin tone, facial features, expression, facial hair,
clothing, background, lighting, and camera angle. Keep hair color natural unless told otherwise.
The result must look like a real, unedited photograph of the same person.
```

**Beard only**
```
Edit this photo. Change ONLY the person's facial hair to: {beard.name} — {beard.prompt_hint}.
Keep the exact same face, identity, hairstyle, skin tone, expression, clothing, background,
lighting and camera angle. Beard must match the person's hair color and grow naturally along
the jawline. Photorealistic, no artifacts.
```

**Hair + beard**
```
Edit this photo. Change ONLY the hairstyle to {hair.name} ({hair.prompt_hint}) and the facial
hair to {beard.name} ({beard.prompt_hint}). Keep identity, face shape, skin tone, expression,
clothing, background, lighting and camera angle exactly the same. Photorealistic.
```

**Side/back view (Phase 2, beta)**
Append: `Generate the same person with the same hairstyle from the {side|back} view.`

**Stricter retry suffix**
`The face MUST remain identical to the input photo. Do not alter eyes, nose, mouth, jawline or skin tone.`

## Cost & Latency Control
- Generate **on click** only, never all 50 at once.
- "Suggest for me" → max 6 images.
- Cache key `(photo_sha256, hair_id, beard_id, view)` → instant repeats.
- Rate limit (`slowapi`): 10 generations / IP / hour anonymous; higher when logged in.
- Downscale input to 1024 px.
- Log `provider`, `latency_ms`, `cost_usd` per job.

## Face Validation Thresholds
| Check | Rule |
|---|---|
| Face count | exactly 1 |
| Face size | ≥ 30% of image height |
| Yaw / pitch | yaw < 20°, pitch < 20° |
| Blur | Laplacian variance above tuned threshold |
| Brightness | mean luminance within tuned range |
| Resolution | ≥ 512×512 |
