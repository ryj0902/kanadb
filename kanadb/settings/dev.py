"""로컬 개발 설정"""

from .base import *  # noqa: F403
from .base import ALLOWED_HOSTS, SECRET_KEY

DEBUG = True

ALLOWED_HOSTS = ALLOWED_HOSTS or ["localhost", "127.0.0.1", "[::1]"]
SECRET_KEY = SECRET_KEY or "django-insecure-local-development-only"
