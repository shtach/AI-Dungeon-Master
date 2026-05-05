"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""

from unittest.mock import patch, MagicMock

import pytest
from django.test import override_settings

from ai_dungeon_master.apps.ai.client import get_ai_client
from ai_dungeon_master.apps.ai.exceptions import AIClientError, AIProviderError
from ai_dungeon_master.apps.ai.providers.mock import MockProvider

class TestMockProvider:
    def test_returns_configured_response(self):
        client = MockProvider(response="You enter a dark dungeon.")
        assert client.generate("Describe the room.") == "You enter a dark dungeon."

    def test_raises_ai_provider_error_when_configured(self):
        client = MockProvider(raise_error=True)
        with pytest.raises(AIProviderError):
            client.generate("anything")


class TestGetAiClient:
    @override_settings(AI_PROVIDER="mock")
    def test_returns_mock_provider(self):
        client = get_ai_client()
        assert isinstance(client, MockProvider)

    @override_settings(AI_PROVIDER="unknown_provider")
    def test_raises_for_unknown_provider(self):
        with pytest.raises(AIClientError, match="Unknown AI_PROVIDER"):
            get_ai_client()

    @override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="")
    def test_gemini_raises_when_api_key_missing(self):
        with pytest.raises(AIClientError, match="GEMINI_API_KEY"):
            get_ai_client()

    @override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="fake-key")
    @patch("ai_dungeon_master.apps.ai.providers.gemini.genai.Client")
    def test_gemini_generate_returns_string(self, mock_genai_client):
        mock_response = MagicMock()
        mock_response.text = "You stand before a crumbling fortress."
        mock_genai_client.return_value.models.generate_content.return_value = mock_response

        client = get_ai_client()
        result = client.generate("Describe the scene.")

        assert result == "You stand before a crumbling fortress."

    @override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="fake-key")
    @patch("ai_dungeon_master.apps.ai.providers.gemini.genai.Client")
    def test_gemini_raises_on_empty_response(self, mock_genai_client):
        mock_response = MagicMock()
        mock_response.text = None
        mock_genai_client.return_value.models.generate_content.return_value = mock_response

        client = get_ai_client()
        with pytest.raises(AIProviderError, match="empty response"):
            client.generate("Describe the scene.")