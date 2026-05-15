from .base import *

DEBUG = True
SECRET_KEY = "dev-insecure-key-not-for-production-change-me"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "desktop-im15h9i.tail0b55ff.ts.net"]
CSRF_TRUSTED_ORIGINS = ["https://desktop-im15h9i.tail0b55ff.ts.net"]
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

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]

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
