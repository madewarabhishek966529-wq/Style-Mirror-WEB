import io
import time
import logging
from PIL import Image, ImageOps, ImageDraw, ImageFont
from app.db import SessionLocal
from app.models import Generation, Photo, Style
from app.config import settings
from app.prompts import build_prompt
from app.services.storage import get_full_path, save_generation_result
from app.services.face_check import validate_photo_bytes
from app.services.identity import compute_identity_similarity
from app.ai.gemini import GeminiProvider
from app.ai.fallback import FallbackProvider, ReplicateProvider

logger = logging.getLogger(__name__)

def get_provider(provider_name: str):
    p = (provider_name or "").lower().strip()
    if p == "gemini":
        try:
            return GeminiProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize GeminiProvider: {e}. Falling back to Stylist provider.")
            return FallbackProvider()
    elif p == "replicate":
        try:
            return ReplicateProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize ReplicateProvider: {e}. Falling back to Stylist provider.")
            return FallbackProvider()
    return FallbackProvider()

def add_watermark(image_bytes: bytes, text: str = "StyleMirror AI Preview") -> bytes:
    try:
        im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(im)
        w, h = im.size
        # Draw subtle bottom watermark pill
        box_w, box_h = 190, 28
        x0, y0 = w - box_w - 16, h - box_h - 16
        draw.rectangle([x0, y0, x0 + box_w, y0 + box_h], fill=(15, 23, 42, 180))
        draw.text((x0 + 12, y0 + 7), text, fill=(226, 232, 240))
        
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=92)
        return out.getvalue()
    except Exception:
        return image_bytes

async def process_generation_job(job_id: str):
    db = SessionLocal()
    start_time = time.time()
    try:
        job = db.query(Generation).filter(Generation.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        job.status = "running"
        db.commit()

        photo = db.query(Photo).filter(Photo.id == job.photo_id).first()
        if not photo:
            job.status = "failed"
            job.error = "Photo not found or expired"
            db.commit()
            return

        # 1. Load original photo bytes and preprocess (EXIF fix + resize to 1024px max)
        photo_file = get_full_path(photo.storage_path)
        with open(photo_file, "rb") as f:
            raw_bytes = f.read()

        pil_img = Image.open(io.BytesIO(raw_bytes))
        pil_img = ImageOps.exif_transpose(pil_img)
        w, h = pil_img.size
        max_dim = max(w, h)
        if max_dim > 1024:
            scale = 1024.0 / max_dim
            pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        
        proc_buf = io.BytesIO()
        pil_img.save(proc_buf, format="JPEG", quality=92)
        proc_bytes = proc_buf.getvalue()

        # 2. Styles info
        hair_style = db.query(Style).filter(Style.id == job.hair_style_id).first() if job.hair_style_id else None
        beard_style = db.query(Style).filter(Style.id == job.beard_style_id).first() if job.beard_style_id else None

        # 3. Build prompt
        prompt = build_prompt(
            hair_name=hair_style.name if hair_style else None,
            hair_hint=hair_style.prompt_hint if hair_style else None,
            beard_name=beard_style.name if beard_style else None,
            beard_hint=beard_style.prompt_hint if beard_style else None,
            view=job.view or "front",
            is_strict_retry=False
        )

        # 4. Choose provider
        provider = get_provider(settings.AI_PROVIDER)
        provider_name = settings.AI_PROVIDER
        output_bytes = None
        async def call_provider(prov):
            try:
                return await prov.edit(
                    proc_bytes,
                    prompt,
                    hair_style_id=job.hair_style_id,
                    beard_style_id=job.beard_style_id
                )
            except TypeError:
                return await prov.edit(proc_bytes, prompt)

        try:
            output_bytes = await call_provider(provider)
        except Exception as e:
            logger.warning(f"Primary provider {settings.AI_PROVIDER} failed: {e}. Trying fallback.")
            if settings.AI_FALLBACK_PROVIDER and settings.AI_FALLBACK_PROVIDER != settings.AI_PROVIDER:
                try:
                    fallback_prov = get_provider(settings.AI_FALLBACK_PROVIDER)
                    provider_name = settings.AI_FALLBACK_PROVIDER
                    output_bytes = await call_provider(fallback_prov)
                except Exception as e2:
                    logger.warning(f"Secondary fallback failed: {e2}. Using Stylist provider.")
                    fallback_prov = FallbackProvider()
                    provider_name = "fallback"
                    output_bytes = await call_provider(fallback_prov)
            else:
                fallback_prov = FallbackProvider()
                provider_name = "fallback"
                output_bytes = await call_provider(fallback_prov)

        if not output_bytes:
            raise RuntimeError("GENERATION_FAILED: No image output produced")

        # 5. Identity check
        score = compute_identity_similarity(proc_bytes, output_bytes)
        if score < 0.55:
            # Retry once with stricter prompt
            strict_prompt = build_prompt(
                hair_name=hair_style.name if hair_style else None,
                hair_hint=hair_style.prompt_hint if hair_style else None,
                beard_name=beard_style.name if beard_style else None,
                beard_hint=beard_style.prompt_hint if beard_style else None,
                view=job.view or "front",
                is_strict_retry=True
            )
            try:
                output_bytes = await provider.edit(proc_bytes, strict_prompt)
                score = compute_identity_similarity(proc_bytes, output_bytes)
            except Exception:
                pass

        # 6. Watermark
        output_bytes = add_watermark(output_bytes)

        # 7. Save result
        result_rel_path = save_generation_result(job.photo_id, job.id, output_bytes)

        latency = int((time.time() - start_time) * 1000)
        job.status = "done"
        job.result_path = result_rel_path
        job.identity_score = score
        job.provider = provider_name
        job.latency_ms = latency
        job.cost_usd = 0.005 if "gemini" in provider_name else 0.0
        job.error = None
        db.commit()
        logger.info(f"Job {job.id} completed in {latency}ms with score {score}")

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        try:
            job = db.query(Generation).filter(Generation.id == job_id).first()
            if job:
                job.status = "failed"
                job.error = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
