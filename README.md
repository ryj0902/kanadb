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
tests/                  pytest 특성화 테스트, tests/visual/(화면 비교, 브라우저 점검)
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
git pull                                   # deploy 브랜치
pip install -r requirements.txt
python manage.py migrate                   # 모델이 바뀐 배포에서만 실제 변경이 생긴다
python manage.py compilemessages --ignore=venv
python manage.py collectstatic --noinput   # DJANGO_STATIC_ROOT를 소스 static/로 두었다면 생략
# 앱 서버 재시작
```

### 첫 배포 때 한 번만 (리팩토링 + Python 3.14 / Django 6.1 / MariaDB 12.3 업그레이드)

Django 6.1은 Python 3.12 이상, MariaDB 10.11 이상에서만 동작한다.
기존 서버(Ubuntu 22.04, Python 3.10, MariaDB 10.6)는 둘 다 맞지 않으므로 **아래 순서대로** 올린 뒤 새 코드를 받는다.
MariaDB 10.6은 2026년 7월에 지원이 끝나 이제 보안 패치도 나오지 않는다.

**0. 백업** (이 단계 동안 사이트는 그대로 돌아간다)

```bash
mkdir -p ~/backup
mysqldump -u root -p --all-databases --single-transaction --routines --events > ~/backup/all-$(date +%F).sql
cp <프로젝트 경로>/kanadb/settings.py ~/backup/settings.py.server   # 서버에서 고쳐 쓰던 설정
systemctl cat gunicorn > ~/backup/gunicorn.service.txt              # ExecStart의 venv 경로, User 확인용
```

**1. MariaDB 10.6 -> 12.3 LTS** (Ubuntu 22.04 기본 저장소에는 10.6뿐이라 MariaDB 공식 저장소를 쓴다)

```bash
sudo systemctl stop gunicorn
curl -LsSO https://r.mariadb.com/downloads/mariadb_repo_setup
sudo bash mariadb_repo_setup --mariadb-server-version="mariadb-12.3"
sudo apt-get update
sudo apt-get install mariadb-server mariadb-client   # 10.6 패키지를 교체 (데이터 /var/lib/mysql 과 설정은 유지)
                                                    # 설정 파일을 바꿀지 물으면 기존 것 유지(N)
sudo systemctl restart mariadb
sudo mariadb-upgrade                                 # 시스템 테이블 갱신 ("already upgraded"면 정상)
mariadb -u root -p -e "SELECT VERSION(); SELECT COUNT(*) FROM kanadb.card_vote;"
```

- 12.x에는 `mysql`/`mysqldump` 명령이 없을 수 있다. 이때는 `mariadb`/`mariadb-dump`를 쓰면 되고 옵션은 같다.
  예를 들어 card.sql 적용은 `mariadb -u <사용자> -p kanadb < card.sql`.
  예전 명령 이름을 그대로 쓰려면 `sudo apt-get install mariadb-client-compat`.
- MariaDB가 뜨지 않으면 먼저 `sudo journalctl -u mariadb -n 50`으로 원인을 본다.
  최후 수단은 기존 데이터 디렉터리를 옮겨 두고 백업으로 복원하는 것이다.
  ```bash
  sudo systemctl stop mariadb && sudo mv /var/lib/mysql /var/lib/mysql.10.6
  sudo mariadb-install-db --user=mysql && sudo systemctl start mariadb
  sudo mariadb < ~/backup/all-<날짜>.sql && sudo mariadb-upgrade --force
  ```

**2. Python 3.14 설치** (시스템 `python3`(3.10)는 Ubuntu 도구가 쓰므로 바꾸지 않고 옆에 설치한다)

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.14 python3.14-venv
python3.14 --version
```

PPA에 3.14가 없으면 uv로 설치한다: `curl -LsSf https://astral.sh/uv/install.sh | sh` 후 `uv python install 3.14`.
이 경우 아래 venv는 `uv venv --python 3.14 --seed venv`로 만든다.

