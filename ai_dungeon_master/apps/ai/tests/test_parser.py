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
