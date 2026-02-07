from collections import defaultdict

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


RANK_THRESHOLDS = [(200, "E"), (600, "D"), (1200, "C"), (2000, "B"), (9999, "A")]


def calculate_statistics(cards: list[Card]):
    stat_point = 0
    stat_category = [["amount", 0], ["char", 0], ["spell", 0]]
    stat_size = [0] * 10
    stat_theme = [["vita", 0], ["academy", 0], ["crux", 0], ["darklore", 0], ["sg", 0]]
    stat_rarity = [
        ["COMMON", 0],
        ["UNCOMMON", 0],
        ["SUPERIOR", 0],
        ["RARE", 0],
        ["DOUBLE_RARE", 0],
        ["UNIQUE", 0],
    ]
    ep_enh_dict = defaultdict(lambda: [0, 0])
    tag_enh_dict = defaultdict(lambda: [0, 0])
    tag_enh_us_dict = defaultdict(lambda: [0, 0])

    for card in cards:
        stat_point += card.count * card.point

        if card.category != 1:  # not count character
            stat_category[0][1] += card.count
            stat_category[card.category - 1][1] += card.count

        stat_size[card.size - 1] += card.count
        stat_theme[card.theme - 1][1] += card.count
        stat_rarity[card.rarity - 1][1] += card.count

        ep_enh_dict[card.episode][0] += card.count
        ep_enh_dict[card.episode][1] += card.count * card.enhance

        for t in card.tag.split(","):
            tag_enh_dict[t][0] += card.count
            tag_enh_dict[t][1] += card.count * card.enhance
        for t in card.tag_us.split(","):
            tag_enh_us_dict[t][0] += card.count
            tag_enh_us_dict[t][1] += card.count * card.enhance

    # make count-enhance string
    ep_enh_str_list = []
    for key, value in sorted(ep_enh_dict.items()):
        tmp = f"{Card.get_episode_string(key)}: {value[0]}"
        if value[1] != 0:
            tmp += f"(+{value[1]})"
        ep_enh_str_list.append(tmp)
    ep_enh_str = " | ".join(ep_enh_str_list)

    tag_enh_str_list = []
    for key, value in sorted(tag_enh_dict.items()):
        tmp = f"{key}: {value[0]}"
        if value[1] != 0:
            tmp += f"(+{value[1]})"
        tag_enh_str_list.append(tmp)
    tag_enh_str = " | ".join(tag_enh_str_list)

    tag_enh_str_us_list = []
    for key, value in sorted(tag_enh_us_dict.items()):
        tmp = f"{key}: {value[0]}"
        if value[1] != 0:
            tmp += f"(+{value[1]})"
        tag_enh_str_us_list.append(tmp)
    tag_enh_str_us = " | ".join(tag_enh_str_us_list)

    stat_rank_char = "E"
    for limit, rank_char in RANK_THRESHOLDS:
        if stat_point <= limit:
            stat_rank_char = rank_char
            break

    return {
        "stat_point": stat_point,
        "stat_rank_char": stat_rank_char,
        "stat_category": stat_category,
        "stat_size": stat_size,
        "stat_theme": stat_theme,
        "stat_rarity": stat_rarity,
        "ep_enh_str": ep_enh_str,
        "tag_enh_str": tag_enh_str,
        "tag_enh_str_us": tag_enh_str_us,
    }


def npc_detail(request, npc_id):
    npc = npc_total.filter(id=npc_id)[0]
    setup = list(map(lambda x: int(x), npc.setup.split(",")))

    card_ids, counts = np.unique(setup, return_counts=True)

    cards = list()
    for card_id, count in zip(card_ids, counts):
        card = Card.objects.get(id=card_id)
        card.count = count
        cards.append(card)

    sorted_cards = sorted(cards[1:], key=lambda card: (card.category, card.size))

    statistics = calculate_statistics(sorted_cards)

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
        "deck_card_list": sorted_cards,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
        "floors": floors,
        "current_floor": npc_id,
        "floor_down": floor_down,
        "floor_up": floor_up,
    }

    context |= statistics

    return render(request, "npc/npc_detail.html", context)
