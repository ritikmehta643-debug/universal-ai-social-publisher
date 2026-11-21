import logging
from typing import Optional, Tuple, Dict, Any
from .base import BaseImageProvider
from .dalle import DalleImageProvider
from .gemini_imagen import GeminiImagenProvider
from .huggingface_image import HuggingFaceImageProvider
from .custom_image import CustomImageProvider
from ...database import get_db

logger = logging.getLogger(__name__)

IMAGE_CLASSES = {
    "dalle": DalleImageProvider,
    "gemini": GeminiImagenProvider,
    "huggingface": HuggingFaceImageProvider,
    "custom": CustomImageProvider,
}

def create_image_provider_instance(record: Dict[str, Any]) -> BaseImageProvider:
    ptype = record.get("provider_type", "").lower()
    cls = IMAGE_CLASSES.get(ptype, CustomImageProvider)
    return cls(
        name=record.get("name", "Unknown"),
        api_key=record.get("api_key", ""),
        api_endpoint=record.get("api_endpoint", ""),
        model=record.get("model", ""),
        aspect_ratio=record.get("aspect_ratio", "1:1"),
        resolution=record.get("resolution", "1024x1024"),
        style=record.get("style", "photorealistic documentary"),
        negative_prompt=record.get("negative_prompt", "")
    )

def get_active_image_provider(provider_id: Optional[int] = None) -> Tuple[Optional[BaseImageProvider], Optional[BaseImageProvider]]:
    with get_db() as conn:
        primary_record = None
        fallback_record = None

        if provider_id:
            primary_record = conn.execute(
                "SELECT * FROM image_providers WHERE id = ? AND is_enabled = 1", (provider_id,)
            ).fetchone()

        if not primary_record:
            primary_record = conn.execute(
                "SELECT * FROM image_providers WHERE is_default = 1 AND is_enabled = 1 LIMIT 1"
            ).fetchone()

        if not primary_record:
            primary_record = conn.execute(
                "SELECT * FROM image_providers WHERE is_enabled = 1 AND api_key != '' LIMIT 1"
            ).fetchone()

        fallback_record = conn.execute(
            "SELECT * FROM image_providers WHERE is_fallback = 1 AND is_enabled = 1 LIMIT 1"
        ).fetchone()

    primary = create_image_provider_instance(primary_record) if primary_record else None
    fallback = create_image_provider_instance(fallback_record) if fallback_record and (not primary_record or fallback_record["id"] != primary_record["id"]) else None
    return primary, fallback

def generate_image_with_fallback(prompt: str, provider_id: Optional[int] = None) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Attempts to generate an image using primary or fallback provider.
    Returns: (remote_url, local_path, provider_name_used, error_or_none)
    If unavailable or fails, returns (None, None, None, error_message)
    so the post can be marked 'pending' without crashing.
    """
    primary, fallback = get_active_image_provider(provider_id)
    if not primary and not fallback:
        return None, None, None, "No active image provider configured. Post placed in pending status."

    if primary:
        try:
            logger.info(f"Generating image with primary provider: {primary.name}")
            url, local_path = primary.generate_image(prompt)
            return url, local_path, primary.name, None
        except Exception as e:
            logger.warning(f"Primary image provider {primary.name} failed: {e}")
            if not fallback:
                return None, None, primary.name, f"Primary image generation failed: {str(e)}"

    if fallback:
        try:
            logger.info(f"Generating image with fallback provider: {fallback.name}")
            url, local_path = fallback.generate_image(prompt)
            return url, local_path, fallback.name, None
        except Exception as e:
            logger.error(f"Fallback image provider {fallback.name} failed: {e}")
            return None, None, fallback.name, f"Both primary and fallback image generation failed: {str(e)}"

    return None, None, None, "Image generation could not be completed."
