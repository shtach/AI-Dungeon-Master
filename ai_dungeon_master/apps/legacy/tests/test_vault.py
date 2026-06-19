import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.legacy.models import LegacyPerk, OwnedPerk, PlayerProfile, Relic

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def setup():
    user = User.objects.create_user(username="hero", password="pass1234")
    profile, _ = PlayerProfile.objects.get_or_create(user=user)
    profile.legacy_points = 100
    profile.save(update_fields=["legacy_points"])
    return user, profile


class TestBuyPerk:
    def test_buy_perk_deducts(self, setup):
        user, profile = setup
        perk = LegacyPerk.objects.create(
            key="hardy_soul", name="Hardy Soul", cost=30,
            description="+2 max HP", effect={"max_hp": 2},
        )
        client = Client()
        client.login(username="hero", password="pass1234")
        resp = client.post(f"/legacy/perk/{perk.key}/buy/")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert resp.json()["points_remaining"] == 70
        profile.refresh_from_db()
        assert profile.legacy_points == 70
        assert OwnedPerk.objects.filter(profile=profile, perk=perk).exists()

    def test_cannot_overspend(self, setup):
        user, profile = setup
        perk = LegacyPerk.objects.create(
            key="legendary", name="Legendary", cost=200,
            description="Too expensive", effect={},
        )
        profile.legacy_points = 10
        profile.save(update_fields=["legacy_points"])
        client = Client()
        client.login(username="hero", password="pass1234")
        resp = client.post(f"/legacy/perk/{perk.key}/buy/")
        assert resp.status_code == 400
        assert not OwnedPerk.objects.filter(profile=profile, perk=perk).exists()


class TestPerkAffectsStats:
    def test_perk_affects_stats(self, setup):
        user, profile = setup
        perk = LegacyPerk.objects.create(
            key="sharp_eye", name="Sharp Eye", cost=40,
            description="+1 to-hit", effect={"hit_bonus": 1},
        )
        OwnedPerk.objects.create(profile=profile, perk=perk)
        character = Character.objects.create(
            user=user, name="Test", character_class="ROGUE",
            strength=12, dexterity=16, constitution=10,
            intelligence=10, wisdom=10, charisma=10,
        )
        weapon = InventoryItem.objects.create(
            character=character, name="Dagger", slot="WEAPON",
            equipped=True, hit_bonus=0, attack_stat="dexterity",
        )
        from ai_dungeon_master.apps.characters.stats import to_hit
        result = to_hit(character, weapon)
        assert result >= 3


class TestRelicEquippedOnStart:
    def test_relic_equipped_on_start(self, setup):
        user, profile = setup
        relic = Relic.objects.create(
            profile=profile, name="Ancient Blade", slot="WEAPON",
            damage_die="2d6", attack_stat="strength", hit_bonus=2,
        )
        character = Character.objects.create(
            user=user, name="Test", character_class="WARRIOR",
        )
        InventoryItem.objects.create(
            character=character, name="Longsword", item_type="Weapon",
            slot="WEAPON", equipped=True, damage_die="1d8", attack_stat="strength",
        )
        InventoryItem.objects.create(
            character=character, name=relic.name, item_type="Relic",
            slot=relic.slot, equipped=True,
            damage_die=relic.damage_die, attack_stat=relic.attack_stat,
            hit_bonus=relic.hit_bonus, ac_bonus=relic.ac_bonus,
            stat_bonuses=relic.stat_bonuses,
        )
        items = InventoryItem.objects.filter(character=character, slot="WEAPON", equipped=True)
        assert items.filter(name="Ancient Blade").exists()
