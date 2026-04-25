from __future__ import annotations

import random
from urllib.parse import quote

from config.settings import IMAGE_PROVIDER, IMAGE_SIZE


def _parse_size(raw_size: str) -> tuple[int, int]:
    try:
        width_str, height_str = raw_size.lower().split("x", 1)
        width = max(512, min(2048, int(width_str)))
        height = max(512, min(2048, int(height_str)))
        return width, height
    except Exception:
        return 1200, 1200


def _build_prompt(niche: str, tone: str) -> str:
    return (
        f"Instagram social media image about {niche}, "
        f"tone {tone}, cinematic lighting, high quality, modern composition, "
        "no text, no watermark"
    )


def generate_image_url(niche: str, tone: str) -> str:
    provider = IMAGE_PROVIDER
    if provider != "pollinations":
        raise ValueError(f"Unsupported IMAGE_PROVIDER: {provider}")

    width, height = _parse_size(IMAGE_SIZE)
    seed = random.randint(1, 999999)
    prompt = _build_prompt(niche=niche, tone=tone)
    encoded_prompt = quote(prompt, safe="")
    return (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={width}&height={height}&seed={seed}&nologo=true"
    )
