import json
import pytest
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.game.models import GameSession
from ai_dungeon_master.apps.game.combat.models import Enemy
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


def test_turn_increment(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response="[NARRATIVE]Hello[/NARRATIVE]"),
    )
    client.force_login(user)

    assert game_session.turn_count == 0
    client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Act"}),
        content_type="application/json",
    )
    game_session.refresh_from_db()
    assert game_session.turn_count == 1

    client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Act again"}),
        content_type="application/json",
    )
    game_session.refresh_from_db()
    assert game_session.turn_count == 2


def test_kill_counter(client, user, game_session):
    weapon = InventoryItem.objects.create(
        character=game_session.character, name="Sword", item_type="Weapon",
        slot="WEAPON", damage="1d8", attack_stat="strength",
    )
    enemy = Enemy.objects.create(
        session=game_session, name="Goblin", max_hp=1, current_hp=1,
        armor_class=1, attack_bonus=0,
    )
    client.force_login(user)

    assert game_session.kills == 0
    resp = client.post(
        f"/combat/session/{game_session.id}/attack/",
        data=json.dumps({"enemy_id": enemy.id, "weapon_id": weapon.id}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    game_session.refresh_from_db()
    assert game_session.kills == 1


def test_dice_counters(client, user, game_session):
    client.force_login(user)

    assert game_session.dice_rolled == 0
    assert game_session.nat20s == 0
    assert game_session.nat1s == 0
    assert game_session.highest_roll == 0

    client.post(
        f"/dice/session/{game_session.id}/roll/",
        data=json.dumps({"dice_type": "d20"}),
        content_type="application/json",
    )
    game_session.refresh_from_db()
    assert game_session.dice_rolled == 1


def test_damage_counters(client, user, game_session, monkeypatch):
    from ai_dungeon_master.apps.ai.providers.mock import MockProvider

    game_session.character.current_hp = 10
    game_session.character.save(update_fields=["current_hp"])
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response="[NARRATIVE]Hit![/NARRATIVE][HP_CHANGE]-4[/HP_CHANGE]"),
    )
    client.force_login(user)

    client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Fight"}),
        content_type="application/json",
    )
    game_session.refresh_from_db()
    assert game_session.damage_taken == 4
    assert game_session.damage_dealt == 0

    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.turn_views.get_ai_client",
        lambda: MockProvider(response="[NARRATIVE]Strike![/NARRATIVE][HP_CHANGE]+3[/HP_CHANGE]"),
    )
    client.post(
        f"/session/{game_session.id}/message/",
        data=json.dumps({"label": "Attack"}),
        content_type="application/json",
    )
    game_session.refresh_from_db()
    assert game_session.damage_dealt == 3
    assert game_session.damage_taken == 4
