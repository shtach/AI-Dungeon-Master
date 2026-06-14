from ai_dungeon_master.apps.ai.parser import NARRATIVE_MAX_CHARS, parse_ai_response


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
