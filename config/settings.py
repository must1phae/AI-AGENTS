from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


IG_USER_ID = _get_env("IG_USER_ID")
IG_ACCESS_TOKEN = _get_env("IG_ACCESS_TOKEN")
GEMINI_API_KEY = _get_env("GEMINI_API_KEY")

GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0").strip()
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
DEFAULT_IMAGE_URL = os.getenv("DEFAULT_IMAGE_URL", "").strip()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0").strip()
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "").strip()
PUBLISH_TARGET = os.getenv("PUBLISH_TARGET", "instagram").strip().lower()

NICHE = os.getenv("NICHE", "AI et technologie").strip()
TONE = os.getenv("TONE", "viral").strip()
MAX_HASHTAGS = int(os.getenv("MAX_HASHTAGS", "2"))
POST_HOUR = int(os.getenv("POST_HOUR", "9"))


SETTINGS: dict[str, Any] = {
    "IG_USER_ID": IG_USER_ID,
    "IG_ACCESS_TOKEN": IG_ACCESS_TOKEN,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "GRAPH_API_VERSION": GRAPH_API_VERSION,
    "BASE_URL": BASE_URL,
    "GEMINI_MODEL": GEMINI_MODEL,
    "DEFAULT_IMAGE_URL": DEFAULT_IMAGE_URL,
    "REDIS_URL": REDIS_URL,
    "FACEBOOK_PAGE_ID": FACEBOOK_PAGE_ID,
    "PUBLISH_TARGET": PUBLISH_TARGET,
    "NICHE": NICHE,
    "TONE": TONE,
    "MAX_HASHTAGS": MAX_HASHTAGS,
    "POST_HOUR": POST_HOUR,
}
