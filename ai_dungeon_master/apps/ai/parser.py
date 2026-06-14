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


_ROLL_RE = re.compile(r"roll=(\w+)")
_DC_RE = re.compile(r"dc=(\d+)")
_REQUIRES_RE = re.compile(r"requires=(\w+)")


def _parse_card(raw: str) -> dict[str, Any]:
    parts = [p.strip() for p in raw.split("|")]

    label = _clamp_words(parts[0] if parts else "", LABEL_MAX_WORDS)
    roll = None
    dc = None
    requires = None
    detail = None

    if len(parts) >= 2:
        field_str = parts[1]
        m_roll = _ROLL_RE.search(field_str)
        if m_roll:
            stat = m_roll.group(1).lower()
            if stat in _STAT_KEYS:
                roll = stat

        m_dc = _DC_RE.search(field_str)
        if m_dc:
            dc = int(m_dc.group(1))

        m_req = _REQUIRES_RE.search(field_str)
        if m_req:
            requires = m_req.group(1)

    if len(parts) >= 3:
        detail = _clamp_words(parts[2], DETAIL_MAX_WORDS)

    return {"label": label, "roll": roll, "dc": dc, "requires": requires, "detail": detail}
