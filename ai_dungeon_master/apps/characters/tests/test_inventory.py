import pytest
from django.urls import reverse
from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.characters.stats import armor_class

pytestmark = pytest.mark.django_db


def test_new_character_has_starting_weapon(auth_client):
    client, user = auth_client

    session = client.session
    session["character_wizard"] = {
        "name": "Aragorn",
        "race": "HUMAN",
        "character_class": "WARRIOR",
        "stats": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 12,
        },
    }
    session.save()

    url = reverse("characters:create_step4")
    client.post(url, {"background": "Ranger of the North"})

    char = Character.objects.get(name="Aragorn")

    equipped_items = char.inventory.filter(equipped=True)
    assert equipped_items.count() == 2

    weapon = equipped_items.get(slot="WEAPON")
    assert weapon.name == "Longsword"
    assert weapon.damage_die == "1d8"
    assert weapon.attack_stat == "strength"

    armor = equipped_items.get(slot="ARMOR")
    assert armor.name == "Chainmail"
    assert armor.ac_bonus == 2


def test_equip_changes_numbers():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create(username="testuser")

    char = Character.objects.create(
        user=user,
        name="Tester",
        character_class="ROGUE",
        dexterity=16,  # mod: +3
    )

    assert armor_class(char) == 13

    armor = InventoryItem.objects.create(character=char, name="Magic Leather", slot="ARMOR", equipped=True, ac_bonus=2)

    assert armor_class(char) == 15
    armor.equipped = False
    armor.save()
    assert armor_class(char) == 13
