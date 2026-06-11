from .base import *
import os

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# Only warnings and errors in production
LOGGING["loggers"]["ai_dungeon_master.apps.ai"]["level"] = "WARNING"
LOGGING["loggers"]["ai_dungeon_master.apps.game"]["level"] = "WARNING"