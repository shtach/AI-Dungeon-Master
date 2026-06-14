import logging

from ai_dungeon_master.apps.ai.parser import (
    DETAIL_MAX_WORDS,
    LABEL_MAX_WORDS,
    MAX_CARDS,
    NARRATIVE_MAX_CHARS,
    parse_ai_response,
)


class TestNarrative:
    def test_basic(self):
        text = "[NARRATIVE] You enter a dark cave."
        result = parse_ai_response(text)
        assert result["narrative"] == "You enter a dark cave."

    def test_missing_tag(self):
        result = parse_ai_response("No tags here.")
        assert result["narrative"] is None

    def test_empty_string(self):
        result = parse_ai_response("")
        assert result["narrative"] is None
        assert result["cards"] == []

    def test_none_input(self):
        result = parse_ai_response(None)
        assert result["narrative"] is None
        assert result["cards"] == []

    def test_long_narrative_clamped(self):
        long_text = " ".join(["word"] * 200)
        text = f"[NARRATIVE] {long_text}"
        result = parse_ai_response(text)
        assert len(result["narrative"]) <= NARRATIVE_MAX_CHARS + 10

    def test_narrative_clamped_at_sentence_boundary(self):
        text = "[NARRATIVE] " + "A" * 350 + ". Extra text after period that should be cut."
        result = parse_ai_response(text)
        assert result["narrative"].endswith(".")

    def test_multiple_narrative_tags(self):
        text = "[NARRATIVE] First narrative. [NARRATIVE] Second narrative."
        result = parse_ai_response(text)
        assert result["narrative"] == "First narrative."


class TestCards:
    def test_single_card(self):
        text = "[CARD] Attack the goblin | roll=strength dc=12 | A fierce strike"
        result = parse_ai_response(text)
        assert len(result["cards"]) == 1
        card = result["cards"][0]
        assert card["label"] == "Attack the goblin"
        assert card["roll"] == "strength"
        assert card["dc"] == 12
        assert card["requires"] is None
        assert card["detail"] == "A fierce strike"

    def test_card_with_requires(self):
        text = "[CARD] Use healing potion | requires=item | Restore health"
        result = parse_ai_response(text)
        card = result["cards"][0]
        assert card["requires"] == "item"
        assert card["roll"] is None
        assert card["dc"] is None

    def test_card_minimal(self):
        text = "[CARD] Look around"
        result = parse_ai_response(text)
        card = result["cards"][0]
        assert card["label"] == "Look around"
        assert card["roll"] is None
        assert card["dc"] is None
        assert card["requires"] is None
        assert card["detail"] is None

    def test_multiple_cards(self):
        text = (
            "[CARD] Attack | roll=strength dc=14\n"
            "[CARD] Sneak | roll=dexterity dc=16\n"
            "[CARD] Persuade | roll=charisma dc=10\n"
            "[CARD] Run away"
        )
        result = parse_ai_response(text)
        assert len(result["cards"]) == 4
        assert result["cards"][0]["dc"] == 14
        assert result["cards"][1]["roll"] == "dexterity"
        assert result["cards"][2]["dc"] == 10

    def test_long_label_trimmed(self):
        long_label = " ".join(["word"] * 20)
        text = f"[CARD] {long_label}"
        result = parse_ai_response(text)
        assert len(result["cards"][0]["label"].split()) <= LABEL_MAX_WORDS

    def test_long_detail_trimmed(self):
        long_detail = " ".join(["word"] * 30)
        text = f"[CARD] Attack | {long_detail}"
        result = parse_ai_response(text)
        detail = result["cards"][0]["detail"]
        if detail:
            assert len(detail.split()) <= DETAIL_MAX_WORDS

    def test_more_than_4_cards_trimmed(self):
        text = "\n".join(f"[CARD] Option {i}" for i in range(8))
        result = parse_ai_response(text)
        assert len(result["cards"]) == MAX_CARDS

    def test_invalid_stat_ignored(self):
        text = "[CARD] Attack | roll=invalid_stat dc=12"
        result = parse_ai_response(text)
        assert result["cards"][0]["roll"] is None
        assert result["cards"][0]["dc"] == 12

    def test_all_stat_keys(self):
        stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for stat in stats:
            text = f"[CARD] Test | roll={stat} dc=10"
            result = parse_ai_response(text)
            assert result["cards"][0]["roll"] == stat


class TestHpChange:
    def test_positive(self):
        text = "[HP_CHANGE] -5"
        result = parse_ai_response(text)
        assert result["hp_change"] == -5

    def test_negative(self):
        text = "[HP_CHANGE] +3"
        result = parse_ai_response(text)
        assert result["hp_change"] == 3

    def test_missing(self):
        result = parse_ai_response("[NARRATIVE] Nothing here.")
        assert result["hp_change"] is None

    def test_malformed(self):
        text = "[HP_CHANGE] not_a_number"
        result = parse_ai_response(text)
        assert result["hp_change"] is None


class TestCombatStart:
    def test_full(self):
        text = "[COMBAT_START] Goblin hp=20 ac=15 atk=4 dmg=6"
        result = parse_ai_response(text)
        combat = result["combat_start"]
        assert combat["name"] == "Goblin"
        assert combat["hp"] == 20
        assert combat["ac"] == 15
        assert combat["atk"] == 4
        assert combat["dmg"] == 6

    def test_partial(self):
        text = "[COMBAT_START] Dragon hp=100"
        result = parse_ai_response(text)
        combat = result["combat_start"]
        assert combat["name"] == "Dragon"
        assert combat["hp"] == 100
        assert combat["ac"] is None

    def test_empty(self):
        text = "[COMBAT_START]"
        result = parse_ai_response(text)
        assert result["combat_start"] is None

    def test_missing(self):
        result = parse_ai_response("[NARRATIVE] Peaceful day.")
        assert result["combat_start"] is None

    def test_multi_word_name(self):
        text = "[COMBAT_START] Ancient Dragon hp=150 ac=19 atk=7 dmg=12"
        result = parse_ai_response(text)
        assert result["combat_start"]["name"] == "Ancient Dragon"


