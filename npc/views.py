import numpy as np
from django.shortcuts import render
from django.utils.translation import gettext as _

from card.models import Card

from .models import Npc

npc_total = Npc.objects.all()


def index(request):
    npcs = Npc.objects.all()

    context = {"npc_list": npcs}

    return render(request, "npc/index.html", context)


def npc_detail(request, npc_id):
    npc = npc_total.filter(id=npc_id)[0]
    setup = list(map(lambda x: int(x), npc.setup.split(",")))

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
    npc_floors = npc_total.filter(
        id__gte=npc_id // 100 * 100, id__lt=(npc_id // 100 + 1) * 100
    )
    floors = list(npc_floors.values_list("id", flat=True))
    floor_down = npc_id - 1 if npc_id - 1 in floors else -1
    floor_up = npc_id + 1 if npc_id + 1 in floors else -1

    context = {
        "chapter_name": npc.chapter_name,
        "chapter_name_us": npc.chapter_name_us,
        "loading_name": npc.loading_name,
        "loading_name_us": npc.loading_name_us,
        "loading_desc": npc.loading_desc,
        "loading_desc_us": npc.loading_desc_us,
        "card_character": cards[0],
        "card_list": sorted_cards,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
        "floors": floors,
        "current_floor": npc_id,
        "floor_down": floor_down,
        "floor_up": floor_up,
    }

    return render(request, "npc/npc_detail.html", context)
