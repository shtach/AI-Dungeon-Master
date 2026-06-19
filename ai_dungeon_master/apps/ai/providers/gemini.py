"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""

import logging

from django.conf import settings
from google import genai
from google.genai.errors import APIError, ClientError

from ai_dungeon_master.apps.ai.exceptions import (
    AIClientError,
    AIProviderError,
    AIRateLimitError,
)

logger = logging.getLogger("ai_dungeon_master.apps.ai")

DEFAULT_TEMPERATURE = 0.8
DEFAULT_MAX_TOKENS = 2048


def _is_rate_limit(exc) -> bool:
    """True when the provider error represents an HTTP 429 / quota exhaustion."""

    if getattr(exc, "code", None) == 429:
        return True
    text = str(exc)
    return "429" in text or "RESOURCE_EXHAUSTED" in text

class GeminiProvider:
    """
        LLM provider backed by Google Gemini via the google-genai SDK.

        Reads GEMINI_API_KEY and GEMINI_MODEL from Django settings.
        Raises AIClientError on configuration problems.
        Raises AIProviderError on API/network errors.
    """

    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not api_key:
            raise AIClientError(
                "ERROR with GEMINI_API_KEY. It is not set."
                "Add it to your .env file."
            )

        self._model = settings.GEMINI_MODEL
        self._client = genai.Client(api_key=api_key)

        logger.info("Gemini provider installed. Model=%s", self._model)

    def generate(self, prompt: str) -> str:
        """
            Send prompt to Gemini and return response text.

            Raises:
                AIProviderError: On any API or network failure.
        """

        logger.debug("Gemini req. | model: %s | prompt length: %s", self._model, len(prompt))

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=DEFAULT_TEMPERATURE,
                    max_output_tokens=DEFAULT_MAX_TOKENS,
                ),
            )

        except (APIError, ClientError) as exc:
            logger.error("Gemini API ERROR: %s", exc)
            if _is_rate_limit(exc):
                raise AIRateLimitError(f"Gemini rate limited (429): {exc}") from exc
            raise AIProviderError(f"Gemini returned an error: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected error calling Gemini: %s", exc)
            raise AIProviderError(f"Unexpected provider error: {exc}") from exc

        result = response.text

        if not result:
            raise AIProviderError(
                "Gemini returned an empty response. "
                "The prompt may have been blocked by safety filters."
            )

        logger.debug("Gemini response | response_len=%d", len(result))
        return result

