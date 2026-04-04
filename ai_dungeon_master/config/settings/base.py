import os
from pathlib import Path

from dotenv import load_dotenv

# Project root: base.py → settings/ → config/ → ai_dungeon_master/ → root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def get_env(var_name: str, default=None) -> str:
    value = os.environ.get(var_name, default)
    if value is None:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(f"Set the {var_name} environment variable")
    return value


# ─────────────────────────────────────
# SECURITY
# ─────────────────────────────────────
SECRET_KEY = get_env("DJANGO_SECRET_KEY", default="insecure-base-placeholder-override-in-each-env")
ALLOWED_HOSTS = get_env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ─────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "tailwind",
    "theme",
    "django_htmx",
    # Project apps
    "ai_dungeon_master.apps.accounts",
    "ai_dungeon_master.apps.characters",
    "ai_dungeon_master.apps.game",
    "ai_dungeon_master.apps.world",
    "ai_dungeon_master.apps.core",
]

# ─────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────
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

ROOT_URLCONF = "ai_dungeon_master.urls"
WSGI_APPLICATION = "ai_dungeon_master.wsgi.application"

# ─────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────
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

# ─────────────────────────────────────
# DATABASE
# ─────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("DB_NAME", "ai_dungeon_master"),
        "USER": get_env("DB_USER", "postgres"),
        "PASSWORD": get_env("DB_PASSWORD", ""),
        "HOST": get_env("DB_HOST", "localhost"),
        "PORT": get_env("DB_PORT", "5432"),
    }
}

# ─────────────────────────────────────
# AUTH
# ─────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ─────────────────────────────────────
# I18N
# ─────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────
# STATIC FILES
# ─────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ─────────────────────────────────────
# TAILWIND
# ─────────────────────────────────────
TAILWIND_APP_NAME = "theme"

# ─────────────────────────────────────
# ANTHROPIC
# ─────────────────────────────────────
ANTHROPIC_API_KEY = get_env("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-opus-4-6"
ANTHROPIC_MAX_TOKENS = 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
