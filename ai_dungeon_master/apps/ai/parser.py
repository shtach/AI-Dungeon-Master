import logging
import re
from typing import Any

logger = logging.getLogger("ai_dungeon_master.apps.ai.parser")

NARRATIVE_MAX_CHARS = 400
LABEL_MAX_WORDS = 6
DETAIL_MAX_WORDS = 12
MAX_CARDS = 4

_TAG_RE = re.compile(r"\[(\w+)\]([^\[]*)")

_STAT_KEYS = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}


def _clamp_words(text: str | None, max_words: int) -> str | None:
    if not text:
        return None
    text = text.strip()
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = " ".join(words[:max_words])
    logger.debug("Truncated text to %d words: %r -> %r", max_words, text, truncated)
    return truncated


def _clamp_narrative(text: str | None) -> str | None:
    if not text:
        return None
    text = text.strip()
    if len(text) <= NARRATIVE_MAX_CHARS:
        return text

    truncated = text[:NARRATIVE_MAX_CHARS]
    last_period = truncated.rfind(".")
    last_excl = truncated.rfind("!")
    last_q = truncated.rfind("?")
    boundary = max(last_period, last_excl, last_q)

    if boundary > NARRATIVE_MAX_CHARS // 2:
        truncated = truncated[: boundary + 1]
    else:
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]

    logger.debug("Clamped narrative from %d to %d chars", len(text), len(truncated))
    return truncated
