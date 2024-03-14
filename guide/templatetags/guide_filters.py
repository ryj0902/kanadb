from django import template
import re

register = template.Library()


@register.filter()
def card_filter(value):
    # 정규 표현식을 사용하여 패턴을 찾고 링크를 추가합니다.
    return re.sub(
        r"\{(.+?)\}\((\d+)\)", r'<a href="#" onclick="selectCard(\2, 0)">\1</a>', value
    )
