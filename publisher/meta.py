from __future__ import annotations

from typing import Any

import requests

from config.settings import GRAPH_API_VERSION

_REQUEST_TIMEOUT = 30


def list_pages(access_token: str) -> dict[str, Any]:
    response = requests.get(
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/accounts",
        params={"access_token": access_token},
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def get_instagram_business_account(page_id: str, access_token: str) -> dict[str, Any]:
    response = requests.get(
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}",
        params={
            "fields": "instagram_business_account",
            "access_token": access_token,
        },
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()
