from django import template

from card.models import FILTER_ROW_SIZE

register = template.Library()


@register.filter
def split_by_9(value):
    """체크박스 목록을 한 줄에 FILTER_ROW_SIZE개씩 나눈다"""
    return [
        value[i : i + FILTER_ROW_SIZE] for i in range(0, len(value), FILTER_ROW_SIZE)
    ]
