import re

from django import template

register = template.Library()

# 가이드 본문의 {카드 이름}(카드 id) 문법 -> 카드 상세를 여는 링크
CARD_LINK_PATTERN = re.compile(r"\{(.+?)\}\((\d+)\)")


@register.filter()
def card_filter(value):
    return CARD_LINK_PATTERN.sub(
        r'<a href="javascript:void(0);" onclick="selectCard(\2, 0)">\1</a>', value
    )
