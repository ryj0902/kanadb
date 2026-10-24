"""가이드 마크다운 파일과 티어 리스트(투표) 연결"""

from django.conf import settings
from django.http import Http404
from django.utils.translation import get_language

GUIDE_DIR = settings.BASE_DIR / "templates" / "guide"

# 투표 카테고리 -> 티어 리스트가 붙는 가이드 파일
VOTE_GUIDES = {
    "unique": "guide3.md",  # 유니크 티어 리스트
    "empire_dr": "guide4.md",  # 제국 DR 추종자 티어 리스트
}


def guide_files():
    """현재 언어의 가이드 마크다운 파일 목록"""
    return sorted((GUIDE_DIR / get_language()).glob("*.md"))


def guide_title(path):
    """첫 줄의 '# 제목'"""
    with open(path, encoding="utf-8") as f:
        return f.readline().rstrip().split("# ")[1]


def read_guide(guide_name):
    """가이드 마크다운 원문 (목록에 없는 파일이면 404)"""
    for path in guide_files():
        if path.name == guide_name:
            return path.read_text(encoding="utf-8")
    raise Http404


def vote_category(guide_name):
    """티어 리스트가 붙는 가이드면 투표 카테고리, 아니면 None"""
    for category, vote_guide_name in VOTE_GUIDES.items():
        if guide_name == vote_guide_name:
            return category
    return None
