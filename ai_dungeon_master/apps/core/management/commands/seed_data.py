from django.core.management import call_command
from django.core.management.base import BaseCommand

from ai_dungeon_master.apps.world.models import Scenario, WorldSetting


class Command(BaseCommand):
    help = "Load initial world and scenario seed data (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reload seed data even if worlds already exist (upsert by pk).",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if WorldSetting.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    "Seed data already present — skipping. Use --force to reload."
                )
            )
            return

        call_command("loaddata", "initial_data", verbosity=0)

        world_count = WorldSetting.objects.count()
        scenario_count = Scenario.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed data loaded successfully: "
                f"{world_count} world(s), {scenario_count} scenario(s)."
            )
        )
