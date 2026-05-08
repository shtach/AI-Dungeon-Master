"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""

from typing import Protocol

class BaseLLMClient(Protocol):
    """
        Provider-agnostic interface for all LLM clients.

        Any class implementing this protocol can be used as a drop-in replacement.
        No inheritance required — structural subtyping (duck typing + type checking).
    """

    def generate(self, prompt: str) -> str:
        """
            Send a prompt to the LLM and return the response as a plain string.

            Args:
                prompt: The full prompt text to send to the model.

            Returns:
                Non-empty string response from the model.

            Raises:
                AIClientError: Configuration problem (missing key, bad provider).
                AIProviderError: Provider returned an error or is unreachable.
        """
        ...