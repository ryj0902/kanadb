"""PNG 카드 이미지 -> WebP 변환 후 PNG 삭제 (로컬 전용, pyvips 필요)

    python manage.py convert_card_images                    # static/card/Texture2D
    python manage.py convert_card_images D:/data/Texture2D --keep-png

Windows에서 libvips DLL 위치는 VIPS_BIN 환경변수(.env)로 지정한다 (예: C:\vips\bin).
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

# libvips는 내부적으로 멀티스레드를 쓰므로 작업자는 CPU의 절반 정도
WORKERS = max(2, (os.cpu_count() or 4) // 2)


def load_pyvips():
    vips_bin = os.environ.get("VIPS_BIN")
    if vips_bin and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(vips_bin)
    import pyvips  # 파이프라인 전용 의존성

    return pyvips


def convert(pyvips, png_path):
    image = pyvips.Image.new_from_file(str(png_path), access="sequential")
    image.write_to_file(
        str(png_path.with_suffix(".webp")), Q=85, lossless=False, effort=4
    )


class Command(BaseCommand):
    help = "PNG 카드 이미지를 WebP로 변환한다"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            nargs="?",
            type=Path,
            default=settings.BASE_DIR / "static" / "card" / "Texture2D",
        )
        parser.add_argument(
            "--keep-png", action="store_true", help="변환 후 PNG를 지우지 않는다"
        )

    def handle(self, *args, **options):
        pyvips = load_pyvips()
        png_files = sorted(
            path
            for path in options["directory"].rglob("*")
            if path.suffix.lower() == ".png"
        )
        self.stdout.write(f"PNG {len(png_files)}개 변환 (작업자 {WORKERS})")

        failed = []
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(convert, pyvips, path): path for path in png_files
            }
            for done, future in enumerate(as_completed(futures), start=1):
                try:
                    future.result()
                except Exception as exc:  # noqa: BLE001 - 실패 파일만 모아 보고
                    failed.append(futures[future])
                    self.stderr.write(f"[ERROR] {futures[future]}: {exc}")
                if done % 500 == 0:
                    self.stdout.write(f"  {done}/{len(png_files)}")

        if not options["keep_png"]:
            for path in png_files:
                if path not in failed:
                    path.unlink()

        self.stdout.write(
            self.style.SUCCESS(
                f"완료: {len(png_files) - len(failed)}개, 실패 {len(failed)}개"
            )
        )
