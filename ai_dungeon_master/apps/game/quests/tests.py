import json
import pytest
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.game.models import GameSession
from ai_dungeon_master.apps.game.quests.models import Quest
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


def test_offer_creates(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response="[NARRATIVE]A quest![/NARRATIVE][QUEST_OFFER]title=Find Gem|description=Get it[/QUEST_OFFER]"),
    )

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/message/", data=json.dumps({"label": "Look"}), content_type="application/json")

    assert resp.status_code == 200
    assert Quest.objects.filter(session=game_session, status="OFFERED").count() == 1


def test_accept(client, user, game_session):
    quest = Quest.objects.create(session=game_session, title="Test", status="OFFERED")

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/quest/{quest.id}/accept/", content_type="application/json")

    assert resp.status_code == 200
    quest.refresh_from_db()
    assert quest.status == "ACTIVE"


def test_decline(client, user, game_session):
    quest = Quest.objects.create(session=game_session, title="Test", status="OFFERED")

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/quest/{quest.id}/decline/", content_type="application/json")

    assert resp.status_code == 200
    quest.refresh_from_db()
    assert quest.status == "FAILED"


def test_complete(client, user, game_session):
    quest = Quest.objects.create(session=game_session, title="Test", status="ACTIVE")

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/quest/{quest.id}/complete/", content_type="application/json")

    assert resp.status_code == 200
    quest.refresh_from_db()
    assert quest.status == "COMPLETED"


def test_cross_user_denied(client, user, game_session):
    other_user = User.objects.create_user(username="other", password="pass123")
    quest = Quest.objects.create(session=game_session, title="Test", status="OFFERED")

    client.force_login(other_user)
    resp = client.post(f"/session/{game_session.id}/quest/{quest.id}/accept/", content_type="application/json")

    assert resp.status_code == 404


def test_quests_in_prompt(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    Quest.objects.create(session=game_session, title="Defeat Dragon", description="Slay it", status="ACTIVE")
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response="[NARRATIVE]Dragon![/NARRATIVE]"),
    )

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/message/", data=json.dumps({"label": "Enter"}), content_type="application/json")

    assert resp.status_code == 200
