"""NPC 상세 페이지의 난이도/층 탐색 (npc/catalog.py 조회)"""

from django.utils.translation import gettext_lazy as _

from .catalog import CATALOG

NONE = -1  # 이전/다음이 없음


def build_floor_index(catalog):
    """NPC id -> (던전, 난이도 위치, 층 위치)"""
    index = {}
    for section in catalog:
        for block in section.blocks:
            for dungeon in block.dungeons:
                if dungeon is None:
                    continue
                for d, difficulty in enumerate(dungeon.difficulties):
                    for f, floor in enumerate(difficulty.floors):
                        index[floor.id] = (dungeon, d, f)
    return index


FLOOR_INDEX = build_floor_index(CATALOG)


def _neighbor(items, position, offset):
    target = position + offset
    return items[target] if 0 <= target < len(items) else None


def navigation(npc_id):
    """난이도 선택/이동, 층 선택/이동에 쓰는 값 (카탈로그에 없으면 None)"""
    if npc_id not in FLOOR_INDEX:
        return None
    dungeon, current_d, current_f = FLOOR_INDEX[npc_id]
    difficulties = dungeon.difficulties

    # 난이도 이동: 같은 위치의 층, 없으면 해당 난이도의 첫 층
    difficulty_list = []
    for d, difficulty in enumerate(difficulties):
        floors = difficulty.floors
        target = floors[current_f] if current_f < len(floors) else floors[0]
        difficulty_list.append(
            {"value": d + 1, "label": difficulty.label, "url_id": target.id}
        )

    # 층 번호: 난이도별 1부터, 층이 이어지는 던전(차원의 탑)은 던전 전체에서 이어서
    floors = difficulties[current_d].floors
    first_number = 1
    if dungeon.continuous_floors:
        first_number += sum(
            len(difficulty.floors) for difficulty in difficulties[:current_d]
        )
    floor_options = [
        {"id": floor.id, "label": str(first_number + f), "is_current": f == current_f}
        for f, floor in enumerate(floors)
    ]

    prev_floor = _neighbor(floors, current_f, -1)
    next_floor = _neighbor(floors, current_f, 1)
    if dungeon.continuous_floors:
        if prev_floor is None and current_d > 0:
            prev_floor = difficulties[current_d - 1].floors[-1]
        if next_floor is None and current_d < len(difficulties) - 1:
            next_floor = difficulties[current_d + 1].floors[0]

    prev_difficulty = _neighbor(difficulty_list, current_d, -1)
    next_difficulty = _neighbor(difficulty_list, current_d, 1)

    diff_prev_id = prev_difficulty["url_id"] if prev_difficulty else NONE
    diff_next_id = next_difficulty["url_id"] if next_difficulty else NONE
    floor_prev_id = prev_floor.id if prev_floor else NONE
    floor_next_id = next_floor.id if next_floor else NONE

    # 화면 배치용: [난이도, 층] 각각 이전 버튼 / 선택 / 다음 버튼
    groups = [
        {
            "kind": "difficulty",
            "label": _("난이도"),
            "prev_id": diff_prev_id,
            "next_id": diff_next_id,
            "options": [
                {
                    "id": item["url_id"],
                    "label": item["label"],
                    "selected": d == current_d,
                }
                for d, item in enumerate(difficulty_list)
            ],
        },
        {
            "kind": "floor",
            "label": _("층"),
            "prev_id": floor_prev_id,
            "next_id": floor_next_id,
            "options": [
                {
                    "id": item["id"],
                    "label": item["label"],
                    "selected": item["is_current"],
                }
                for item in floor_options
            ],
        },
    ]

    return {
        "groups": groups,
        "difficulty_list": difficulty_list,
        "current_diff": current_d + 1,
        "floor_options": floor_options,
        "diff_prev_id": diff_prev_id,
        "diff_next_id": diff_next_id,
        "floor_prev_id": floor_prev_id,
        "floor_next_id": floor_next_id,
    }
