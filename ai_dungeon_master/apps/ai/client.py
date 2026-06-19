"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""

import logging

from django.conf import settings

from ai_dungeon_master.apps.ai.base import BaseLLMClient
from ai_dungeon_master.apps.ai.exceptions import AIClientError
from ai_dungeon_master.apps.ai.metering import MeteredClient

logger = logging.getLogger("ai_dungeon_master.apps.ai")

def get_ai_client() -> BaseLLMClient:
    """
        Return the configured LLM provider, wrapped so every call is metered.

        Provider is selected by the AI_PROVIDER env var (via settings):
            gemini  — GeminiProvider (default)
            ollama  — OllamaProvider (local Ollama engine)
            mock    — MockProvider (tests / local dev without API key)

        The chosen provider is wrapped in MeteredClient so each generate() call
        emits one usage record, regardless of which provider is active.

        Raises:
            AIClientError: If AI_PROVIDER value is not recognized.
    """

    provider = getattr(settings, "AI_PROVIDER", "gemini").lower()
    logger.info("AI provider selected: %s", provider)

    return MeteredClient(_build_provider(provider), provider=provider)


def _build_provider(provider: str) -> BaseLLMClient:
    """Construct the raw (un-metered) provider selected by ``provider``."""

    if provider == "gemini":
        from ai_dungeon_master.apps.ai.providers.gemini import GeminiProvider
        return GeminiProvider()

    if provider == "ollama":
        from ai_dungeon_master.apps.ai.providers.ollama import OllamaProvider
        return OllamaProvider()

    if provider == "mock":
        from ai_dungeon_master.apps.ai.providers.mock import MockProvider
        return MockProvider()

    raise AIClientError(
        f"Unknown AI_PROVIDER='{provider}'. "
        "Supported values: 'gemini', 'ollama', 'mock'."
    )