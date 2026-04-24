from __future__ import annotations

from typing import Any

import requests

from config.settings import BASE_URL, IG_ACCESS_TOKEN

_REQUEST_TIMEOUT = 30


def get_post_insights(media_id: str) -> dict[str, Any]:
    if not media_id:
        raise ValueError("media_id is required.")
    if not IG_ACCESS_TOKEN:
        raise ValueError("IG_ACCESS_TOKEN is required to read insights.")

    response = requests.get(
        f"{BASE_URL}/{media_id}/insights",
        params={
            "metric": "likes,impressions,reach,engagement",
            "access_token": IG_ACCESS_TOKEN,
        },
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _metric_value(insights: dict[str, Any], metric_name: str) -> float:
    for item in insights.get("data", []):
        if item.get("name") == metric_name:
            values = item.get("values") or []
            if values:
                value = values[0].get("value", 0)
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0
    return 0.0


def adjust_tone_from_feedback(insights: dict[str, Any]) -> str:
    engagement = _metric_value(insights, "engagement")
    if engagement > 500:
        return "viral"
    if engagement > 100:
        return "educatif"
    return "storytelling"
