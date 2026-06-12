from .base import *

DEBUG = False
SECRET_KEY = get_env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = get_env("ALLOWED_HOSTS").split(",")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Run `python manage.py collectstatic --no-input` before deploying.

LOGGING["loggers"]["ai_dungeon_master.apps.ai"]["level"] = "WARNING"
LOGGING["loggers"]["ai_dungeon_master.apps.game"]["level"] = "WARNING"
