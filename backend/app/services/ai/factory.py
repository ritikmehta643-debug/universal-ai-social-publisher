import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from .base import BaseAIProvider
from .gemini import GoogleGeminiProvider
from .openai_provider import OpenAIProvider
from .claude import AnthropicClaudeProvider
from .groq import GroqProvider
from .openrouter import OpenRouterProvider
from .huggingface import HuggingFaceProvider
from .custom import CustomAIProvider
from ...database import get_db

logger = logging.getLogger(__name__)

PROVIDER_CLASSES = {
    "gemini": GoogleGeminiProvider,
    "openai": OpenAIProvider,
    "claude": AnthropicClaudeProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "huggingface": HuggingFaceProvider,
    "custom": CustomAIProvider,
}

def create_provider_instance(record: Dict[str, Any]) -> BaseAIProvider:
    ptype = record.get("provider_type", "").lower()
    cls = PROVIDER_CLASSES.get(ptype, CustomAIProvider)
    return cls(
        name=record.get("name", "Unknown"),
        api_key=record.get("api_key", ""),
        api_endpoint=record.get("api_endpoint", ""),
        model=record.get("model", "")
    )

def get_active_provider(provider_id: Optional[int] = None) -> Tuple[BaseAIProvider, Optional[BaseAIProvider]]:
    """Returns (primary_provider, fallback_provider)."""
    with get_db() as conn:
        primary_record = None
        fallback_record = None

        if provider_id:
            primary_record = conn.execute(
                "SELECT * FROM ai_providers WHERE id = ? AND is_enabled = 1", (provider_id,)
            ).fetchone()

        if not primary_record:
            # Pick default provider
            primary_record = conn.execute(
                "SELECT * FROM ai_providers WHERE is_default = 1 AND is_enabled = 1 LIMIT 1"
            ).fetchone()

        if not primary_record:
            # Fall back to any enabled provider with an API key
            primary_record = conn.execute(
                "SELECT * FROM ai_providers WHERE is_enabled = 1 AND api_key != '' LIMIT 1"
            ).fetchone()

        # Find designated fallback provider
        fallback_record = conn.execute(
            "SELECT * FROM ai_providers WHERE is_fallback = 1 AND is_enabled = 1 LIMIT 1"
        ).fetchone()

    if not primary_record:
        raise RuntimeError("No enabled AI provider found. Please configure and enable at least one provider in AI Settings.")

    primary = create_provider_instance(primary_record)
    fallback = create_provider_instance(fallback_record) if fallback_record and fallback_record["id"] != primary_record["id"] else None
    return primary, fallback

def generate_with_fallback(prompt: str, system_prompt: str = "", provider_id: Optional[int] = None) -> Tuple[str, str]:
    """Tries primary provider first; if it fails, tries fallback. Returns (content, provider_name_used)."""
    primary, fallback = get_active_provider(provider_id)
    try:
        logger.info(f"Generating content with primary AI provider: {primary.name}")
        content = primary.generate_text(prompt, system_prompt=system_prompt)
        return content, primary.name
    except Exception as e:
        logger.warning(f"Primary provider {primary.name} failed: {e}")
        if fallback:
            logger.info(f"Switching to fallback AI provider: {fallback.name}")
            content = fallback.generate_text(prompt, system_prompt=system_prompt)
            return content, fallback.name
        raise RuntimeError(f"Primary provider {primary.name} failed: {e}. No fallback available.")
