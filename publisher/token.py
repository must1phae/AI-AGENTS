from __future__ import annotations

from typing import Any

import requests

from config.settings import GRAPH_API_VERSION

_REQUEST_TIMEOUT = 30


def exchange_for_long_lived_token(app_id: str, app_secret: str, short_lived_token: str) -> dict[str, Any]:
    response = requests.get(
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_lived_token,
        },
        timeout=_REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()
