"""

    Per-call AI usage metering.

    Every AI provider call emits exactly one usage record so the team can watch
    RPM / TPM / RPD trends (like the AI Studio console). A record captures the
    provider, model, an approximate prompt token count, latency and a status —
    with rate limits (HTTP 429) flagged distinctly from other failures.

"""

import time
import logging
from contextlib import contextmanager
from datetime import timedelta

from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncMinute, TruncDay
from django.utils import timezone

from ai_dungeon_master.apps.ai.exceptions import AIRateLimitError

logger = logging.getLogger("ai_dungeon_master.apps.ai")

# Rough heuristic: ~4 characters per token. Good enough to spot TPM trends
# without paying for a real tokenizer round-trip on every call.
CHARS_PER_TOKEN = 4


class UsageStatus(models.TextChoices):
    OK = "ok", "OK"
    ERROR = "error", "Error"
    RATE_LIMITED = "rate_limited", "Rate limited (429)"


def estimate_tokens(text: str) -> int:
    """
        Approximate the number of prompt tokens in ``text``.

        Uses a simple chars-per-token heuristic; non-empty prompts count as at
        least one token.
    """

    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


class UsageRecord(models.Model):
    """
        One row per AI provider call.

        Rows are append-only; aggregation helpers roll them up into per-minute
        and per-day buckets for the admin / JSON views.
    """

    provider = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    prompt_tokens_est = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=UsageStatus.choices, default=UsageStatus.OK
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["provider", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.created_at:%Y-%m-%d %H:%M:%S} {self.provider}/{self.model} "
            f"{self.status} ({self.latency_ms}ms)"
        )

    @classmethod
    def recent_rates(cls, *, now=None) -> dict:
        """Current request/token rates over the last minute and last day."""

        now = now or timezone.now()
        last_minute = cls.objects.filter(created_at__gte=now - timedelta(minutes=1))
        last_day = cls.objects.filter(created_at__gte=now - timedelta(days=1))

        return {
            "rpm": last_minute.count(),
            "tpm": last_minute.aggregate(t=Sum("prompt_tokens_est"))["t"] or 0,
            "rpd": last_day.count(),
            "rate_limited_last_day": last_day.filter(
                status=UsageStatus.RATE_LIMITED
            ).count(),
        }

    @classmethod
    def per_minute(cls, *, since=None) -> list:
        """Per-minute request / token counts, oldest bucket first."""

        return cls._buckets(TruncMinute, since)

    @classmethod
    def per_day(cls, *, since=None) -> list:
        """Per-day request / token counts, oldest bucket first."""

        return cls._buckets(TruncDay, since)

    @classmethod
    def _buckets(cls, trunc, since) -> list:
        qs = cls.objects.all()
        if since is not None:
            qs = qs.filter(created_at__gte=since)
        return list(
            qs.annotate(bucket=trunc("created_at"))
            .values("bucket")
            .annotate(
                requests=Count("id"),
                tokens=Sum("prompt_tokens_est"),
                rate_limited=Count(
                    "id", filter=models.Q(status=UsageStatus.RATE_LIMITED)
                ),
            )
            .order_by("bucket")
        )


def record_usage(*, provider, model, prompt_tokens_est, latency_ms, status) -> "UsageRecord | None":
    """
        Persist a single usage record and emit a structured log line.

        Metering must never break a real AI call, so a failure to write the row
        is logged and swallowed rather than propagated.
    """

    logger.info(
        "ai.usage provider=%s model=%s tokens_est=%s latency_ms=%s status=%s",
        provider,
        model,
        prompt_tokens_est,
        latency_ms,
        status,
    )

    try:
        return UsageRecord.objects.create(
            provider=provider,
            model=model,
            prompt_tokens_est=prompt_tokens_est,
            latency_ms=latency_ms,
            status=status,
        )
    except Exception:  # pragma: no cover - defensive, metering is best-effort
        logger.exception("Failed to persist AI usage record")
        return None


class MeteredClient:
    """
        Wraps any BaseLLMClient so every generate() call emits one usage record.

        Provider-agnostic on purpose: get_ai_client() wraps whatever provider it
        builds, so Gemini, Ollama, Mock and any future provider are metered the
        same way without touching their code. The model name is read from the
        wrapped provider's ``_model`` attribute, falling back to the provider
        slug when it has none.
    """

    def __init__(self, inner, *, provider: str):
        self._inner = inner
        self._provider = provider

    def generate(self, prompt: str) -> str:
        model = getattr(self._inner, "_model", self._provider)
        with track_usage(provider=self._provider, model=model, prompt=prompt):
            return self._inner.generate(prompt)


@contextmanager
def track_usage(*, provider: str, model: str, prompt: str):
    """
        Wrap a provider ``generate()`` call so it emits exactly one usage record.

        Measures latency, classifies the outcome (OK / ERROR / RATE_LIMITED) and
        always records — even when the wrapped call raises — before re-raising.
        ``AIRateLimitError`` (HTTP 429) is flagged distinctly from other errors.
    """

    start = time.perf_counter()
    status = UsageStatus.OK
    try:
        yield
    except AIRateLimitError:
        status = UsageStatus.RATE_LIMITED
        raise
    except Exception:
        status = UsageStatus.ERROR
        raise
    finally:
        latency_ms = int(round((time.perf_counter() - start) * 1000))
        record_usage(
            provider=provider,
            model=model,
            prompt_tokens_est=estimate_tokens(prompt),
            latency_ms=latency_ms,
            status=status,
        )
