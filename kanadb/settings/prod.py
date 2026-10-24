"""운영 설정 (값은 서버의 .env 또는 환경변수로 지정)"""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import ALLOWED_HOSTS, SECRET_KEY
from .env import env_bool

DEBUG = False

if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY 또는 secret_key.txt가 필요합니다")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS가 필요합니다")

# HTTPS로 서비스할 때만 켠다 (http 환경에서 켜면 세션/CSRF 쿠키가 전송되지 않음)
if env_bool("DJANGO_HTTPS"):
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
