import os
from pathlib import Path

# BASE_DIR — это корень проекта (папка AI-Dungeon-Master)
# __file__ = .../ai_dungeon_master/config/settings/base.py
# .parent = settings/
# .parent.parent = config/
# .parent.parent.parent = ai_dungeon_master/
# .parent.parent.parent.parent = AI-Dungeon-Master/ это и есть BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Секретный ключ берём из .env файла (Для Лёхи)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-insecure-key-change-in-production')

DEBUG = True

ALLOWED_HOSTS = []

# Все установленные приложения
INSTALLED_APPS = [
    # Django встроенные
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Наши приложения
    'ai_dungeon_master.apps.accounts',
    'ai_dungeon_master.apps.characters',
    'ai_dungeon_master.apps.game',
    'ai_dungeon_master.apps.world',
    'ai_dungeon_master.apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Указываем где лежит главный urls.py
ROOT_URLCONF = 'ai_dungeon_master.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # BASE_DIR / 'templates' — это папка templates/ в корне проекта
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ai_dungeon_master.wsgi.application'

# База данных — берём из .env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'game_db'),
        'USER': os.environ.get('DB_USER', 'pgadmin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'zaq12wsx'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Статика (CSS, JS, картинки)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Куда редиректить после логина/логаута
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Anthropic API ключ (будет нужен позже)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')