from django import template

from card.models import DECK_SIZE

register = template.Library()


@register.inclusion_tag("components/card_tile.html")
def card_tile(card, variant="grid"):
    """카드 타일

    variant
    - grid      : 검색 결과 (드래그 가능)
    - deck      : NPC/덱 요약의 덱 카드 (장수 표시)
    - character : NPC/덱 요약의 캐릭터 카드 (체력만 표시)
    """
    return {"card": card, "variant": variant}


@register.filter
def deck_percent(count):
    """덱 최대 장수 대비 비율(%) - {% widthratio count DECK_SIZE 100 %}와 같은 반올림"""
    return round(count / DECK_SIZE * 100)


@register.filter
def with_id(bound_field, element_id):
    """같은 폼 필드를 여러 번 그릴 때 id가 겹치지 않게 지정"""
    return bound_field.as_widget(attrs={"id": element_id})
