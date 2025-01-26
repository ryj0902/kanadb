import numpy as np
from django.shortcuts import render
from django.utils.translation import gettext as _

from card.models import Card

from .models import Deck

deck_total = Deck.objects.all()


def index(request):
    decks = Deck.objects.all()

    context = {"deck_list": decks}

    return render(request, "deck/index.html", context)


def deck_detail(request, deck_id):
    deck = deck_total.filter(id=deck_id)[0]
    setup = list(map(lambda x: int(x), deck.setup.split(",")))

    card_ids, counts = np.unique(setup, return_counts=True)

    cards = list()
    for card_id, count in zip(card_ids, counts):
        card = Card.objects.all().filter(id=card_id)[0]
        card.count = count
        cards.append(card)

    sorted_cards = sorted(cards[1:], key=lambda card: (card.category, card.size))

    # parse string after sorting
    for card in cards:
        Card.parse_static_url(card)
        Card.parse_to_string(card)

    # floor navigation
    deck_floors = deck_total.filter(
        id__gte=deck_id // 100 * 100, id__lt=(deck_id // 100 + 1) * 100
    )
    floors = list(deck_floors.values_list("id", flat=True))
    floor_down = deck_id - 1 if deck_id - 1 in floors else -1
    floor_up = deck_id + 1 if deck_id + 1 in floors else -1

    context = {
        "chapter_name": deck.chapter_name,
        "chapter_name_us": deck.chapter_name_us,
        "loading_name": deck.loading_name,
        "loading_name_us": deck.loading_name_us,
        "loading_desc": deck.loading_desc,
        "loading_desc_us": deck.loading_desc_us,
        "card_character": cards[0],
        "card_list": sorted_cards,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
        "floors": floors,
        "current_floor": deck_id,
        "floor_down": floor_down,
        "floor_up": floor_up,
    }

    return render(request, "deck/deck_detail.html", context)


"""
def deck_temp(request):
    cards = list()
    card_ids = [
        1402300,  # 아이돌 로자리아
        2003060,  # 서머 나이트
        2008710,  # 라이브 뮤직 - 핀테일
        2008710,
        2100170,  # 재액의 소용돌이
        2007750,  # 송편 두 개
        2007750,
        2007750,
        2200160,  # 카나의 제단
        2200160,
        2300410,  # 신토불이
        2001210,  # 신의의 기사
        2003520,  # 성역의 문
        2003520,
        2003850,  # 증원 부대
        2004430,  # 천마의 할로윈 파티
        2004500,  # 새해 인사
        2007630,  # 겨울의 휴일
        2100080,  # 에필로그
        2100120,  # 장난 금지
        2100300,  # 두꺼비집
        2100350,  # 엘 브릴로
        2300230,  # 침실 놀이
        2004010,  # 강제 중재
        2004170,  # 자매의 재회
        2005620,  # [僞] 강제 중재
        2005660,  # [僞] 자매의 재회
        2004740,  # 식사 예절
        2100200,  # 시공관리국 카나
        2100320,  # 코인 팩토리
        2100730,  # 궁극의 아이돌
    ]
    card_ids, counts = np.unique(card_ids, return_counts=True)
    for card_id, count in zip(card_ids, counts):
        card = Card.objects.all().filter(id=card_id)[0]
        card.count = count
        cards.append(card)

    sorted_cards = sorted(cards[1:], key=lambda card: (card.category, card.size))

    # parse string after sorting
    for card in cards:
        Card.parse_static_url(card)
        Card.parse_to_string(card)

    context = {
        "chapter_name": "EV11 300클 올스펠덱",
        "chapter_name_us": "EV11 공략",
        "loading_name": "아이돌 로자리아 못생김",
        "loading_name_us": "EV11 공략",
        "loading_desc": "이게 내 최선이다",
        "loading_desc_us": "EV11 공략",
        "card_character": cards[0],
        "card_list": sorted_cards,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }

    return render(request, "deck/deck_detail.html", context)
"""
