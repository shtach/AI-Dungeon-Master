"""

    Created by shtach
    Date: 5 May 2026
    Modified: -

"""

from unittest.mock import patch, MagicMock

import httpx
import pytest
from django.test import override_settings

from ai_dungeon_master.apps.ai.client import get_ai_client
from ai_dungeon_master.apps.ai.exceptions import AIClientError, AIProviderError
from ai_dungeon_master.apps.ai.metering import MeteredClient
from ai_dungeon_master.apps.ai.providers.mock import MockProvider
from ai_dungeon_master.apps.ai.providers.ollama import OllamaProvider

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
        assert isinstance(client, MeteredClient)
        assert isinstance(client._inner, MockProvider)

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

    @override_settings(AI_PROVIDER="ollama")
    def test_returns_ollama_provider(self):
        client = get_ai_client()
        assert isinstance(client, MeteredClient)
        assert isinstance(client._inner, OllamaProvider)


class TestOllamaProvider:
    @override_settings(OLLAMA_HOST="http://localhost:11434", OLLAMA_MODEL="gemma3")
    @patch("ai_dungeon_master.apps.ai.providers.ollama.httpx.post")
    def test_generate_returns_text(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "A dragon blocks the path."}
        mock_post.return_value = mock_response

        client = OllamaProvider()
        assert client.generate("Describe the scene.") == "A dragon blocks the path."

    @override_settings(OLLAMA_HOST="http://localhost:11434", OLLAMA_MODEL="gemma3")
    @patch("ai_dungeon_master.apps.ai.providers.ollama.httpx.post")
    def test_connection_error_is_client_error(self, mock_post):
        # Connection refused → the server is unreachable → config problem.
        mock_post.side_effect = httpx.ConnectError("Connection refused")

        client = OllamaProvider()
        with pytest.raises(AIClientError):
            client.generate("Describe the scene.")

    @override_settings(OLLAMA_HOST="http://localhost:11434", OLLAMA_MODEL="gemma3")
    @patch("ai_dungeon_master.apps.ai.providers.ollama.httpx.post")
    def test_model_not_pulled_is_client_error(self, mock_post):
        # 404 → the model name is not pulled → config problem.
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        client = OllamaProvider()
        with pytest.raises(AIClientError, match="ollama pull"):
            client.generate("Describe the scene.")

    @override_settings(OLLAMA_HOST="http://localhost:11434", OLLAMA_MODEL="gemma3")
    @patch("ai_dungeon_master.apps.ai.providers.ollama.httpx.post")
    def test_http500_is_provider_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "internal server error"
        mock_post.return_value = mock_response

        client = OllamaProvider()
        with pytest.raises(AIProviderError):
            client.generate("Describe the scene.")

    @override_settings(OLLAMA_HOST="http://localhost:11434", OLLAMA_MODEL="gemma3")
    @patch("ai_dungeon_master.apps.ai.providers.ollama.httpx.post")
    def test_timeout_is_provider_error(self, mock_post):
        mock_post.side_effect = httpx.ReadTimeout("timed out")

        client = OllamaProvider()
        with pytest.raises(AIProviderError):
            client.generate("Describe the scene.")

    @override_settings(OLLAMA_HOST="http://localhost:11434", OLLAMA_MODEL="gemma3")
    @patch("ai_dungeon_master.apps.ai.providers.ollama.httpx.post")
    def test_empty_response_is_provider_error(self, mock_post):
        # 200 OK but an empty "response" field → runtime problem.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": ""}
        mock_post.return_value = mock_response

        client = OllamaProvider()
        with pytest.raises(AIProviderError, match="empty response"):
            client.generate("Describe the scene.")

    @override_settings(OLLAMA_HOST="http://localhost:11434", OLLAMA_MODEL="gemma3")
    @patch("ai_dungeon_master.apps.ai.providers.ollama.httpx.post")
    def test_malformed_body_is_provider_error(self, mock_post):
        # 200 OK but the body is missing the "response" key → runtime problem.
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "shape"}
        mock_post.return_value = mock_response

        client = OllamaProvider()
        with pytest.raises(AIProviderError, match="malformed"):
            client.generate("Describe the scene.")