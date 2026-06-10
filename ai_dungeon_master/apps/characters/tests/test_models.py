import pytest
from ai_dungeon_master.apps.characters.models import Character

pytestmark = pytest.mark.django_db


class TestCharacterDerivedStats:
    def test_ability_modifier_boundaries(self):
        assert Character.ability_modifier(8) == -1
        assert Character.ability_modifier(10) == 0
        assert Character.ability_modifier(11) == 0
        assert Character.ability_modifier(14) == 2
        assert Character.ability_modifier(15) == 2
        assert Character.ability_modifier(20) == 5

    def test_max_hp_from_class_and_con(self, auth_client):
        _, user = auth_client
        character = Character.objects.create(
            user=user, name="Logen", character_class="WARRIOR", constitution=14, dexterity=10
        )
        assert character.max_hp == 18

    def test_armor_class_from_class_and_dex(self, auth_client):
        _, user = auth_client
        character = Character.objects.create(
            user=user, name="Garrett", character_class="ROGUE", constitution=10, dexterity=15
        )
        assert character.armor_class == 12

    def test_current_equals_max_on_create(self, auth_client):
        _, user = auth_client
        character = Character.objects.create(
            user=user, name="Gandalf", character_class="WIZARD", constitution=12, dexterity=10
        )
        assert character.max_hp == 11
        assert character.current_hp == character.max_hp
