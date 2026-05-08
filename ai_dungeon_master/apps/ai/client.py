"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""

import logging

from django.conf import settings

from ai_dungeon_master.apps.ai.base import BaseLLMClient
from ai_dungeon_master.apps.ai.exceptions import AIClientError

logger = logging.getLogger("ai_dungeon_master.apps.ai")

def get_ai_client() -> BaseLLMClient:
    """
        Return the configured LLM provider instance.

        Provider is selected by the AI_PROVIDER env var (via settings):
            gemini  — GeminiProvider (default)
            mock    — MockProvider (tests / local dev without API key)

        Raises:
            AIClientError: If AI_PROVIDER value is not recognized.
    """

    provider = getattr(settings, "AI_PROVIDER", "gemini").lower()
    logger.info("AI provider selected: %s", provider)

    if provider == "gemini":
        from ai_dungeon_master.apps.ai.providers.gemini import GeminiProvider
        return GeminiProvider()

    if provider == "mock":
        from ai_dungeon_master.apps.ai.providers.mock import MockProvider
        return MockProvider()

    raise AIClientError(
        f"Unknown AI_PROVIDER='{provider}'. "
        "Supported values: 'gemini', 'mock'."
    )