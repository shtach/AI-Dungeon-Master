import re

NARRATIVE_MAX_CHARS = 400
LABEL_MAX_WORDS = 6
DETAIL_MAX_WORDS = 12
MAX_CARDS = 4

_TAG_RE = re.compile(r"\[(\w+)\]([^\[]*)")

_STAT_KEYS = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
