import json
import pytest
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.game.models import GameSession
from ai_dungeon_master.apps.world.models import Scenario, WorldSetting

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def game_session(user):
    world = WorldSetting.objects.create(
        name="Test World", description="A test world.", ai_instructions="Be a DM."
    )
    scenario = Scenario.objects.create(
        world=world, title="Test Scenario", intro_text="Welcome!"
    )
    character = Character.objects.create(
        user=user, name="Thorin", character_class="WARRIOR",
        strength=16, dexterity=12, constitution=14,
        intelligence=10, wisdom=10, charisma=8,
    )
    session = GameSession.objects.create(
        user=user, character=character, world=world, scenario=scenario,
    )
    return session


def test_no_roll_path(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    ai_response = (
        "[NARRATIVE]You enter a dark cave.[/NARRATIVE]"
        "[CARD]Explore deeper[/CARD]"
        "[CARD]Go back|roll=strength|dc=12[/CARD]"
    )
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response=ai_response),
    )

    client.force_login(user)
    response = client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Enter cave"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["narrative"] == "You enter a dark cave."
    assert len(data["cards"]) == 2
    assert data["cards"][0]["label"] == "Explore deeper"
    assert data["cards"][1]["roll"] == "strength"
    assert "dice" not in data

    game_session.refresh_from_db()
    assert game_session.turn_count == 1


def test_roll_branch_success(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    ai_response = (
        "[NARRATIVE]You find a treasure chest![/NARRATIVE]"
        "[CARD]Open it[/CARD]"
    )
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response=ai_response),
    )

    client.force_login(user)
    response = client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({
            "label": "Search for traps",
            "roll": "dexterity",
            "dc": 10,
        }),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.json()
    assert "dice" in data
    assert data["dice"]["roll"] == "dexterity"
    assert data["dice"]["dc"] == 10
    assert data["narrative"] == "You find a treasure chest!"

    response2 = client.post(
        f"/session/{game_session.id}/resolve/",
        data=json.dumps({
            "roll_result": 15,
            "roll_total": 17,
            "roll_success": True,
            "label": "Search for traps",
        }),
        content_type="application/json",
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["narrative"] == "You find a treasure chest!"

    game_session.refresh_from_db()
    assert game_session.turn_count == 1


def test_roll_branch_failure(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    ai_response = (
        "[NARRATIVE]You trip and fall![/NARRATIVE]"
        "[HP_CHANGE]-2[/HP_CHANGE]"
    )
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response=ai_response),
    )

    client.force_login(user)
    response = client.post(
        f"/session/{game_session.id}/resolve/",
        data=json.dumps({
            "roll_result": 3,
            "roll_total": 5,
            "roll_success": False,
            "label": "Jump across",
        }),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["narrative"] == "You trip and fall!"
    assert data["hp_change"] == -2

    game_session.refresh_from_db()
    assert game_session.turn_count == 1


def test_requires_filtering(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    InventoryItem.objects.create(
        character=game_session.character,
        name="Rope",
        item_type="Tool",
        slot="MISC",
    )

    ai_response = (
        "[NARRATIVE]You see a chasm.[/NARRATIVE]"
        "[CARD]Climb down|requires=Rope[/CARD]"
        "[CARD]Go back[/CARD]"
    )
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response=ai_response),
    )

    client.force_login(user)
    response = client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Approach chasm"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["cards"]) == 2

    InventoryItem.objects.filter(character=game_session.character, name="Rope").delete()

    response2 = client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Approach chasm again"}),
        content_type="application/json",
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["cards"]) == 1
    assert data2["cards"][0]["label"] == "Go back"


def test_ai_error_graceful(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.exceptions import AIProviderError

    def raise_error(prompt):
        raise AIProviderError("Service unavailable")

    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: type("FailClient", (), {"generate": staticmethod(raise_error)})(),
    )

    client.force_login(user)
    response = client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Attack"}),
        content_type="application/json",
    )

    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert "temporarily unavailable" in data["error"]

    response2 = client.post(
        f"/session/{game_session.id}/resolve/",
        data=json.dumps({
            "roll_result": 10,
            "roll_total": 12,
            "roll_success": True,
            "label": "Attack",
        }),
        content_type="application/json",
    )

    assert response2.status_code == 503
    data2 = response2.json()
    assert "error" in data2
