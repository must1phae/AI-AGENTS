from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests

from config.settings import BASE_URL, IG_ACCESS_TOKEN

_REQUEST_TIMEOUT = 30
_KNOWN_IMAGE_HOSTS = {
    "image.pollinations.ai",
    "picsum.photos",
    "fastly.picsum.photos",
    "images.unsplash.com",
    "raw.githubusercontent.com",
}


def _request_json(method: str, url: str, *, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.request(method, url, params=params, timeout=_REQUEST_TIMEOUT)
    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}

    if response.status_code >= 400:
        graph_error = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(graph_error, dict):
            message = graph_error.get("message", "Unknown Graph API error")
            code = graph_error.get("code", "?")
            subcode = graph_error.get("error_subcode", "?")
            raise RuntimeError(f"Facebook Graph API error {code}/{subcode}: {message}")
        response.raise_for_status()

    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(str(payload["error"]))
    return payload


def get_page_access_token(page_id: str) -> str:
    payload = _request_json(
        "GET",
        f"{BASE_URL}/me/accounts",
        params={"access_token": IG_ACCESS_TOKEN},
    )
    for page in payload.get("data", []):
        if page.get("id") == page_id:
            token = page.get("access_token", "")
            if token:
                return token
    raise RuntimeError(
        f"No page access token found for page_id={page_id}. Ensure the user token has pages permissions."
    )


def _looks_like_image_bytes(data: bytes) -> bool:
    if not data:
        return False
    signatures = (
        b"\xFF\xD8\xFF",  # JPEG
        b"\x89PNG\r\n\x1a\n",  # PNG
        b"GIF87a",  # GIF
        b"GIF89a",  # GIF
        b"RIFF",  # WebP (RIFF....WEBP)
    )
    if any(data.startswith(sig) for sig in signatures[:4]):
        return True
    return data.startswith(b"RIFF") and b"WEBP" in data[:16]


def _validate_public_image_url(image_url: str) -> None:
    # Facebook can only fetch publicly reachable direct image URLs.
    methods = ("HEAD", "GET")
    last_error: Exception | None = None
    saw_reachable_response = False

    for method in methods:
        try:
            response = requests.request(
                method,
                image_url,
                allow_redirects=True,
                timeout=_REQUEST_TIMEOUT,
                stream=(method == "GET"),
                headers={"Accept": "image/*,*/*;q=0.8"},
            )
            if response.status_code >= 400:
                continue

            saw_reachable_response = True
            content_type = (response.headers.get("content-type") or "").lower()
            if content_type.startswith("image/"):
                return

            if method == "GET":
                head_bytes = response.raw.read(32, decode_content=True)
                if _looks_like_image_bytes(head_bytes):
                    return
        except Exception as error:
            last_error = error

    host = urlparse(image_url).hostname or ""
    if saw_reachable_response and host in _KNOWN_IMAGE_HOSTS:
        # Some AI image/CDN providers return atypical content-type headers.
        return

    if last_error is not None:
        raise RuntimeError(
            "image_url is not publicly reachable as an image. "
            f"Last network error: {last_error}"
        )

    raise RuntimeError(
        "image_url is reachable but does not return a valid image file (HTTP < 400 with Content-Type image/* or image bytes)."
    )


def publish_photo(page_id: str, image_url: str, caption: str) -> dict[str, Any]:
    if not page_id:
        raise ValueError("page_id is required for Facebook page publishing.")
    if not image_url:
        raise ValueError("image_url is required and must be publicly reachable.")

    _validate_public_image_url(image_url)

    page_token = get_page_access_token(page_id)
    return _request_json(
        "POST",
        f"{BASE_URL}/{page_id}/photos",
        params={
            "url": image_url,
            "caption": caption,
            "published": "true",
            "access_token": page_token,
        },
    )
