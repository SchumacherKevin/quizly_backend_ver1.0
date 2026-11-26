"""
Django settings for the Quizly backend.

Secrets and environment specific values are read from the ``.env`` file
in the project root (see ``.env.template``).
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

from core.env import get_bool, get_int, get_list

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = get_bool("DEBUG", False)

ALLOWED_HOSTS = get_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "auth_app",
    "quiz_app",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

PASSWORD_VALIDATION = "django.contrib.auth.password_validation"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{PASSWORD_VALIDATION}.UserAttributeSimilarityValidator"},
    {"NAME": f"{PASSWORD_VALIDATION}.MinimumLengthValidator"},
    {"NAME": f"{PASSWORD_VALIDATION}.CommonPasswordValidator"},
    {"NAME": f"{PASSWORD_VALIDATION}.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "static/"


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}


# CORS (frontend sends credentials, so origins must be explicit)
CORS_ALLOWED_ORIGINS = get_list(
    "CORS_ORIGINS", ["http://127.0.0.1:5500", "http://localhost:5500"]
)

CORS_ALLOW_CREDENTIALS = True


# Django REST framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "auth_app.authentication.CookieJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# JWT (simplejwt) and auth cookies
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}

AUTH_COOKIE_SAMESITE = "Lax"

AUTH_COOKIE_SECURE = not DEBUG


# Quizly
# AI provider for quiz generation: "gemini" (default) or "openai"
# (any OpenAI-compatible API, e.g. OpenAI, Mistral, Groq, Ollama).
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Only used with AI_PROVIDER=openai. Local servers (Ollama, LM Studio) do
# not need a key.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

MAX_VIDEO_MINUTES = get_int("MAX_VIDEO_MINUTES", 15)
