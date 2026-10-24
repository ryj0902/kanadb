"""게임 데이터(TextAsset) -> 로컬 DB(card_card, npc_npc) -> card.sql

로컬에서만 실행한다. 운영 서버에는 지금처럼 card.sql만 적용하면 된다.

    python manage.py build_gamedata                 # 기본 경로 사용
    python manage.py build_gamedata --reset         # 예전 노트북이 만든 테이블(PK 없음)을 새로 만든다
    python manage.py build_gamedata --no-dump       # card.sql은 만들지 않음

mysqldump 경로는 MYSQLDUMP 환경변수(.env)로 지정할 수 있다 (기본: PATH의 mysqldump).
"""

import os
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from card.gamedata import GameData, build_cards, build_npcs, fix_swapped_card_images
from card.models import Card
from npc.models import Npc

STATIC_CARD_DIR = settings.BASE_DIR / "static" / "card"
TABLES = [Card, Npc]


class Command(BaseCommand):
    help = "게임 데이터로 card_card / npc_npc 테이블을 채우고 card.sql을 만든다 (로컬 전용)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--text-asset", type=Path, default=STATIC_CARD_DIR / "TextAsset"
        )
        parser.add_argument(
            "--texture", type=Path, default=STATIC_CARD_DIR / "Texture2D"
        )
        parser.add_argument("--output", type=Path, default=STATIC_CARD_DIR / "card.sql")
        parser.add_argument(
            "--reset",
            action="store_true",
            help="card_card / npc_npc 테이블을 지우고 모델 정의대로 다시 만든다",
        )
        parser.add_argument(
            "--no-dump", action="store_true", help="card.sql을 만들지 않는다"
        )
        parser.add_argument(
            "--skip-image-fix",
            action="store_true",
            help="뒤바뀐 카드 이미지 파일 이름 바로잡기를 건너뛴다",
        )

    def handle(self, *args, **options):
        if not options["skip_image_fix"]:
            fix_swapped_card_images(options["texture"], log=self.stdout.write)

        self.stdout.write("게임 데이터 변환 중...")
        data = GameData(options["text_asset"])
        cards = build_cards(data, options["texture"])
        npcs = build_npcs(data)
        self.stdout.write(f"카드 {len(cards)}장, NPC {len(npcs)}개")

        if options["reset"]:
            self.recreate_tables()
        else:
            self.check_tables()

        with transaction.atomic(), foreign_key_checks_disabled():
            replace_rows(Card, cards)
            replace_rows(Npc, npcs)
        self.stdout.write(self.style.SUCCESS("로컬 DB 갱신 완료"))

        if not options["no_dump"]:
            dump_tables(options["output"])
            self.stdout.write(self.style.SUCCESS(f"{options['output']} 생성 완료"))

    def check_tables(self):
        """예전 노트북(to_sql)이 만든 테이블은 PK가 없다 -> --reset 안내"""
        with connection.cursor() as cursor:
            for model in TABLES:
                table = model._meta.db_table
                primary_key = connection.introspection.get_primary_key_column(
                    cursor, table
                )
                if primary_key is None:
                    raise CommandError(
                        f"{table} 테이블에 기본 키가 없습니다 (예전 방식으로 만든 테이블). "
                        "--reset 옵션으로 다시 만드세요."
                    )

    def recreate_tables(self):
        existing = connection.introspection.table_names()
        with foreign_key_checks_disabled(), connection.schema_editor() as editor:
            for model in TABLES:
                if model._meta.db_table in existing:
                    editor.delete_model(model)
                editor.create_model(model)
        self.stdout.write("card_card / npc_npc 테이블을 새로 만들었습니다")


class foreign_key_checks_disabled:
    """MySQL: 투표(card_vote)가 참조하는 카드 테이블을 비우고 다시 채우는 동안 FK 검사 끔"""

    def __enter__(self):
        if connection.vendor == "mysql":
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    def __exit__(self, *exc):
        if connection.vendor == "mysql":
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def replace_rows(model, rows):
    """테이블의 모든 행을 바꾼다 (ORM delete를 쓰지 않아 투표가 함께 지워지지 않는다)"""
    table = connection.ops.quote_name(model._meta.db_table)
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table}")
    model.objects.bulk_create([model(**row) for row in rows], batch_size=1000)


def dump_tables(output):
    """mysqldump로 card_card, npc_npc를 card.sql로 내보낸다 (서버에 적용하는 파일)"""
    db = settings.DATABASES["default"]
    command = [
        os.environ.get("MYSQLDUMP", "mysqldump"),
        f"--host={db['HOST'] or 'localhost'}",
        f"--port={db['PORT'] or '3306'}",
        f"--user={db['USER']}",
        "--add-drop-table",  # 기존 테이블 삭제 후 생성
        db["NAME"],
        *[model._meta.db_table for model in TABLES],
    ]
    env = {
        **os.environ,
        "MYSQL_PWD": db["PASSWORD"],
    }  # 비밀번호는 명령줄에 남기지 않는다
    try:
        with open(output, "wb") as outfile:
            subprocess.run(
                command, stdout=outfile, stderr=subprocess.PIPE, env=env, check=True
            )
    except FileNotFoundError as exc:
        raise CommandError(
            f"mysqldump를 찾을 수 없습니다: {command[0]} (MYSQLDUMP 환경변수로 경로 지정)"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise CommandError(
            f"mysqldump 실패: {exc.stderr.decode(errors='replace')}"
        ) from exc
