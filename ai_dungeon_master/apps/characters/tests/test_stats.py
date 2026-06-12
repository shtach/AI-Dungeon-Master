import pytest
from django.contrib.auth import get_user_model
from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.characters.stats import effective_stat, ability_mod, armor_class, to_hit

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def test_character():
    user = User.objects.create(username="stats_tester")
    return Character.objects.create(
        user=user, name="Artax", character_class="WARRIOR", strength=16, dexterity=14, intelligence=10
    )


class MockItem:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_gear_bonus_changes_ac(test_character):
    assert armor_class(test_character, equipped_items=[]) == 14

    shield = MockItem(ac_bonus=2)
    ring = MockItem(ac_bonus=1)

    assert armor_class(test_character, equipped_items=[shield, ring]) == 17


def test_amulet_raises_effective_int(test_character):
    assert effective_stat(test_character, "intelligence", equipped_items=[]) == 10
    assert ability_mod(test_character, "intelligence", equipped_items=[]) == 0

    amulet = MockItem(stat_bonus_type="intelligence", stat_bonus_value=4)
    items = [amulet]

    assert effective_stat(test_character, "intelligence", equipped_items=items) == 14
    assert ability_mod(test_character, "intelligence", equipped_items=items) == 2


def test_to_hit_picks_weapon_stat(test_character):
    sword = MockItem(attack_stat="strength", hit_bonus=1)
    assert to_hit(test_character, sword, equipped_items=[]) == 4

    dagger = MockItem(attack_stat="dexterity", hit_bonus=0)
    assert to_hit(test_character, dagger, equipped_items=[]) == 2
