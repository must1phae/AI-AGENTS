from __future__ import annotations

import time
from typing import Any

import requests

from config.settings import BASE_URL, IG_ACCESS_TOKEN, IG_USER_ID

_REQUEST_TIMEOUT = 30


def _request_json(method: str, url: str, *, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.request(method, url, params=params, timeout=_REQUEST_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(str(payload["error"]))
    return payload


def create_media_container(image_url: str, caption: str) -> str:
    if not IG_USER_ID:
        raise ValueError("IG_USER_ID is required to create a media container.")
    if not IG_ACCESS_TOKEN:
        raise ValueError("IG_ACCESS_TOKEN is required to create a media container.")
    if not image_url:
        raise ValueError("image_url is required and must be publicly reachable.")

    payload = _request_json(
        "POST",
        f"{BASE_URL}/{IG_USER_ID}/media",
        params={
            "image_url": image_url,
            "caption": caption,
            "access_token": IG_ACCESS_TOKEN,
        },
    )
    container_id = payload.get("id")
    if not container_id:
        raise RuntimeError(f"Unexpected response while creating media container: {payload}")
    return container_id


def get_container_status(container_id: str) -> dict[str, Any]:
    if not container_id:
        raise ValueError("container_id is required.")
    return _request_json(
        "GET",
        f"{BASE_URL}/{container_id}",
        params={
            "fields": "status_code",
            "access_token": IG_ACCESS_TOKEN,
        },
    )


def wait_for_container_ready(container_id: str, timeout_seconds: int = 120, poll_interval: int = 5) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        status = get_container_status(container_id)
        status_code = str(status.get("status_code", "")).upper()
        if status_code in {"FINISHED", "DONE"}:
            return
        if status_code in {"ERROR", "FAILED"}:
            raise RuntimeError(f"Instagram container failed to process: {status}")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out waiting for Instagram container {container_id} to finish.")
        time.sleep(poll_interval)


def publish_media(container_id: str) -> dict[str, Any]:
    if not IG_USER_ID:
        raise ValueError("IG_USER_ID is required to publish media.")
    if not IG_ACCESS_TOKEN:
        raise ValueError("IG_ACCESS_TOKEN is required to publish media.")

    payload = _request_json(
        "POST",
        f"{BASE_URL}/{IG_USER_ID}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": IG_ACCESS_TOKEN,
        },
    )
    return payload
