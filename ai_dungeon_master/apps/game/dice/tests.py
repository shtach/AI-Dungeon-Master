import json
import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.game.models import DiceRoll, GameSession, Message
from ai_dungeon_master.apps.world.models import Scenario, WorldSetting

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def roll_client(client, user):
    client.force_login(user)
    return client, user


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


def test_roll_modifier_per_stat(roll_client, game_session):
    client, user = roll_client
    response = client.post(
        f"/dice/session/{game_session.id}/roll/",
        data=json.dumps({"dice_type": "d20", "stat": "strength", "dc": 10}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["modifier"] == 3


def test_roll_boundaries(roll_client, game_session):
    client, user = roll_client
    for _ in range(50):
        response = client.post(
            f"/dice/session/{game_session.id}/roll/",
            data=json.dumps({"dice_type": "d20"}),
            content_type="application/json",
        )
        data = response.json()
        assert 1 <= data["roll"] <= 20
        assert data["dc"] is None
        assert data["success"] is None


def test_diceroll_persisted(roll_client, game_session):
    client, user = roll_client
    assert DiceRoll.objects.count() == 0
    client.post(
        f"/dice/session/{game_session.id}/roll/",
        data=json.dumps({"dice_type": "d6", "dc": 3}),
        content_type="application/json",
    )
    assert DiceRoll.objects.count() == 1
    roll = DiceRoll.objects.first()
    assert roll.dice_type == "d6"
    assert 1 <= roll.result <= 6
    assert roll.message is not None


def test_success_threshold(roll_client, game_session):
    client, user = roll_client
    response = client.post(
        f"/dice/session/{game_session.id}/roll/",
        data=json.dumps({"dice_type": "d20", "stat": "strength", "dc": 100}),
        content_type="application/json",
    )
    data = response.json()
    assert data["success"] is False

    response = client.post(
        f"/dice/session/{game_session.id}/roll/",
        data=json.dumps({"dice_type": "d20", "stat": "strength", "dc": 0}),
        content_type="application/json",
    )
    data = response.json()
    assert data["success"] is True


def test_unauthenticated(roll_client, game_session):
    client, user = roll_client
    from django.contrib.auth import logout
    logout(client)
    response = client.post(
        f"/dice/session/{game_session.id}/roll/",
        data=json.dumps({"dice_type": "d20"}),
        content_type="application/json",
    )
    assert response.status_code == 302


def test_invalid_dice_type(roll_client, game_session):
    client, user = roll_client
    response = client.post(
        f"/dice/session/{game_session.id}/roll/",
        data=json.dumps({"dice_type": "d99"}),
        content_type="application/json",
    )
    assert response.status_code == 400


def test_invalid_json(roll_client, game_session):
    client, user = roll_client
    response = client.post(
        f"/dice/session/{game_session.id}/roll/",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
