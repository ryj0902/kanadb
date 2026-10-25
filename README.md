# kanadb
Unofficial Kanatales Card Search Web DB

카나테일즈 카드 검색, 덱 편집, NPC 덱, 가이드(티어 투표)를 제공하는 Django 사이트.

## 구성

- Python 3.14, Django 6.1, MariaDB 10.11 이상(운영 12.3 LTS), 한국어/영어(i18n_patterns, msgid는 한국어 원문)
- 프론트엔드: Django 템플릿 + 빌드 도구 없는 Vanilla ES 모듈 + 일반 CSS(BEM)

```
kanadb/                 설정 (settings/{base,dev,prod}.py, 값은 .env/환경변수)
core/                   공통: context processor, 템플릿 태그, IP 도우미, makemessages
card/                   카드 검색/상세, 게임 데이터 변환(gamedata.py, 관리 명령)
  querysets.py          검색 조건 -> QuerySet
  presenters.py         카드 -> 화면 표시 데이터
deck/                   덱 편집, 덱 규칙/통계(services.py)
guide/                  가이드 마크다운, 티어 투표(registry.py, services.py)
npc/                    NPC 목록/상세, catalog.py(목록과 난이도/층 이동의 단일 출처)
templates/
  base.html, layouts/   페이지 뼈대, 2단 레이아웃(본문 + 카드 상세)
  components/           카드 타일, 카드 상세, 통계 막대
  card/ deck/ guide/ npc/   페이지 템플릿. 한 페이지 안에서만 쓰는 조각은 {% partialdef %}로 같은 파일에 두고
                            (AJAX는 "page.html#partial"로 렌더), 여러 화면이 쓰는 조각만 _*.html
static/
  css/{base,layout,components,pages}/
  js/{core,components,pages}/   페이지마다 <script type="module"> 하나
  vendor/               html2canvas (캡처할 때만 불러옴)
  fonts/
  card/Texture2D, card/TextAsset   게임 데이터 (git 제외)
tests/                  pytest 특성화 테스트, tests/visual/(화면 비교, 브라우저 점검) - 로컬 전용 (git 제외)
notebooks/              예전 데이터 갱신 노트북(참고용)
```

## 로컬 개발

Python 3.14와 MariaDB 10.11 이상이 필요하다(`.python-version` 참고, 운영과 같은 MariaDB 12.3 권장).

```bash
py -3.14 -m venv venv                        # Linux/macOS: python3.14 -m venv venv
venv\Scripts\activate
pip install -r requirements/dev.txt          # 게임 데이터 갱신까지 하려면 requirements/pipeline.txt도
```

프로젝트 루트에 `.env`를 만든다 (git 제외, 예시는 `.env.example`).

```
DJANGO_ENV=dev
DB_PW=<로컬 MySQL 비밀번호>
```

```bash
python manage.py migrate
python manage.py compilemessages --ignore=venv
python manage.py runserver
```

게임 데이터는 아래 "게임 데이터 갱신"의 `build_gamedata`로 채우거나 `card.sql`을 로컬 DB에 적용한다.

## 테스트와 점검

`tests/`는 git에 올리지 않고 로컬에만 둔다. CI는 lint와 번역 컴파일만 확인한다.

```bash
pytest                                   # 특성화 테스트 (SQLite + tests/fixtures/gamedata.json.gz)
ruff check . && ruff format --check .
djlint templates --lint
```

- 결과 비교용 golden 파일은 `tests/golden/`에 있다. 동작을 **의도적으로** 바꿨을 때만
  `UPDATE_GOLDEN=1 pytest`로 다시 기록하고 diff를 검토한다.
- fixture는 로컬 DB에서 `python tests/build_fixture.py`로 만든다.
- 화면/브라우저 점검 (로컬 서버 실행 중):

  ```bash
  python -m playwright install chromium            # 처음 한 번
  python tests/visual/capture.py capture before    # 변경 전 스크린샷
  python tests/visual/capture.py capture after     # 변경 후
  python tests/visual/capture.py compare before after
  python tests/visual/interactions.py              # 링크 복사, 드래그, 투표 등 동작 점검
  ```

- `pre-commit install`로 커밋 때 ruff/djlint를 자동 실행할 수 있다.

## 게임 데이터 갱신 (로컬에서 card.sql 생성 -> 서버 적용)

서버에서 하는 작업은 이전과 같다(압축 업로드 -> 해제 -> card.sql 적용). 로컬의 생성 과정만 노트북 대신 관리 명령으로 한다.

1. 새 이미지(png)를 `static/card/Texture2D`에 넣고 변환한다.
   ```bash
   python manage.py convert_card_images          # png -> webp, png 삭제
   ```
2. `static/card/TextAsset`을 새 데이터로 바꾸고 card.sql을 만든다.
   ```bash
   python manage.py build_gamedata               # 로컬 DB 갱신 + static/card/card.sql
   python manage.py build_gamedata --reset       # 예전 노트북이 만든 테이블이면 처음 한 번
   ```
   - 로컬 DB의 `card_card`, `npc_npc`만 다시 채운다(투표는 그대로).
   - `mysqldump` 경로는 `.env`의 `MYSQLDUMP`, libvips 경로는 `VIPS_BIN`.
