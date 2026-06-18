import pytest
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.characters.models import Character
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


def test_take_creates_item(client, user, game_session):
    from ai_dungeon_master.apps.characters.models import InventoryItem

    game_session.pending_loot = {"name": "Magic Sword", "slot": "WEAPON", "damage_die": "d8", "hit_bonus": 2}
    game_session.save(update_fields=["pending_loot"])

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/loot/take/", content_type="application/json")
    data = resp.json()

    assert resp.status_code == 200
    assert data["taken"] is True
    assert data["name"] == "Magic Sword"

    item = InventoryItem.objects.get(id=data["item_id"])
    assert item.name == "Magic Sword"
    assert item.slot == "WEAPON"
    assert item.hit_bonus == 2

    game_session.refresh_from_db()
    assert game_session.pending_loot is None


def test_leave_discards(client, user, game_session):
    game_session.pending_loot = {"name": "Junk", "slot": "MISC"}
    game_session.save(update_fields=["pending_loot"])

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/loot/leave/", content_type="application/json")

    assert resp.status_code == 200
    assert resp.json()["discarded"] is True

    game_session.refresh_from_db()
    assert game_session.pending_loot is None


def test_bonus_clamped(client, user, game_session):
    from ai_dungeon_master.apps.characters.models import InventoryItem

    game_session.pending_loot = {"name": "Op Sword", "slot": "WEAPON", "hit_bonus": 99, "ac_bonus": -99}
    game_session.save(update_fields=["pending_loot"])

    client.force_login(user)
    resp = client.post(f"/session/{game_session.id}/loot/take/", content_type="application/json")
    data = resp.json()

    assert resp.status_code == 200
    item = InventoryItem.objects.get(id=data["item_id"])
    assert item.hit_bonus == 10
    assert item.ac_bonus == -5