**3. 설정 옮기기, venv 다시 만들기, 새 코드 받기**

1. **서버 설정 옮기기**: 서버에서 직접 고쳐 쓰던 `kanadb/settings.py`의 값을 프로젝트 루트 `.env`로 옮긴다
   (`DEBUG`, `ALLOWED_HOSTS`, DB 정보, static 경로 등, `.env.example` 참고). 설정 파일은 이제 `kanadb/settings/` 패키지다.
   옮긴 뒤 `git checkout -- kanadb/settings.py`로 서버의 수정분을 버려야 pull이 충돌하지 않는다.
   - `.env`가 없거나 `DJANGO_ALLOWED_HOSTS`가 비어 있으면 운영 설정이 시작을 거부한다(DEBUG가 켜진 채 뜨지 않도록).
   - 프록시 수는 `DJANGO_NUM_PROXIES`로 맞춘다. 투표 IP 판별에 쓰인다.
     - nginx만 있으면 1 (기본값, 현재 서버)
     - 로드밸런서 + nginx면 2
   - 지금처럼 소스의 `static/`을 웹서버가 직접 서빙한다면 `DJANGO_STATIC_ROOT=<프로젝트 경로>/static`.
2. **migrations**: 이제 git에 포함된다. 서버에서 직접 만들어 둔 `card/migrations`, `npc/migrations`가 있으면
   pull 전에 다른 곳으로 옮긴다.
3. **venv와 코드**: venv는 gunicorn.service의 ExecStart가 가리키는 경로에 다시 만든다(아래는 `<프로젝트 경로>/venv`인 경우).
   ```bash
   cd <프로젝트 경로>
   mv venv venv.bak-py310                    # 되돌리기용
   python3.14 -m venv venv
   source venv/bin/activate
   git pull                                  # deploy 브랜치
   pip install -r requirements.txt           # Django 6.1 + gunicorn
   python manage.py migrate --fake-initial   # 기존 테이블은 두고 이력만 맞춘다
   python manage.py compilemessages --ignore=venv --ignore=venv.bak-py310
   python manage.py collectstatic --noinput  # DJANGO_STATIC_ROOT를 소스 static/로 두었다면 생략
   sudo systemctl start gunicorn
   ```
4. **card.sql**: 새 `build_gamedata`로 만든 card.sql부터는 `card_card`/`npc_npc`에 기본 키가 생긴다. 적용 방법은 같다.

**4. 확인**

```bash
python -c "import sys, django; print(sys.version.split()[0], django.get_version())"   # 3.14.x 6.1.x
python manage.py check --deploy
sudo systemctl status gunicorn
```

브라우저로 카드 검색, 덱, 가이드 투표, NPC 페이지를 한 번씩 열어 본다. 문제가 없으면 `venv.bak-py310`은 지워도 된다.

**되돌리기**: 아래 순서로 되돌린다. MariaDB 12.3은 이전 코드(Django 4.2)와도 동작하므로 DB는 그대로 둔다.
1. `venv.bak-py310`을 `venv`로 되돌린다.
2. 이전 deploy 커밋으로 `git checkout`한다.
3. `~/backup/settings.py.server`를 복원한다.
4. gunicorn을 재시작한다.

### 이후 버전 업그레이드

- 버전은 `requirements/*.txt`에 고정한다.
  - 올릴 때는 로컬에서 `pip install -r requirements/dev.txt`를 하고, `pytest`와 화면 점검을 통과시킨 뒤 커밋한다.
  - 서버는 평소 배포의 `pip install -r requirements.txt`로 따라온다.
- Python 버전을 바꿀 때는 `.python-version`, `pyproject.toml`(ruff `target-version`), `.github/workflows/ci.yml`을 함께 바꾼다.
  서버는 위 2~3단계처럼 새 Python으로 venv를 다시 만든다.
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