class TestEnemyHp:
    def test_basic(self):
        text = "[ENEMY_HP] 15"
        result = parse_ai_response(text)
        assert result["enemy_hp"] == 15

    def test_malformed(self):
        text = "[ENEMY_HP] not_a_number"
        result = parse_ai_response(text)
        assert result["enemy_hp"] is None


class TestCombatEnd:
    def test_victory(self):
        text = "[COMBAT_END] victory The goblin falls."
        result = parse_ai_response(text)
        assert result["combat_end"]["victory"] is True

    def test_defeat(self):
        text = "[COMBAT_END] defeat You collapse."
        result = parse_ai_response(text)
        assert result["combat_end"]["victory"] is False

    def test_empty(self):
        text = "[COMBAT_END]"
        result = parse_ai_response(text)
        assert result["combat_end"] is None


class TestLoot:
    def test_full(self):
        text = "[LOOT] Magic Sword | weapon | dmg=1d8 hit=2 bonuses=fire | An ancient blade"
        result = parse_ai_response(text)
        loot = result["loot"]
        assert loot["name"] == "Magic Sword"
        assert loot["type"] == "weapon"
        assert loot["dmg"] == "1d8"
        assert loot["hit"] == 2
        assert loot["bonuses"] == "fire"
        assert loot["lore"] == "An ancient blade"

    def test_minimal(self):
        text = "[LOOT] Gold Coins"
        result = parse_ai_response(text)
        loot = result["loot"]
        assert loot["name"] == "Gold Coins"
        assert loot["type"] is None

    def test_empty(self):
        text = "[LOOT]"
        result = parse_ai_response(text)
        assert result["loot"] is None


class TestQuest:
    def test_offer(self):
        text = "[QUEST_OFFER] Save the Village"
        result = parse_ai_response(text)
        assert result["quest_offer"] == "Save the Village"

    def test_complete(self):
        text = "[QUEST_COMPLETE] Save the Village"
        result = parse_ai_response(text)
        assert result["quest_complete"] == "Save the Village"


class TestMalformed:
    def test_garbage_input(self):
        result = parse_ai_response("!!!###$$$%%%")
        assert result["narrative"] is None
        assert result["cards"] == []

    def test_partial_tags(self):
        text = "[NARRATIVE] Valid narrative. [INVALID_TAG] stuff. [CARD]"
        result = parse_ai_response(text)
        assert result["narrative"] == "Valid narrative."

    def test_no_exception_on_any_input(self):
        inputs = [
            None,
            "",
            "plain text",
            "[NARRATIVE]",
            "[CARD] |||",
            "[HP_CHANGE] abc",
            "[COMBAT_START] hp=xyz ac=abc",
            "[LOOT] ||| ||| |||",
            "[]",
            "[",
            "]",
            "[][]",
        ]
        for inp in inputs:
            try:
                parse_ai_response(inp)
            except Exception as e:
                assert False, f"parse_ai_response raised {type(e).__name__}: {e}"


class TestTruncationLogging:
    def test_long_narrative_logged(self, caplog):
        long_text = " ".join(["word"] * 200)
        text = f"[NARRATIVE] {long_text}"
        with caplog.at_level(logging.DEBUG, logger="ai_dungeon_master.apps.ai.parser"):
            parse_ai_response(text)
        assert any("Clamped narrative" in r.message for r in caplog.records)

    def test_long_label_logged(self, caplog):
        long_label = " ".join(["word"] * 20)
        text = f"[CARD] {long_label}"
        with caplog.at_level(logging.DEBUG, logger="ai_dungeon_master.apps.ai.parser"):
            parse_ai_response(text)
        assert any("Truncated text" in r.message for r in caplog.records)

    def test_excess_cards_logged(self, caplog):
        text = "\n".join(f"[CARD] Option {i}" for i in range(8))
        with caplog.at_level(logging.WARNING, logger="ai_dungeon_master.apps.ai.parser"):
            parse_ai_response(text)
        assert any("trimmed to" in r.message for r in caplog.records)


class TestFullResponse:
    def test_all_tags(self):
        text = (
            "[NARRATIVE] You see a dragon on the mountain.\n"
            "[CARD] Fight the dragon | roll=strength dc=20 | Risky but rewarding\n"
            "[CARD] Sneak past | roll=dexterity dc=15\n"
            "[CARD] Negotiate | roll=charisma dc=12\n"
            "[CARD] Retreat\n"
            "[HP_CHANGE] -3\n"
            "[QUEST_OFFER] Slay the Dragon\n"
            "[COMBAT_START] Ancient Dragon hp=150 ac=19 atk=7 dmg=12"
        )
        result = parse_ai_response(text)
        assert result["narrative"] == "You see a dragon on the mountain."
        assert len(result["cards"]) == 4
        assert result["hp_change"] == -3
        assert result["quest_offer"] == "Slay the Dragon"
        assert result["combat_start"]["name"] == "Ancient Dragon"
        assert result["combat_start"]["hp"] == 150

    def test_empty_response(self):
        result = parse_ai_response("")
        for key in ["narrative", "hp_change", "quest_offer", "quest_complete",
                     "combat_start", "enemy_hp", "combat_end", "loot"]:
            assert result[key] is None
        assert result["cards"] == []
