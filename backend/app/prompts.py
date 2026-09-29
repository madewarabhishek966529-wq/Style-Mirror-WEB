"""
AI prompt templates for hairstyle and beard modifications.
Reference: stylemirror-docs/04_AI_PIPELINE.md
"""
from typing import Optional

def build_prompt(
    hair_name: Optional[str] = None,
    hair_hint: Optional[str] = None,
    beard_name: Optional[str] = None,
    beard_hint: Optional[str] = None,
    view: str = "front",
    is_strict_retry: bool = False
) -> str:
    prompt = ""
    if hair_name and beard_name:
        prompt = (
            f"Edit this photo. Change ONLY the hairstyle to {hair_name} ({hair_hint}) and the facial "
            f"hair to {beard_name} ({beard_hint}). Keep identity, face shape, skin tone, expression, "
            f"clothing, background, lighting and camera angle exactly the same. Photorealistic."
        )
    elif hair_name:
        prompt = (
            f"Edit this photo. Change ONLY the person's hairstyle to: {hair_name} — {hair_hint}. "
            f"Keep the exact same face, identity, skin tone, facial features, expression, facial hair, "
            f"clothing, background, lighting, and camera angle. Keep hair color natural unless told otherwise. "
            f"The result must look like a real, unedited photograph of the same person."
        )
    elif beard_name:
        prompt = (
            f"Edit this photo. Change ONLY the person's facial hair to: {beard_name} — {beard_hint}. "
            f"Keep the exact same face, identity, hairstyle, skin tone, expression, clothing, background, "
            f"lighting and camera angle. Beard must match the person's hair color and grow naturally along "
            f"the jawline. Photorealistic, no artifacts."
        )
    else:
        prompt = "Preserve the original portrait photo with photorealistic clarity."

    if view in ("side", "back"):
        prompt += f" Generate the same person with the same hairstyle from the {view} view."

    if is_strict_retry:
        prompt += " The face MUST remain identical to the input photo. Do not alter eyes, nose, mouth, jawline or skin tone."

    return prompt
