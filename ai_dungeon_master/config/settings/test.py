from .base import *

DEBUG = False
SECRET_KEY = "test-insecure-key-for-ci-and-pytest-only"

AUTH_PASSWORD_VALIDATORS = []

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

AI_PROVIDER = "mock"
