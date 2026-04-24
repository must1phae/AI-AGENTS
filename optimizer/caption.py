from __future__ import annotations

import re

from config.settings import MAX_HASHTAGS

_HASHTAG_PATTERN = re.compile(r"#\w+")
_WHITESPACE_PATTERN = re.compile(r"[ \t]+")


def optimize(caption: str) -> str:
    cleaned = caption.strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _WHITESPACE_PATTERN.sub(" ", cleaned)

    hashtags = _HASHTAG_PATTERN.findall(cleaned)
    if len(hashtags) > MAX_HASHTAGS:
        for tag in hashtags[MAX_HASHTAGS:]:
            cleaned = cleaned.replace(tag, "")

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\s*(#\w+)", r"\n\1", cleaned, count=1)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned
