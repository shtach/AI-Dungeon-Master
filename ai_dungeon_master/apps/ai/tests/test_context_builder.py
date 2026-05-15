import pytest
from unittest.mock import MagicMock
from ai_dungeon_master.apps.ai.context_builder import build_prompt, CONTEXT_WINDOW_MESSAGES


@pytest.fixture
def mock_game_data():
    mock_char = MagicMock(
        name="Thorin", race="Dwarf", character_class="Warrior",
        level=1, current_hp=15, max_hp=15, armor_class=16,
        strength=15, dexterity=14, constitution=13,
        intelligence=10, wisdom=12, charisma=8
    )
    mock_world = MagicMock(name="Middle Earth", description="Fantasy", ai_instructions="Be gritty")
    mock_scenario = MagicMock(title="Lonely Mountain", intro_text="Intro")

    mock_session = MagicMock()
    mock_session.character = mock_char
    mock_session.world = mock_world
    mock_session.scenario = mock_scenario
    mock_session.summary = ""

    mock_messages_manager = MagicMock()
    mock_session.messages = mock_messages_manager

    return mock_session, mock_messages_manager


def test_prompt_contains_basic_info_and_no_empty_summary(mock_game_data):
    mock_session, mock_messages_manager = mock_game_data

    mock_messages_manager.order_by.return_value.__getitem__.return_value = []

    result = build_prompt(mock_session, "I look around.")

    assert "Thorin" in result
    assert "Middle Earth" in result
    assert "SESSION SUMMARY" not in result
    assert result.endswith("[Player]: I look around.\n[DM]:")


def test_prompt_includes_summary_when_present(mock_game_data):
    mock_session, mock_messages_manager = mock_game_data

    mock_session.summary = "Thorin previously killed a goblin."
    mock_messages_manager.order_by.return_value.__getitem__.return_value = []

    result = build_prompt(mock_session, "What next?")

    assert "=== SESSION SUMMARY ===" in result
    assert "Thorin previously killed a goblin." in result


def test_prompt_truncates_messages_to_context_window(mock_game_data):
    mock_session, mock_messages_manager = mock_game_data

    fake_messages = []
    for i in range(25):
        msg = MagicMock()
        msg.role = "user" if i % 2 == 0 else "assistant"
        msg.content = f"Test message {i}"
        fake_messages.append(msg)

    mock_sliced = fake_messages[-CONTEXT_WINDOW_MESSAGES:]
    mock_messages_manager.order_by.return_value.__getitem__.return_value = mock_sliced

    result = build_prompt(mock_session, "Final action")

    assert "Test message 24" in result
    assert "Test message 0" not in result