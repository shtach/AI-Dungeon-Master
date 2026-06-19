from django.apps import AppConfig


class LegacyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_dungeon_master.apps.legacy"
    verbose_name = "Legacy"

    def ready(self):
        import ai_dungeon_master.apps.legacy.signals  # noqa: F401
