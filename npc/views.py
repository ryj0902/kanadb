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

    # --- Floor Navigation 로직 시작 ---
    npc_id_str = str(npc_id)
    id_len = len(npc_id_str)
    is_weekly = npc_id_str.startswith("98")

    difficulty_list = []
    floors_in_current_diff = []
    current_diff = 0
    current_floor_num = 0

    # [CASE A: 주간 / CASE B: 4자리 / CASE C: 일반] 분기 로직은 동일하게 유지하되
    # 각 분기 마지막에 floors_in_current_diff가 ID 리스트로 채워지게 합니다.

    if id_len == 8 and is_weekly:
        current_diff = (npc_id // 10000) % 100
        current_floor_num = (npc_id // 1000) % 10
        accessible_npcs = npc_total.filter(id__gte=98000000, id__lt=99000000).order_by(
            "id"
        )
        diff_labels = {
            1: _("월"),
            2: _("화"),
            3: _("수"),
            4: _("목"),
            5: _("금"),
            6: _("토"),
            7: _("일"),
        }
        available_diffs = sorted(
            list(
                set(
                    (id // 10000) % 100
                    for id in accessible_npcs.values_list("id", flat=True)
                )
            )
        )

        for d in available_diffs:
            target_id = (
                (98 * 1000000)
                + (d * 10000)
                + (current_floor_num * 1000)
                + (npc_id % 1000)
            )
            if not npc_total.filter(id=target_id).exists():
                target_id = (
                    accessible_npcs.filter(id__gte=98000000 + d * 10000).first().id
                )
            difficulty_list.append(
                {"value": d, "label": diff_labels.get(d, str(d)), "url_id": target_id}
            )

        floors_in_current_diff = list(
            accessible_npcs.filter(
                id__gte=98000000 + current_diff * 10000,
                id__lt=98000000 + (current_diff + 1) * 10000,
            ).values_list("id", flat=True)
        )

    elif id_len == 4:
        current_diff = (npc_id // 100) % 10
        current_floor_num = npc_id % 100
        accessible_npcs = npc_total.filter(id__gte=9100, id__lt=9600).order_by("id")
        diff_labels = {1: "E", 2: "D", 3: "C", 4: "B", 5: "A"}
        available_diffs = sorted(
            list(
                set(
                    (id // 100) % 10
                    for id in accessible_npcs.values_list("id", flat=True)
                )
            )
        )

        for d in available_diffs:
            target_rank_min = 9000 + (d * 100)
            target_id = target_rank_min + current_floor_num
            if not accessible_npcs.filter(id=target_id).exists():
                last_npc = accessible_npcs.filter(
                    id__gte=target_rank_min, id__lt=target_rank_min + 100
                ).last()
                target_id = last_npc.id if last_npc else target_rank_min + 1
            difficulty_list.append(
                {"value": d, "label": diff_labels.get(d, str(d)), "url_id": target_id}
            )

        floors_in_current_diff = list(
            accessible_npcs.filter(
                id__gte=9000 + (current_diff * 100),
                id__lt=9000 + ((current_diff + 1) * 100),
            ).values_list("id", flat=True)
        )

    else:
        dungeon_prefix = npc_id // 10000
        current_diff = (npc_id // 1000) % 10
        current_floor_num = npc_id % 100
        accessible_npcs = npc_total.filter(
            id__gte=dungeon_prefix * 10000 + 1000, id__lt=dungeon_prefix * 10000 + 4000
        ).order_by("id")
        diff_labels = {1: _("이지"), 2: _("노말"), 3: _("하드")}
        available_diffs = sorted(
            list(
                set(
                    (id // 1000) % 10
                    for id in accessible_npcs.values_list("id", flat=True)
                )
            )
        )

        for d in available_diffs:
            target_id = (dungeon_prefix * 10000) + (d * 1000) + 100 + current_floor_num
            if not npc_total.filter(id=target_id).exists():
                target_id = (
                    accessible_npcs.filter(id__gte=dungeon_prefix * 10000 + d * 1000)
                    .first()
                    .id
                )
            difficulty_list.append(
                {"value": d, "label": diff_labels.get(d, str(d)), "url_id": target_id}
            )

        floors_in_current_diff = list(
            accessible_npcs.filter(
                id__gte=dungeon_prefix * 10000 + current_diff * 1000,
                id__lt=dungeon_prefix * 10000 + (current_diff + 1) * 1000,
            ).values_list("id", flat=True)
        )

    # --- 템플릿용 최종 데이터 가공 ---

    # 1. 난이도 버튼용 이전/다음 계산
    diff_prev_id = -1
    diff_next_id = -1
    for i, item in enumerate(difficulty_list):
        if item["value"] == current_diff:
            if i > 0:
                diff_prev_id = difficulty_list[i - 1]["url_id"]
            if i < len(difficulty_list) - 1:
                diff_next_id = difficulty_list[i + 1]["url_id"]
            break

    # 2. 층수 버튼 및 셀렉터용 데이터 가공 (label을 view에서 생성)
    floor_options = []
    floor_prev_id = -1
    floor_next_id = -1

    for i, f_id in enumerate(floors_in_current_diff):
        is_current = f_id == npc_id
        if is_current:
            if i > 0:
                floor_prev_id = floors_in_current_diff[i - 1]
            if i < len(floors_in_current_diff) - 1:
                floor_next_id = floors_in_current_diff[i + 1]

        f_str = str(f_id)
        if is_weekly:
            # 9801(1)101 -> 5번째 자리
            label = f_str[4]
        else:
            label = str(int(f_str[-2:]))

        floor_options.append({"id": f_id, "label": label, "is_current": is_current})

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
        "difficulty_list": difficulty_list,
        "current_diff": current_diff,
        "floor_options": floor_options,
        "current_floor_id": npc_id,
        "diff_prev_id": diff_prev_id,
        "diff_next_id": diff_next_id,
        "floor_prev_id": floor_prev_id,
        "floor_next_id": floor_next_id,
    }

    context |= statistics

    return render(request, "npc/npc_detail.html", context)
