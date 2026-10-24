"""공통 설정 (환경별 값은 dev.py / prod.py, 비밀값은 환경변수로)"""

from pathlib import Path

import pymysql

from .env import BASE_DIR, env_int, env_list, env_str, load_dotenv

pymysql.install_as_MySQLdb()

load_dotenv(BASE_DIR / ".env")


def read_secret_key():
    """DJANGO_SECRET_KEY 환경변수, 없으면 secret_key.txt"""
    secret_key = env_str("DJANGO_SECRET_KEY")
    if secret_key:
        return secret_key
    secret_key_file = BASE_DIR / "secret_key.txt"
    if secret_key_file.is_file():
        return secret_key_file.read_text().strip()
    return None


SECRET_KEY = read_secret_key()

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# X-Forwarded-For를 덧붙이는 신뢰 프록시 수 (nginx만 있으면 1, ALB + nginx면 2)
NUM_PROXIES = env_int("DJANGO_NUM_PROXIES", 1)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
    "card.apps.CardConfig",
    "guide.apps.GuideConfig",
    "npc.apps.NpcConfig",
    "deck.apps.DeckConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kanadb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.layout",
                "core.context_processors.language_urls",
            ],
        },
    },
]

WSGI_APPLICATION = "kanadb.wsgi.application"


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env_str("DB_NAME", "kanadb"),
        "USER": env_str("DB_USER", "root"),
        "PASSWORD": env_str("DB_PW", ""),
        "HOST": env_str("DB_HOST", "localhost"),
        "PORT": env_str("DB_PORT", "3306"),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "ko"
LANGUAGES = [
    ("ko", "Korean"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = Path(env_str("DJANGO_STATIC_ROOT", BASE_DIR / "staticfiles"))
# 소스 static/ 을 STATIC_ROOT로 직접 서빙하는 기존 운영 방식도 지원
STATICFILES_DIRS = [] if STATIC_ROOT == BASE_DIR / "static" else [BASE_DIR / "static"]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
