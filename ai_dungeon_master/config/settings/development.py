from .base import *

DEBUG = True
SECRET_KEY = "dev-insecure-key-not-for-production-change-me"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

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

# Show SQL queries in console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        }
    },
}
