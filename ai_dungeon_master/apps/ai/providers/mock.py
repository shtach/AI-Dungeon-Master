"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""

from ai_dungeon_master.apps.ai.exceptions import AIProviderError

class MockProvider:
    """
        Fake LLM provider for use in unit tests.

        Returns predictable responses without making any network calls.
        Can be configured to raise AIProviderError to test error handling.
    """

    def __init__(self, response: str = "Mock response", raise_error: bool = False):
        self._response = response
        self._raise_error = raise_error

    def generate(self, prompt: str) -> str:
        if self._raise_error:
            raise AIProviderError("Mock provider ERR.")
        return self._response