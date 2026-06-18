import json
import pytest
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.game.combat.engine import (
    attack, enemy_turn, flee, outwit, persuade, roll_dice,
)
from ai_dungeon_master.apps.game.combat.models import Enemy
from ai_dungeon_master.apps.game.models import GameSession
from ai_dungeon_master.apps.world.models import Scenario, WorldSetting

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def game_session(user):
    world = WorldSetting.objects.create(name="Test World", description="A test world.")
    scenario = Scenario.objects.create(world=world, title="Test", intro_text="Welcome!")
    character = Character.objects.create(
        user=user, name="Thorin", character_class="WARRIOR",
        strength=16, dexterity=12, constitution=14,
        intelligence=10, wisdom=10, charisma=8,
        max_hp=20, current_hp=20, armor_class=14,
    )
    return GameSession.objects.create(
        user=user, character=character, world=world, scenario=scenario,
    )


@pytest.fixture
def enemy(game_session):
    return Enemy.objects.create(
        session=game_session, name="Goblin",
        max_hp=8, current_hp=8, armor_class=12,
        attack_bonus=2, damage_die="1d6",
    )


@pytest.fixture
def weapon(game_session):
    return InventoryItem.objects.create(
        character=game_session.character, name="Sword",
        item_type="Weapon", slot="WEAPON", equipped=True,
        damage_die="1d8", attack_stat="strength", hit_bonus=1,
    )


def test_attack_hit_miss(game_session, enemy, weapon, monkeypatch):
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.combat.engine.random.randint",
        lambda a, b: 18,
    )
    result = attack(game_session.character, weapon, enemy)
    assert result["hit"] is True
    assert result["damage"] > 0

    enemy.refresh_from_db()
    assert enemy.current_hp < 8


def test_damage_math(game_session, enemy, weapon, monkeypatch):
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.combat.engine.random.randint",
        lambda a, b: 18,
    )
    result = attack(game_session.character, weapon, enemy)
    assert result["hit"] is True
    assert result["damage"] >= 1


def test_enemy_turn(game_session, enemy, monkeypatch):
    initial_hp = game_session.character.current_hp
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.combat.engine.random.randint",
        lambda a, b: 20,
    )
    result = enemy_turn(enemy, game_session.character)
    assert result["hit"] is True
    assert result["damage"] > 0

    game_session.character.refresh_from_db()
    assert game_session.character.current_hp < initial_hp


def test_enemy_death_ends(game_session, enemy, weapon, monkeypatch):
    enemy.current_hp = 1
    enemy.save()

    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.combat.engine.random.randint",
        lambda a, b: 18,
    )
    result = attack(game_session.character, weapon, enemy)
    assert result["hit"] is True
    assert result["damage"] >= 1

    enemy.refresh_from_db()
    assert enemy.current_hp == 0
    assert enemy.status == Enemy.StatusChoices.DEAD


def test_flee(game_session, monkeypatch):
    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.combat.engine.random.randint",
        lambda a, b: 20,
    )
    result = flee(game_session.character)
    assert result["success"] is True


def test_player_death(game_session, enemy, monkeypatch):
    game_session.character.current_hp = 1
    game_session.character.save()

    monkeypatch.setattr(
        "ai_dungeon_master.apps.game.combat.engine.random.randint",
        lambda a, b: 20,
    )
    result = enemy_turn(enemy, game_session.character)
    assert result["hit"] is True

    game_session.character.refresh_from_db()
    assert game_session.character.current_hp == 0

    game_session.refresh_from_db()
    assert game_session.status == GameSession.StatusChoices.DEAD
