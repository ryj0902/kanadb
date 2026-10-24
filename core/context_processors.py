from django.conf import settings
from django.urls import translate_url
from django.utils.translation import get_language_info
from django.utils.translation import gettext_lazy as _


def layout(request):
    """카드 상세 패널의 가로/세로 전환 버튼 문구"""
    return {
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }


def language_urls(request):
    """언어 전환 메뉴: 현재 페이지(쿼리 포함)를 각 언어로 연 URL"""
    path = request.get_full_path()
    return {
        "language_urls": [
            {
                "code": code,
                "name_local": get_language_info(code)["name_local"],
                "url": translate_url(path, code),
            }
            for code, _name in settings.LANGUAGES
        ]
    }
