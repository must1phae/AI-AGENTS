from __future__ import annotations

import argparse
import sys
from typing import Any

from config.settings import DEFAULT_IMAGE_URL, FACEBOOK_PAGE_ID, PUBLISH_TARGET
from generator.content import generate_caption, test_gemini_connection
from optimizer.caption import optimize
from publisher.facebook_api import publish_photo
from publisher.instagram_api import create_media_container, publish_media, wait_for_container_ready


def run_agent(
    image_url: str | None = None,
    publish: bool = True,
    manual_caption: str | None = None,
) -> dict[str, Any]:
    selected_image_url = image_url or DEFAULT_IMAGE_URL
    if not selected_image_url:
        raise ValueError("No image URL provided. Set DEFAULT_IMAGE_URL or pass --image-url.")

    if manual_caption:
        print("Using provided caption...")
        raw_caption = manual_caption
    else:
        print("Generating caption...")
        raw_caption = generate_caption()
    caption = optimize(raw_caption)
    print("Caption ready:")
    print(caption)

    if not publish:
        return {"caption": caption, "image_url": selected_image_url, "published": False}

    target = PUBLISH_TARGET
    if target == "facebook":
        print("Publishing on Facebook Page...")
        if not FACEBOOK_PAGE_ID:
            raise ValueError("FACEBOOK_PAGE_ID is required when PUBLISH_TARGET=facebook.")
        result = publish_photo(FACEBOOK_PAGE_ID, selected_image_url, caption)
        post_id = result.get("post_id") or result.get("id", "")
        print(f"Published successfully on Facebook: {post_id}")
        return {
            "caption": caption,
            "image_url": selected_image_url,
            "post_id": post_id,
            "published": True,
            "target": "facebook",
            "result": result,
        }

    print("Publishing on Instagram...")
    container_id = create_media_container(selected_image_url, caption)
    wait_for_container_ready(container_id)
    result = publish_media(container_id)
    post_id = result.get("id", "")
    print(f"Published successfully: {post_id}")

    return {
        "caption": caption,
        "image_url": selected_image_url,
        "container_id": container_id,
        "post_id": post_id,
        "published": True,
        "target": "instagram",
        "result": result,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and publish an Instagram post.")
    parser.add_argument("--image-url", default=None, help="Public URL of the image to publish.")
    parser.add_argument("--dry-run", action="store_true", help="Generate the caption without publishing.")
    parser.add_argument("--test-gemini", action="store_true", help="Test Gemini API connectivity and exit.")
    parser.add_argument(
        "--caption",
        default=None,
        help="Optional manual caption to bypass LLM generation for testing.",
    )
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    if args.test_gemini:
        print("Testing Gemini connection...")
        try:
            response = test_gemini_connection()
            print(f"Gemini OK: {response}")
        except Exception as error:
            print(f"Gemini test failed: {error}")
            sys.exit(1)
        sys.exit(0)

    run_agent(image_url=args.image_url, publish=not args.dry_run, manual_caption=args.caption)
