"""Настройки учебного проекта ПР7 для локального запуска."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Учебный ключ для локального запуска; на сервере задать переменную окружения.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "queryflow-pr5-local-development-key-only"
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "homepage.apps.HomepageConfig",
    "questions.apps.QuestionsConfig",
    "categories.apps.CategoriesConfig",
    "answers.apps.AnswersConfig",
    "participants.apps.ParticipantsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "queryflow.urls"
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
WSGI_APPLICATION = "queryflow.wsgi.application"
ASGI_APPLICATION = "queryflow.asgi.application"

# Служебная база Django. Предметная база ПР7 — data/queryflow.sqlite.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation."
             "UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation."
             "MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation."
             "CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation."
             "NumericPasswordValidator"},
]
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Панель SQL доступна только при локальной отладке.
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1", "::1"]
