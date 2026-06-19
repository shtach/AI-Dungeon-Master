import pytest
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.game.models import GameSession
from ai_dungeon_master.apps.game.combat.engine import enemy_turn
from ai_dungeon_master.apps.game.combat.models import Enemy
from ai_dungeon_master.apps.legacy.models import PlayerProfile, Relic, SessionSummary
from ai_dungeon_master.apps.legacy.services import end_session, SURVIVAL_BONUS
from ai_dungeon_master.apps.world.models import Scenario, WorldSetting

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def setup(user):
    world = WorldSetting.objects.create(name="Dark Realm", description="A grim world", ai_instructions="Be dark")
    scenario = Scenario.objects.create(world=world, title="The Descent", intro_text="You descend...")
    character = Character.objects.create(
        user=user, name="Hero", character_class="WARRIOR",
        strength=16, dexterity=12, constitution=14,
        intelligence=10, wisdom=10, charisma=8,
        max_hp=20, current_hp=20, armor_class=14,
    )
    session = GameSession.objects.create(
        user=user, character=character, world=world, scenario=scenario,
        kills=3, quests_completed=1, gold_gathered=50, turn_count=5,
        nat20s=2, damage_dealt=40, damage_taken=15,
    )
    InventoryItem.objects.create(
        character=character, name="Dragon Sword", slot="WEAPON",
        damage_die="2d6", attack_stat="strength", hit_bonus=2,
        stat_bonuses={"fire_damage": 1},
    )
    InventoryItem.objects.create(
        character=character, name="Iron Shield", slot="ARMOR",
        ac_bonus=2,
    )
    return user, character, session


class TestDeathCreatesSummary:
    def test_death_produces_summary(self, setup):
        _, _, session = setup
        summary = end_session(session, SessionSummary.VerdictChoices.DIED)
        assert summary.verdict == "DIED"
        assert summary.session == session
        session.refresh_from_db()
        assert session.status == GameSession.StatusChoices.DEAD

    def test_death_summary_has_deeds(self, setup):
        _, _, session = setup
        summary = end_session(session, SessionSummary.VerdictChoices.DIED)
        assert any("3" in d for d in summary.deeds)
        assert any("1" in d for d in summary.deeds)

    def test_death_summary_has_stat_snapshot(self, setup):
        _, _, session = setup
        summary = end_session(session, SessionSummary.VerdictChoices.DIED)
        assert summary.stat_snapshot["name"] == "Hero"
        assert summary.stat_snapshot["level"] == 1


class TestPointsFormula:
    def test_death_points_no_survival(self, setup):
        _, _, session = setup
        summary = end_session(session, SessionSummary.VerdictChoices.DIED)
        expected = 5 * 1 + 3 * 5 + 1 * 8 + 50 // 10
        assert summary.points_awarded == expected

    def test_completion_includes_survival_bonus(self, setup):
        _, _, session = setup
        summary = end_session(session, SessionSummary.VerdictChoices.WON)
        expected = 5 * 1 + 3 * 5 + 1 * 8 + 50 // 10 + SURVIVAL_BONUS
        assert summary.points_awarded == expected

    def test_points_added_to_profile(self, setup):
        _, _, session = setup
        profile = PlayerProfile.objects.get(user=session.user)
        points_before = profile.legacy_points
        summary = end_session(session, SessionSummary.VerdictChoices.DIED)
        profile.refresh_from_db()
        assert profile.legacy_points == points_before + summary.points_awarded

    def test_zero_session_awards_zero(self, user):
        world = WorldSetting.objects.create(name="W", description="D", ai_instructions="I")
        scenario = Scenario.objects.create(world=world, title="T", intro_text="I")
        character = Character.objects.create(user=user, name="N", character_class="WIZARD")
        session = GameSession.objects.create(
            user=user, character=character, world=world, scenario=scenario,
        )
        summary = end_session(session, SessionSummary.VerdictChoices.DIED)
        assert summary.points_awarded == 0


class TestRelicsToVault:
    def test_relics_created_from_inventory(self, setup):
        _, _, session = setup
        end_session(session, SessionSummary.VerdictChoices.DIED)
        profile = PlayerProfile.objects.get(user=session.user)
        relics = Relic.objects.filter(profile=profile, source_run=session)
        assert relics.count() == 2
        names = set(relics.values_list("name", flat=True))
        assert "Dragon Sword" in names
        assert "Iron Shield" in names

    def test_relic_preserves_item_fields(self, setup):
        _, _, session = setup
        end_session(session, SessionSummary.VerdictChoices.DIED)
        sword = Relic.objects.get(name="Dragon Sword", source_run=session)
        assert sword.damage_die == "2d6"
        assert sword.attack_stat == "strength"
        assert sword.hit_bonus == 2
        assert sword.stat_bonuses == {"fire_damage": 1}


class TestDeadSessionRejectsTurns:
    def test_dead_session_blocks_card_click(self, setup):
        _, _, session = setup
        end_session(session, SessionSummary.VerdictChoices.DIED)
        session.refresh_from_db()
        assert session.status != GameSession.StatusChoices.ACTIVE

    def test_end_session_idempotent(self, setup):
        _, _, session = setup
        s1 = end_session(session, SessionSummary.VerdictChoices.DIED)
        s2 = end_session(session, SessionSummary.VerdictChoices.DIED)
        assert s1.id == s2.id

    def test_combat_engine_death_calls_end_session(self, user):
        world = WorldSetting.objects.create(name="W", description="D", ai_instructions="I")
        scenario = Scenario.objects.create(world=world, title="T", intro_text="I")
        character = Character.objects.create(
            user=user, name="Weak", character_class="ROGUE",
            current_hp=1, max_hp=10,
        )
        session = GameSession.objects.create(
            user=user, character=character, world=world, scenario=scenario,
        )
        enemy = Enemy.objects.create(
            session=session, name="Goblin", max_hp=10, current_hp=10,
            armor_class=10, attack_bonus=5, damage_die="1d20",
        )
        monkeypatch_obj = pytest.MonkeyPatch()
        monkeypatch_obj.setattr(
            "ai_dungeon_master.apps.game.combat.engine.random.randint",
            lambda a, b: 20,
        )
        try:
            enemy_turn(enemy, character)
            character.refresh_from_db()
            assert character.current_hp == 0
            assert SessionSummary.objects.filter(session=session).exists()
        finally:
            monkeypatch_obj.undo()
