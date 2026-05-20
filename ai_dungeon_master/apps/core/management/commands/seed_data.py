from django.core.management import call_command
from django.core.management.base import BaseCommand
from ai_dungeon_master.apps.world.models import Scenario, WorldSetting

class Command(BaseCommand):
    help = "Load initial world and scenario seed data (idempotent)."

    def handle(self, *args, **options):
        if WorldSetting.objects.exists():
            self.stdout.write(
                self.style.WARNING("Seed data already present — skipping.")
            )
            return

        call_command("loaddata", "fixtures/initial_data.json", verbosity=0)
        
        world_count = WorldSetting.objects.count()
        scenario_count = Scenario.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed data loaded successfully: "
                f"{world_count} world(s), {scenario_count} scenario(s)."
            )
        )