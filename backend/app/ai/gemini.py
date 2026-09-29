import base64
import logging
import httpx
from typing import Optional, List
from app.ai.base import ImageProvider
from app.services.keys import gemini_key_pool

logger = logging.getLogger(__name__)

class GeminiProvider(ImageProvider):
    def __init__(self, key_pool=None):
        self.key_pool = key_pool or gemini_key_pool

    async def edit(
        self,
        user_image: bytes,
        prompt: str,
        reference_images: Optional[List[bytes]] = None
    ) -> bytes:
        if not self.key_pool.has_keys:
            raise RuntimeError("GEMINI_API_KEYS is empty. Please configure GEMINI_API_KEYS in backend/.env")

        max_attempts = max(1, self.key_pool.size)
        last_error = None

        for attempt in range(max_attempts):
            api_key = self.key_pool.next()
            try:
                result_bytes = await self._call_gemini_api(api_key, user_image, prompt, reference_images)
                return result_bytes
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                logger.warning(f"Gemini API error (status {status}) on attempt {attempt + 1}")
                if status in (429, 403):
                    self.key_pool.mark_invalid(api_key)
                    last_error = "AI_QUOTA_EXCEEDED"
                elif status == 400:
                    last_error = "AI_KEY_INVALID"
                else:
                    last_error = f"GENERATION_FAILED: {status}"
            except Exception as e:
                logger.error(f"Gemini generation exception: {e}")
                last_error = f"GENERATION_FAILED: {str(e)}"

        raise RuntimeError(last_error or "AI_QUOTA_EXCEEDED")

    async def _call_gemini_api(
        self,
        api_key: str,
        user_image: bytes,
        prompt: str,
        reference_images: Optional[List[bytes]] = None
    ) -> bytes:
        img_b64 = base64.b64encode(user_image).decode("utf-8")
        
        # We target the multimodal generative image model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.95
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            # Check if image bytes are returned in inline_data or candidate parts
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("No candidates returned from Gemini API")
            
            parts = candidates[0].get("content", {}).get("parts", [])
            for p in parts:
                if "inline_data" in p and "data" in p["inline_data"]:
                    return base64.b64decode(p["inline_data"]["data"])

            # If text returned instead of image directly (as gemini-2.0-flash does for standard completions),
            # this indicates standard vision output rather than native diffusion output.
            raise RuntimeError("Gemini model returned text instead of edited image. Ensure Imagen or image generation endpoint is enabled.")
