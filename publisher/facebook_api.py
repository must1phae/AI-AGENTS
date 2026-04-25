from __future__ import annotations

from typing import Any

import requests

from config.settings import BASE_URL, IG_ACCESS_TOKEN

_REQUEST_TIMEOUT = 30


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


def _validate_public_image_url(image_url: str) -> None:
    # Facebook can only fetch publicly reachable direct image URLs.
    methods = ("HEAD", "GET")
    last_error: Exception | None = None

    for method in methods:
        try:
            response = requests.request(
                method,
                image_url,
                allow_redirects=True,
                timeout=_REQUEST_TIMEOUT,
                stream=(method == "GET"),
            )
            if response.status_code >= 400:
                continue

            content_type = (response.headers.get("content-type") or "").lower()
            if content_type.startswith("image/"):
                return
        except Exception as error:
            last_error = error

    if last_error is not None:
        raise RuntimeError(
            "image_url is not publicly reachable as an image. "
            f"Last network error: {last_error}"
        )

    raise RuntimeError(
        "image_url is reachable but does not return a valid image file (HTTP < 400 with Content-Type image/*)."
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
