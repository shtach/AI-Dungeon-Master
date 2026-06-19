"""

    Tests for per-call AI usage metering.

"""

from unittest.mock import patch, MagicMock

import pytest
from django.test import override_settings
from google.genai.errors import ClientError

from ai_dungeon_master.apps.ai.client import get_ai_client
from ai_dungeon_master.apps.ai.exceptions import AIProviderError
from ai_dungeon_master.apps.ai.metering import (
    MeteredClient,
    UsageRecord,
    UsageStatus,
    estimate_tokens,
)


pytestmark = pytest.mark.django_db


class _FakeProvider:
    """Stand-in for any provider (e.g. Ollama) with a private _model attr."""

    def __init__(self, response="ok", error=None, model="gemma3"):
        self._model = model
        self._response = response
        self._error = error

    def generate(self, prompt: str) -> str:
        if self._error is not None:
            raise self._error
        return self._response


class TestEstimateTokens:
    def test_empty_prompt_is_zero(self):
        assert estimate_tokens("") == 0

    def test_short_prompt_is_at_least_one(self):
        assert estimate_tokens("hi") == 1

    def test_scales_with_length(self):
        assert estimate_tokens("x" * 40) == 10


class TestUsageRecorded:
    def test_usage_recorded_per_call(self):
        """Every generate() call emits exactly one usage record."""

        client = MeteredClient(_FakeProvider(response="You enter a dungeon."), provider="mock")
        client.generate("Describe the room please.")

        assert UsageRecord.objects.count() == 1
        record = UsageRecord.objects.get()
        assert record.provider == "mock"
        assert record.model == "gemma3"
        assert record.prompt_tokens_est > 0
        assert record.latency_ms >= 0
        assert record.status == UsageStatus.OK

    def test_ollama_call_is_metered(self):
        """The wrapper meters any provider, including a local Ollama engine."""

        client = MeteredClient(_FakeProvider(model="gemma3"), provider="ollama")
        client.generate("A long prompt that the dungeon master must answer.")

        record = UsageRecord.objects.get()
        assert record.provider == "ollama"
        assert record.model == "gemma3"
        assert record.status == UsageStatus.OK

    def test_provider_error_flagged_as_error(self):
        client = MeteredClient(
            _FakeProvider(error=AIProviderError("boom")), provider="ollama"
        )
        with pytest.raises(AIProviderError):
            client.generate("anything")

        assert UsageRecord.objects.get().status == UsageStatus.ERROR

    def test_model_falls_back_to_provider_when_absent(self):
        class _NoModel:
            def generate(self, prompt):
                return "ok"

        MeteredClient(_NoModel(), provider="mock").generate("hi there")
        assert UsageRecord.objects.get().model == "mock"


class TestRateLimitFlagged:
    @override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="fake-key")
    @patch("ai_dungeon_master.apps.ai.providers.gemini.genai.Client")
    def test_429_flagged(self, mock_genai_client):
        """A 429 from the provider is recorded distinctly as rate_limited."""

        rate_limit_error = ClientError(
            429,
            {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "quota"}},
        )
        mock_genai_client.return_value.models.generate_content.side_effect = (
            rate_limit_error
        )

        client = get_ai_client()  # MeteredClient wrapping GeminiProvider
        with pytest.raises(AIProviderError):  # AIRateLimitError is a subclass
            client.generate("Describe the scene.")

        record = UsageRecord.objects.get()
        assert record.provider == "gemini"
        assert record.status == UsageStatus.RATE_LIMITED

    @override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="fake-key")
    @patch("ai_dungeon_master.apps.ai.providers.gemini.genai.Client")
    def test_non_429_error_is_plain_error(self, mock_genai_client):
        other_error = ClientError(
            400,
            {"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "bad"}},
        )
        mock_genai_client.return_value.models.generate_content.side_effect = other_error

        client = get_ai_client()
        with pytest.raises(AIProviderError):
            client.generate("Describe the scene.")

        assert UsageRecord.objects.get().status == UsageStatus.ERROR


class TestAggregations:
    def test_recent_rates_counts_requests_and_tokens(self):
        client = MeteredClient(_FakeProvider(), provider="ollama")
        client.generate("a prompt of some length here")
        client.generate("another prompt here")

        rates = UsageRecord.recent_rates()
        assert rates["rpm"] == 2
        assert rates["tpm"] > 0
        assert rates["rpd"] == 2
        assert rates["rate_limited_last_day"] == 0

    def test_per_minute_buckets(self):
        MeteredClient(_FakeProvider(), provider="ollama").generate("hello world")
        buckets = UsageRecord.per_minute()
        assert len(buckets) == 1
        assert buckets[0]["requests"] == 1
