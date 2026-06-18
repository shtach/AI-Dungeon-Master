import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def get_env(var_name: str, default=None) -> str:
    value = os.environ.get(var_name, default)
    if value is None:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(f"Set the {var_name} environment variable")
    return value


SECRET_KEY = get_env(
    "DJANGO_SECRET_KEY", default="insecure-base-placeholder-override-in-each-env"
)
ALLOWED_HOSTS = get_env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tailwind",
    "theme",
    "django_htmx",
    "ai_dungeon_master.apps.ai",
    "ai_dungeon_master.apps.accounts",
    "ai_dungeon_master.apps.characters",
    "ai_dungeon_master.apps.game",
    "ai_dungeon_master.apps.game.combat",
    "ai_dungeon_master.apps.game.quests",
    "ai_dungeon_master.apps.world",
    "ai_dungeon_master.apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "ai_dungeon_master.config.urls"
WSGI_APPLICATION = "ai_dungeon_master.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("DB_NAME", "game_db"),
        "USER": get_env("DB_USER", "pgadmin"),
        "PASSWORD": get_env("DB_PASSWORD", ""),
        "HOST": get_env("DB_HOST", "localhost"),
        "PORT": get_env("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Resolve fixtures by name (e.g. `loaddata initial_data`) regardless of the
# runtime BASE_DIR — test settings override BASE_DIR to the inner package dir.
FIXTURE_DIRS = [BASE_DIR / "fixtures"]

TAILWIND_APP_NAME = "theme"
# `tailwind start` runs the standalone CLI watcher. `--watch=always` keeps it
# watching when stdin is closed (the case under docker-compose / headless), so
# the watcher container does not exit after the first build.
TAILWIND_STANDALONE_START_COMMAND_ARGS = (
    "-i static_src/src/styles.css -o static/css/dist/styles.css --watch=always"
)

GEMINI_API_KEY = get_env("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
AI_PROVIDER = os.environ.get("AI_PROVIDER", "gemini")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==========================================
# LOGGING
# ==========================================
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file_ai": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "ai.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "file_game": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "game.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "ai_dungeon_master.apps.ai": {
            "handlers": ["console", "file_ai"],
            "level": "DEBUG",
            "propagate": False,
        },
        "ai_dungeon_master.apps.game": {
            "handlers": ["console", "file_game"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}