3. `card.sql`, `Texture2D`, `TextAsset`을 압축해 서버에 올리고, 서버에서 `card.sql`을 DB에 적용한다.

## 코드 배포 (main -> deploy)

평소 배포:

```bash
cd /home/ubuntu/kanadb && source venv/bin/activate
git pull                                   # 서버의 deploy 브랜치 (origin/main 추적)
pip install -r requirements.txt
python manage.py migrate                   # 모델이 바뀐 배포에서만 실제 변경이 생긴다
python manage.py compilemessages --ignore=venv
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

- gunicorn은 systemd drop-in(`/etc/systemd/system/gunicorn.service.d/venv.conf`)으로 프로젝트의 `venv/bin/gunicorn`을 실행한다.
- 설정은 프로젝트 루트의 `.env`에 있다. gunicorn.service의 `EnvironmentFile`(`kanadb.env`)도 읽히며, 같은 이름의 값은 `kanadb.env`가 우선한다.

### 버전 업그레이드

- 버전은 `requirements/*.txt`에 고정한다.
  - 올릴 때는 로컬에서 `pip install -r requirements/dev.txt`를 하고, `pytest`와 화면 점검을 통과시킨 뒤 커밋한다.
  - 서버는 평소 배포의 `pip install -r requirements.txt`로 따라온다.
- Python 버전을 바꿀 때는 `.python-version`, `pyproject.toml`(ruff `target-version`), `.github/workflows/ci.yml`을 함께 바꾼다.
  서버는 새 Python으로 같은 경로에 venv를 다시 만들고(`mv venv venv.bak` 후 `python3.X -m venv venv`, `pip install -r requirements.txt`) gunicorn을 재시작한다.
- Django는 다음 LTS인 6.2(2027년 4월 예정)로 올리는 것을 권장한다.
  올리기 전에 릴리스 노트에 적힌 지원 Python/DB 버전을 서버 버전과 비교한다.

## NPC 목록/탐색 관리

`npc/catalog.py`가 NPC 목록 페이지와 상세 페이지의 난이도/층 이동을 함께 만든다.

- 던전 추가/복각: 해당 Section의 Block에 `Dungeon(...)` 한 줄 추가 (복각은 복사)
  ```python
  # 이지/노말/하드 x 5층 (난이도마다 id 천의 자리 +1)
  Dungeon(Text("EV19", _("새 이벤트")), standard_difficulties(99191101, 5)),
  # id 규칙이 다르면 층을 직접 나열
  Dungeon(_("새 던전"), single([Floor(97131101, _("1층")), Floor(97139999, _("BOSS"))])),
  ```
- 숨김: 해당 줄을 주석 처리하거나 빈 칸이면 `None`
- 카탈로그에 없는 NPC id는 상세 페이지에서 덱만 보이고 이동 UI는 숨겨진다.
- 새 문자열은 `python manage.py makemessages -l ko -l en`으로 번역 파일에 추가한다.

## 네이밍 규칙

| 대상 | 용도 | 규칙 | 예 |
|---|---|---|---|
| `class` | 스타일 전용 | BEM `block__element--modifier` | `card-tile__stat--hp` |
| 상태 class | JS가 바꾸는 상태 | `is-` 접두사 | `is-active`, `is-horizontal` |
| `data-*` | JS 훅/데이터 | kebab-case | `data-action="select-card" data-card-id="1"` |
| `id` | 페이지에서 하나뿐인 앵커만 | kebab-case | - |
| `name` | 폼 필드 | snake_case | `size_min` |
| JS | 변수/함수 camelCase, 상수 UPPER_SNAKE, 파일 kebab-case.js | | `selectCard`, `card-detail.js` |
| JSON | 서버 <-> JS | snake_case | `card_id` |

CSS는 class만, JS는 `data-*`만 보므로 한쪽을 바꿔도 다른 쪽이 깨지지 않는다.

## 환경변수

| 이름 | 설명 | 기본값 |
|---|---|---|
| `DJANGO_ENV` | `dev` / `prod` | `prod` |
| `DJANGO_SECRET_KEY` | 비우면 `secret_key.txt` | - |
| `DJANGO_ALLOWED_HOSTS` | 쉼표 구분 (prod 필수) | - |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | HTTPS 사용 시 | - |
| `DJANGO_HTTPS` | HTTPS 쿠키 설정 | `False` |
| `DJANGO_NUM_PROXIES` | X-Forwarded-For를 붙이는 프록시 수 | `1` |
| `DJANGO_STATIC_ROOT` | collectstatic 대상 | `staticfiles/` |
| `DB_NAME`, `DB_USER`, `DB_PW`, `DB_HOST`, `DB_PORT` | MySQL 접속 | `kanadb`, `root`, -, `localhost`, `3306` |
| `MYSQLDUMP`, `VIPS_BIN` | 게임 데이터 갱신(로컬) | `mysqldump`, - |
