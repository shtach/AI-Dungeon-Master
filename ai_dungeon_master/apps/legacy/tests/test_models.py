import pytest
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.legacy.models import (
    LegacyPerk,
    OwnedPerk,
    PlayerProfile,
    Relic,
    SessionSummary,
)
from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.game.models import GameSession

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestProfileAutoCreated:
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username="newhero", password="pass1234")
        assert PlayerProfile.objects.filter(user=user).exists()
        profile = PlayerProfile.objects.get(user=user)
        assert profile.legacy_points == 0

    def test_profile_not_duplicated(self):
        user = User.objects.create_user(username="dupcheck", password="pass1234")
        count_before = PlayerProfile.objects.filter(user=user).count()
        user.save()
        count_after = PlayerProfile.objects.filter(user=user).count()
        assert count_before == count_after == 1


class TestRelicSnapshot:
    def test_relic_snapshot_fields(self, auth_client):
        _, user = auth_client
        profile = PlayerProfile.objects.get(user=user)
        character = Character.objects.create(user=user, name="Rogue1", character_class="ROGUE")
        item = InventoryItem.objects.create(
            character=character,
            name="Shadow Blade",
            item_type="weapon",
            slot="WEAPON",
            damage_die="1d8",
            attack_stat="dexterity",
            hit_bonus=2,
            ac_bonus=0,
            stat_bonuses={"stealth": 1},
        )
        session = GameSession.objects.create(
            user=user,
            character=character,
            world=None,
            scenario=None,
            status="DEAD",
        )
        relic = Relic.objects.create(
            profile=profile,
            name=item.name,
            slot=item.slot,
            damage_die=item.damage_die,
            attack_stat=item.attack_stat,
            hit_bonus=item.hit_bonus,
            ac_bonus=item.ac_bonus,
            stat_bonuses=item.stat_bonuses,
            lore="Forged in the shadow realm",
            source_run=session,
        )
        assert relic.name == "Shadow Blade"
        assert relic.slot == "WEAPON"
        assert relic.damage_die == "1d8"
        assert relic.stat_bonuses == {"stealth": 1}
        assert relic.source_run == session


class TestPerkCatalogue:
    def test_perk_creation(self):
        perk = LegacyPerk.objects.create(
            key="iron_skin",
            name="Iron Skin",
            description="Gain +1 AC permanently",
            cost=10,
            effect={"stat": "ac_bonus", "bonus": 1},
        )
        assert perk.key == "iron_skin"
        assert perk.effect == {"stat": "ac_bonus", "bonus": 1}

    def test_perk_unique_key(self):
        LegacyPerk.objects.create(
            key="sharp_eye", name="Sharp Eye", description="...", cost=5, effect={}
        )
        with pytest.raises(Exception):
            LegacyPerk.objects.create(
                key="sharp_eye", name="Duplicate", description="...", cost=5, effect={}
            )

    def test_owned_perk(self, auth_client):
        _, user = auth_client
        profile = PlayerProfile.objects.get(user=user)
        perk = LegacyPerk.objects.create(
            key="lucky_strike",
            name="Lucky Strike",
            description="+1 hit bonus",
            cost=15,
            effect={"stat": "hit_bonus", "bonus": 1},
        )
        owned = OwnedPerk.objects.create(profile=profile, perk=perk)
        assert owned.profile == profile
        assert owned.perk == perk

    def test_owned_perk_unique_together(self, auth_client):
        _, user = auth_client
        profile = PlayerProfile.objects.get(user=user)
        perk = LegacyPerk.objects.create(
            key="thick_hide",
            name="Thick Hide",
            description="...",
            cost=10,
            effect={},
        )
        OwnedPerk.objects.create(profile=profile, perk=perk)
        with pytest.raises(Exception):
            OwnedPerk.objects.create(profile=profile, perk=perk)

    def test_perk_ordered_by_cost(self):
        LegacyPerk.objects.create(key="b", name="B", description="...", cost=20, effect={})
        LegacyPerk.objects.create(key="a", name="A", description="...", cost=5, effect={})
        perks = list(LegacyPerk.objects.values_list("key", flat=True))
        assert perks == ["a", "b"]


class TestSessionSummary:
    def test_summary_creation(self, auth_client):
        _, user = auth_client
        profile = PlayerProfile.objects.get(user=user)
        character = Character.objects.create(user=user, name="Hero", character_class="WARRIOR")
        session = GameSession.objects.create(
            user=user, character=character, world=None, scenario=None, status="DEAD"
        )
        summary = SessionSummary.objects.create(
            session=session,
            profile=profile,
            verdict="DIED",
            stat_snapshot={"hp": 0, "level": 3},
            deeds=["Slew 5 goblins", "Found the Golden Chalice"],
            points_awarded=25,
        )
        assert summary.verdict == "DIED"
        assert summary.points_awarded == 25
        assert len(summary.deeds) == 2

    def test_summary_one_to_one_with_session(self, auth_client):
        _, user = auth_client
        profile = PlayerProfile.objects.get(user=user)
        character = Character.objects.create(user=user, name="Hero2", character_class="WIZARD")
        session = GameSession.objects.create(
            user=user, character=character, world=None, scenario=None, status="WON"
        )
        SessionSummary.objects.create(
            session=session, profile=profile, verdict="WON", points_awarded=50
        )
        with pytest.raises(Exception):
            SessionSummary.objects.create(
                session=session, profile=profile, verdict="DIED", points_awarded=10
            )
