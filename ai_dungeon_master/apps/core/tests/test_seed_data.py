import pytest
from django.core.management import call_command

from ai_dungeon_master.apps.world.models import Scenario, WorldSetting

pytestmark = pytest.mark.django_db

EXPECTED_WORLDS = 4
EXPECTED_SCENARIOS = 12


class TestSeedData:
    def test_seed_data_loads(self):
        call_command("seed_data")

        assert WorldSetting.objects.count() == EXPECTED_WORLDS
        assert Scenario.objects.count() == EXPECTED_SCENARIOS

    def test_seed_data_skips_when_present(self):
        WorldSetting.objects.create(
            name="Existing World",
            description="Placeholder",
            ai_instructions="Placeholder",
        )

        call_command("seed_data")

        # No fixture load happened — the single pre-existing world is untouched.
        assert WorldSetting.objects.count() == 1
        assert Scenario.objects.count() == 0

    def test_seed_data_force_reloads_when_present(self):
        call_command("seed_data")
        original_name = WorldSetting.objects.get(pk=1).name

        world = WorldSetting.objects.get(pk=1)
        world.name = "Tampered Name"
        world.save()

        call_command("seed_data", "--force")

        # loaddata upserts by pk, so the tampered world is restored, no dupes.
        assert WorldSetting.objects.get(pk=1).name == original_name
        assert WorldSetting.objects.count() == EXPECTED_WORLDS
        assert Scenario.objects.count() == EXPECTED_SCENARIOS
