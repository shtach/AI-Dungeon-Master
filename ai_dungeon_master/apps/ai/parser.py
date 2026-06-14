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


_HP_RE = re.compile(r"hp=(-?\d+)")
_AC_RE = re.compile(r"ac=(\d+)")
_ATK_RE = re.compile(r"atk=(-?\d+)")
_DMG_RE = re.compile(r"dmg=(-?\d+)")


def _parse_hp_change(raw: str) -> int | None:
    m = _HP_RE.search(raw)
    if m:
        return int(m.group(1))
    raw = raw.strip()
    try:
        return int(raw)
    except ValueError:
        return None


def _parse_combat_start(raw: str) -> dict[str, Any] | None:
    if not raw.strip():
        return None

    hp_match = _HP_RE.search(raw)
    if hp_match:
        name = raw[: hp_match.start()].strip()
    else:
        name = raw.strip().split()[0] if raw.strip() else None
    result: dict[str, Any] = {"name": name}

    m = _HP_RE.search(raw)
    result["hp"] = int(m.group(1)) if m else None

    m = _AC_RE.search(raw)
    result["ac"] = int(m.group(1)) if m else None

    m = _ATK_RE.search(raw)
    result["atk"] = int(m.group(1)) if m else None

    m = _DMG_RE.search(raw)
    result["dmg"] = int(m.group(1)) if m else None

    return result


def _parse_enemy_hp(raw: str) -> int | None:
    raw = raw.strip()
    try:
        return int(raw.split()[0])
    except (ValueError, IndexError):
        return None


def _parse_combat_end(raw: str) -> dict[str, Any] | None:
    raw = raw.strip()
    if not raw:
        return None
    victory = raw.lower().startswith("victory") or "victory" in raw.lower()
    return {"victory": victory, "detail": _clamp_words(raw, DETAIL_MAX_WORDS)}


def _parse_loot(raw: str) -> dict[str, Any] | None:
    if not raw.strip():
        return None

    parts = [p.strip() for p in raw.split("|")]
    result: dict[str, Any] = {
        "name": parts[0] if parts else None,
        "type": parts[1] if len(parts) >= 2 else None,
    }

    if len(parts) >= 3:
        stats_str = parts[2]
        result["dmg"] = None
        result["hit"] = None
        result["bonuses"] = None

        m_dmg = re.search(r"dmg=(\S+)", stats_str)
        if m_dmg:
            result["dmg"] = m_dmg.group(1)

        m_hit = re.search(r"hit=(-?\d+)", stats_str)
        if m_hit:
            result["hit"] = int(m_hit.group(1))

        m_bon = re.search(r"bonuses=(\S+)", stats_str)
        if m_bon:
            result["bonuses"] = m_bon.group(1)

    if len(parts) >= 4:
        result["lore"] = _clamp_words(parts[3], DETAIL_MAX_WORDS)
    else:
        result["lore"] = None

    return result


def parse_ai_response(text: str) -> dict[str, Any]:
    if not text:
        return {
            "narrative": None,
            "cards": [],
            "hp_change": None,
            "quest_offer": None,
            "quest_complete": None,
            "combat_start": None,
            "enemy_hp": None,
            "combat_end": None,
            "loot": None,
        }

    tags: dict[str, list[str]] = {}
    for match in _TAG_RE.finditer(text):
        tag_name = match.group(1).upper()
        tag_content = match.group(2).strip()
        tags.setdefault(tag_name, []).append(tag_content)

    narrative_raw = tags.get("NARRATIVE", [None])[0]
    narrative = _clamp_narrative(narrative_raw)

    cards_raw = tags.get("CARD", [])
    cards = [_parse_card(c) for c in cards_raw[:MAX_CARDS]]

    if len(cards_raw) > MAX_CARDS:
        logger.warning(
            "AI returned %d cards, trimmed to %d", len(cards_raw), MAX_CARDS
        )

    hp_raw = tags.get("HP_CHANGE", [None])[0]
    hp_change = _parse_hp_change(hp_raw) if hp_raw else None

    quest_offer_raw = tags.get("QUEST_OFFER", [None])[0]
    quest_offer = quest_offer_raw.strip() if quest_offer_raw else None

    quest_complete_raw = tags.get("QUEST_COMPLETE", [None])[0]
    quest_complete = quest_complete_raw.strip() if quest_complete_raw else None

    combat_start_raw = tags.get("COMBAT_START", [None])[0]
    combat_start = _parse_combat_start(combat_start_raw) if combat_start_raw else None

    enemy_hp_raw = tags.get("ENEMY_HP", [None])[0]
    enemy_hp = _parse_enemy_hp(enemy_hp_raw) if enemy_hp_raw else None

    combat_end_raw = tags.get("COMBAT_END", [None])[0]
    combat_end = _parse_combat_end(combat_end_raw) if combat_end_raw else None

    loot_raw = tags.get("LOOT", [None])[0]
    loot = _parse_loot(loot_raw) if loot_raw else None

    return {
        "narrative": narrative,
        "cards": cards,
        "hp_change": hp_change,
        "quest_offer": quest_offer,
        "quest_complete": quest_complete,
        "combat_start": combat_start,
        "enemy_hp": enemy_hp,
        "combat_end": combat_end,
        "loot": loot,
    }
