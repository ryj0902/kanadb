"""환경변수 읽기 도우미 (.env 파일 지원, 외부 패키지 없이)"""

import os
from pathlib import Path


def load_dotenv(path: Path):
    """KEY=VALUE 형식의 .env 파일을 읽어 아직 설정되지 않은 환경변수만 채운다"""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def env_str(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def env_int(key, default=0):
    value = os.environ.get(key)
    return int(value) if value not in (None, "") else default


def env_list(key, default=()):
    value = os.environ.get(key)
    if value is None:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def settings_module():
    """.env를 읽은 뒤 DJANGO_ENV(dev/prod, 기본 prod)에 맞는 설정 모듈 경로를 반환"""
    load_dotenv(BASE_DIR / ".env")
    return f"kanadb.settings.{os.environ.get('DJANGO_ENV', 'prod')}"
