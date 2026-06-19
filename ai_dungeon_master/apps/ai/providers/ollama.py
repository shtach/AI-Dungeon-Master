"""Local Ollama LLM provider behind the BaseLLMClient interface."""

import logging

import httpx
from django.conf import settings

from ai_dungeon_master.apps.ai.exceptions import AIClientError, AIProviderError

logger = logging.getLogger("ai_dungeon_master.apps.ai")

DEFAULT_TEMPERATURE = 0.8
# The first call after a cold start loads the model into memory and can take
# tens of seconds, so the timeout is deliberately generous.
DEFAULT_TIMEOUT = 120.0


class OllamaProvider:
    """
        LLM provider backed by a local Ollama engine via its HTTP API.

        Reads OLLAMA_HOST and OLLAMA_MODEL from Django settings.
        Raises AIClientError on configuration problems (server unreachable,
        model not pulled). Raises AIProviderError on runtime errors
        (HTTP 5xx, timeout, malformed body).
    """

    def __init__(self):
        self._host = getattr(settings, "OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        self._model = getattr(settings, "OLLAMA_MODEL", "gemma3")

        logger.info("Ollama provider installed. host=%s model=%s", self._host, self._model)

    def generate(self, prompt: str) -> str:
        """
            Send prompt to Ollama and return response text.

            Raises:
                AIClientError: Server unreachable or model not pulled.
                AIProviderError: HTTP 5xx, timeout, or malformed response.
        """

        url = f"{self._host}/api/generate"
        logger.debug("Ollama req. | model: %s | prompt length: %s", self._model, len(prompt))

        try:
            response = httpx.post(
                url,
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": DEFAULT_TEMPERATURE},
                },
                timeout=DEFAULT_TIMEOUT,
            )
        except httpx.ConnectError as exc:
            # Connection refused — the Ollama server is not running/reachable.
            logger.error("Ollama unreachable at %s: %s", self._host, exc)
            raise AIClientError(
                f"Cannot reach Ollama at {self._host}. "
                "Is the Ollama server running?"
            ) from exc
        except httpx.HTTPError as exc:
            # Timeouts and other transport errors are runtime failures.
            logger.error("Ollama transport error: %s", exc)
            raise AIProviderError(f"Ollama request failed: {exc}") from exc

        # 404 means the model name is not pulled — a configuration problem.
        if response.status_code == 404:
            logger.error("Ollama model not pulled: %s", self._model)
            raise AIClientError(
                f"Ollama model '{self._model}' is not available. "
                f"Pull it first: `ollama pull {self._model}`."
            )

        if response.status_code >= 500:
            logger.error("Ollama server error %s: %s", response.status_code, response.text)
            raise AIProviderError(f"Ollama returned HTTP {response.status_code}.")

        try:
            data = response.json()
            result = data["response"]
        except (ValueError, KeyError) as exc:
            logger.error("Ollama malformed response body: %s", exc)
            raise AIProviderError("Ollama returned a malformed response body.") from exc

        if not result:
            raise AIProviderError("Ollama returned an empty response.")

        logger.debug("Ollama response | response_len=%d", len(result))
        return result
