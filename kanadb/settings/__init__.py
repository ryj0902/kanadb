"""설정 패키지

- base.py : 공통 설정 (비밀값/환경별 값은 환경변수 또는 프로젝트 루트의 .env)
- dev.py  : 로컬 개발 (DEBUG=True)
- prod.py : 운영 (DEBUG=False)

manage.py / wsgi.py / asgi.py가 DJANGO_ENV(기본 prod)로 모듈을 고른다.
DJANGO_SETTINGS_MODULE=kanadb.settings 로 지정된 기존 환경도 같은 규칙으로 동작한다.
"""

import os

if os.environ.get("DJANGO_SETTINGS_MODULE") == "kanadb.settings":
    from .env import BASE_DIR as _BASE_DIR
    from .env import load_dotenv

    load_dotenv(_BASE_DIR / ".env")
    if os.environ.get("DJANGO_ENV", "prod") == "dev":
        from .dev import *  # noqa: F403
    else:
        from .prod import *  # noqa: F403
