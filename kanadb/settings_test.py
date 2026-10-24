"""테스트 전용 설정: MySQL 대신 SQLite 메모리 DB 사용"""

import os

os.environ.setdefault("DB_PW", "")

from kanadb.settings import *  # noqa: E402,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
