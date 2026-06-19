from .base import *

DEBUG = True
SECRET_KEY = "dev-insecure-key-not-for-production-change-me"
ALLOWED_HOSTS = get_env("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

CSRF_TRUSTED_ORIGINS = get_env("CSRF_TRUSTED_ORIGINS", "").split(",") if get_env("CSRF_TRUSTED_ORIGINS", "") else []

# PostgreSQL credentials are read from .env (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
# To use SQLite locally instead, uncomment:
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "local_db" / "db.sqlite3",
#     }
# }

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["127.0.0.1"]

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    # TemplatesPanel disabled: patches Template._render and recurses with django-tailwind
    "debug_toolbar.panels.alerts.AlertsPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]

# Show logs
LOGGING["handlers"]["console_verbose"] = {
    "class": "logging.StreamHandler",
    "formatter": "verbose",
}
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console_verbose"],
    "level": "DEBUG",
    "propagate": False,
}

LOGGING["loggers"]["ai_dungeon_master.apps.ai"]["level"] = "DEBUG"
LOGGING["loggers"]["ai_dungeon_master.apps.game"]["level"] = "DEBUG"
